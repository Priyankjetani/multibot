import vertexai
from vertexai.generative_models import GenerativeModel
from core.config import GCP_PROJECT_ID, GCP_LOCATION
from core.state import chat_history
from services.vector_service import search_documents
from typing import List

vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)


def get_history(username: str, bot_id: str) -> List[dict]:
    """Gets chat history for a user+bot combination"""
    return chat_history.get(username, {}).get(bot_id, [])


def save_message(username: str, bot_id: str, role: str, content: str):
    """Saves a message to chat history"""
    if username not in chat_history:
        chat_history[username] = {}
    if bot_id not in chat_history[username]:
        chat_history[username][bot_id] = []
    chat_history[username][bot_id].append({
        "role": role,
        "content": content
    })


def clear_history(username: str, bot_id: str):
    """Clears chat history for a user+bot"""
    if username in chat_history:
        chat_history[username][bot_id] = []


def chat_with_bot(username: str, bot_id: str, message: str) -> str:
    """Main chat function — searches docs and answers with Gemini"""

    # Step 1: Search ChromaDB for relevant document chunks
    context = search_documents(bot_id, message)

    # Step 2: Get chat history for this user+bot
    history = get_history(username, bot_id)

    # Step 3: Format history for the prompt
    history_text = ""
    for msg in history[-6:]:  # last 6 messages only to save tokens
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    # Step 4: Build prompt
    prompt = f"""You are a helpful AI assistant for a specific knowledge base.
Answer questions using ONLY the context below.
If the answer is not in the context, say "I could not find that in the uploaded documents."
Be conversational and remember the chat history.

RELEVANT CONTEXT FROM DOCUMENTS:
{context}

CHAT HISTORY:
{history_text}

USER: {message}
ASSISTANT:"""

    # Step 5: Call Gemini
    model    = GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    answer   = response.text

    # Step 6: Save both messages to history
    save_message(username, bot_id, "user", message)
    save_message(username, bot_id, "assistant", answer)

    return answer