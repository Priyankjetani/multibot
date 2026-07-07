from fastapi import APIRouter, HTTPException
from models.schemas import RegisterRequest, LoginRequest, LoginResponse
from services.auth_service import hash_password, verify_password, create_access_token
from core.state import users_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register(request: RegisterRequest):
    if request.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    users_db[request.username] = hash_password(request.password)
    return {"message": f"User '{request.username}' registered successfully"}


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    if request.username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(request.password, users_db[request.username]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(request.username)
    return {"access_token": token, "token_type": "bearer"}