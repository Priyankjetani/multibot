from dotenv import load_dotenv
import os

load_dotenv()

# GCP Settings
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION   = os.getenv("GCP_LOCATION")
GCP_BUCKET     = os.getenv("GCP_BUCKET")

# Auth Settings
SECRET_KEY                = os.getenv("SECRET_KEY", "change-this-in-production")
ALGORITHM                 = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# ChromaDB Settings
CHROMA_DB_PATH = "./chroma_db"

# Bot Settings
MAX_FILES_PER_BOT = 20
MAX_BOTS_PER_USER = 10