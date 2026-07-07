from pydantic import BaseModel
from typing import List, Optional


# ─── Auth ───────────────────────────────
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


# ─── Bots ───────────────────────────────
class CreateBotRequest(BaseModel):
    name: str
    description: Optional[str] = ""


class BotResponse(BaseModel):
    bot_id: str
    name: str
    description: str
    owner: str
    file_count: int


class BotListResponse(BaseModel):
    bots: List[BotResponse]


# ─── Chat ───────────────────────────────
class ChatRequest(BaseModel):
    bot_id: str
    message: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    bot_id: str
    message: str
    answer: str
    history: List[ChatMessage]


# ─── Upload ─────────────────────────────
class UploadResponse(BaseModel):
    message: str
    filename: str
    bot_id: str
    uploaded_by: str
    characters_extracted: int