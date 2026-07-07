# Shared in-memory state across all routers

# User store: {username: hashed_password}
users_db = {}

# Chat history per user per bot:
# {username: {bot_id: [{role: "user/assistant", content: "..."}]}}
chat_history = {}