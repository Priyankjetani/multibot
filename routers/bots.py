from fastapi import APIRouter, HTTPException, Depends
from models.schemas import CreateBotRequest, BotResponse, BotListResponse
from services.auth_service import get_current_user
from services.vector_service import delete_bot_collection, get_bot_file_count
from core.state import chat_history
from core.config import MAX_BOTS_PER_USER
import uuid

router = APIRouter(prefix="/bots", tags=["Bots"])

# In-memory bot store
# {bot_id: {name, description, owner}}
bots_db = {}


@router.post("/create", response_model=BotResponse)
async def create_bot(
    request: CreateBotRequest,
    current_user: str = Depends(get_current_user)
):
    # Check max bots per user
    user_bots = [b for b in bots_db.values() if b["owner"] == current_user]
    if len(user_bots) >= MAX_BOTS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_BOTS_PER_USER} bots allowed per user"
        )

    # Check duplicate name for this user
    for bot in user_bots:
        if bot["name"].lower() == request.name.lower():
            raise HTTPException(
                status_code=400,
                detail=f"You already have a bot named '{request.name}'"
            )

    bot_id = str(uuid.uuid4())[:8]
    bots_db[bot_id] = {
        "name":        request.name,
        "description": request.description or "",
        "owner":       current_user
    }

    return BotResponse(
        bot_id=bot_id,
        name=request.name,
        description=request.description or "",
        owner=current_user,
        file_count=0
    )


@router.get("/list", response_model=BotListResponse)
async def list_bots(current_user: str = Depends(get_current_user)):
    user_bots = []
    for bot_id, bot in bots_db.items():
        if bot["owner"] == current_user:
            user_bots.append(BotResponse(
                bot_id=bot_id,
                name=bot["name"],
                description=bot["description"],
                owner=current_user,
                file_count=get_bot_file_count(bot_id)
            ))
    return BotListResponse(bots=user_bots)


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: str,
    current_user: str = Depends(get_current_user)
):
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")

    bot = bots_db[bot_id]
    if bot["owner"] != current_user:
        raise HTTPException(status_code=403, detail="You don't own this bot")

    return BotResponse(
        bot_id=bot_id,
        name=bot["name"],
        description=bot["description"],
        owner=current_user,
        file_count=get_bot_file_count(bot_id)
    )


@router.delete("/{bot_id}")
async def delete_bot(
    bot_id: str,
    current_user: str = Depends(get_current_user)
):
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")

    if bots_db[bot_id]["owner"] != current_user:
        raise HTTPException(status_code=403, detail="You don't own this bot")

    # Delete from ChromaDB
    delete_bot_collection(bot_id)

    # Clear chat history
    if current_user in chat_history:
        chat_history[current_user].pop(bot_id, None)

    # Delete from bots store
    del bots_db[bot_id]

    return {"message": f"Bot '{bot_id}' deleted successfully"}