from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from routers import auth, bots, chat

app = FastAPI(
    title="MultiBot API",
    description="AI-powered multi-collection chatbot with document upload and chat history",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(bots.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")