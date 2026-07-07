from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from google.cloud import storage
from models.schemas import ChatRequest, ChatResponse, ChatMessage, UploadResponse
from services.auth_service import get_current_user
from services.pdf_service import extract_text_from_pdf
from services.vector_service import add_document_to_bot
from services.chat_service import chat_with_bot, get_history, clear_history
from core.config import GCP_BUCKET, MAX_FILES_PER_BOT
from routers.bots import bots_db

router = APIRouter(tags=["Chat"])

# Track files per bot: {bot_id: [filename1, filename2...]}
bot_files = {}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    bot_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    # Validate bot exists and belongs to user
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bots_db[bot_id]["owner"] != current_user:
        raise HTTPException(status_code=403, detail="You don't own this bot")

    # Check max files per bot
    files = bot_files.get(bot_id, [])
    if len(files) >= MAX_FILES_PER_BOT:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_FILES_PER_BOT} files allowed per bot"
        )

    # Check duplicate file
    if file.filename in files:
        raise HTTPException(
            status_code=400,
            detail=f"File '{file.filename}' already uploaded to this bot"
        )

    # Read and extract text
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from this PDF. Try a different file."
        )

    # Add to ChromaDB vector store
    chunk_count = add_document_to_bot(bot_id, file.filename, text)

    # Track file
    if bot_id not in bot_files:
        bot_files[bot_id] = []
    bot_files[bot_id].append(file.filename)

    # Backup to GCP Cloud Storage
    try:
        client = storage.Client()
        bucket = client.bucket(GCP_BUCKET)
        blob = bucket.blob(f"multibot/{current_user}/{bot_id}/{file.filename}")
        blob.upload_from_string(file_bytes, content_type="application/pdf")
    except Exception:
        pass  # Don't fail if GCP backup fails

    return UploadResponse(
        message=f"File uploaded and indexed into {chunk_count} chunks",
        filename=file.filename,
        bot_id=bot_id,
        uploaded_by=current_user,
        characters_extracted=len(text)
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: str = Depends(get_current_user)
):
    # Validate bot
    if request.bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bots_db[request.bot_id]["owner"] != current_user:
        raise HTTPException(status_code=403, detail="You don't own this bot")

    # Check bot has files
    if not bot_files.get(request.bot_id):
        raise HTTPException(
            status_code=400,
            detail="Upload at least one file to this bot before chatting"
        )

    # Get answer from Gemini
    answer = chat_with_bot(current_user, request.bot_id, request.message)

    # Get updated history
    history = get_history(current_user, request.bot_id)

    return ChatResponse(
        bot_id=request.bot_id,
        message=request.message,
        answer=answer,
        history=[ChatMessage(**m) for m in history]
    )


@router.get("/chat/{bot_id}/history")
async def get_chat_history(
    bot_id: str,
    current_user: str = Depends(get_current_user)
):
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bots_db[bot_id]["owner"] != current_user:
        raise HTTPException(status_code=403, detail="You don't own this bot")

    history = get_history(current_user, bot_id)
    return {"bot_id": bot_id, "history": history}


@router.delete("/chat/{bot_id}/history")
async def clear_chat_history(
    bot_id: str,
    current_user: str = Depends(get_current_user)
):
    if bot_id not in bots_db:
        raise HTTPException(status_code=404,detail="Bot not found")
    if bots_db[bot_id]["owner"] != current_user:
        raise HTTPException(status_code=403, detail="You don't own this bot")

    clear_history(current_user, bot_id)
    return {"message": "Chat history cleared"}


@router.get("/bots/{bot_id}/files")
async def list_bot_files(
    bot_id: str,
    current_user: str = Depends(get_current_user)
):
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bots_db[bot_id]["owner"] != current_user:
        raise HTTPException(status_code=403, detail="You don't own this bot")

    return {
        "bot_id": bot_id,
        "files": bot_files.get(bot_id, [])
    }