# 🤖 MultiBot — Production RAG Chatbot Platform

An AI-powered multi-collection chatbot platform where users create separate bots for different purposes, upload documents, and chat with them using real **Retrieval Augmented Generation (RAG)**.

---

## ✨ Features

- 🔐 User registration and login with JWT authentication and bcrypt password hashing
- 🤖 Create multiple named bots — each bot has its own isolated knowledge base
- 📄 Upload multiple PDFs to each bot (up to 20 files per bot)
- 🧠 Real RAG pipeline — documents are chunked, embedded, and stored in ChromaDB
- 🔍 Semantic similarity search — only the most relevant chunks are sent to Gemini
- 💬 Full conversation memory — each bot remembers your chat history
- ☁️ Documents backed up to Google Cloud Storage
- 🐳 Fully containerized with Docker
- ☸️ Kubernetes deployment with secrets management and load balancing

---

## 🏗️ Real RAG Pipeline

This is a production-grade RAG pipeline — not simple document stuffing:

```
PDF Upload
    ↓
Text Extraction (PyPDF2)
    ↓
Chunking (500 chars with 50 char overlap)
    ↓
Embeddings (ChromaDB default embeddings)
    ↓
Vector Storage (ChromaDB persistent store)
    ↓
                    ← User asks question
                    ↓
            Similarity Search (ChromaDB)
                    ↓
            Top 5 relevant chunks retrieved
                    ↓
            Prompt = chunks + chat history + question
                    ↓
            Gemini 2.5 Flash generates answer
                    ↓
            Answer + updated history returned
```

This approach means:
- Works on **large documents** — no token limit issues
- **Accurate answers** — only relevant chunks sent to Gemini
- **Fast responses** — no need to process entire document each time
- **Memory efficient** — vector search scales to thousands of documents

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| API Framework | FastAPI |
| AI Model | Gemini 2.5 Flash (Vertex AI) |
| Vector Database | ChromaDB (persistent) |
| Cloud Storage | Google Cloud Storage |
| Authentication | JWT (python-jose + passlib bcrypt) |
| PDF Extraction | PyPDF2 |
| Containerization | Docker + Docker Compose |
| Orchestration | Kubernetes (Minikube locally, GKE for cloud) |

---

## 📁 Project Structure

```
multibot/
│
├── app.py                      # Main entry point
├── routers/
│   ├── auth.py                 # /auth/register, /auth/login
│   ├── bots.py                 # /bots/create, /bots/list, /bots/{id}
│   └── chat.py                 # /upload, /chat, /chat/{id}/history
├── models/
│   └── schemas.py              # Pydantic request/response models
├── services/
│   ├── auth_service.py         # Password hashing, JWT logic
│   ├── pdf_service.py          # PDF text extraction
│   ├── vector_service.py       # ChromaDB — chunk, embed, search
│   └── chat_service.py         # Gemini AI + chat history management
├── core/
│   ├── config.py               # Environment settings
│   └── state.py                # Shared in-memory storage
├── docker/
│   ├── Dockerfile              # Container build instructions
│   └── docker-compose.yml      # Local Docker setup
├── kubernetes/
│   ├── deployment.yaml         # K8s deployment (2 replicas)
│   ├── service.yaml            # K8s service (NodePort)
│   └── configmap.yaml          # Environment variables
├── run.sh                      # One command runner script
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- GCP account with Vertex AI and Cloud Storage APIs enabled
- Docker Desktop
- Minikube + kubectl (for Kubernetes)

### 1. Clone the repo
```bash
git clone https://github.com/Priyankjetani/multibot.git
cd multibot
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment
Create a `.env` file:
```
GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GCP_BUCKET=your-bucket-name
SECRET_KEY=your-secret-key
```

### 4. Run locally
```bash
uvicorn app:app --reload
# Visit http://127.0.0.1:8000/docs
```

---

## 🐳 Docker

```bash
# Build and start
./run.sh

# Stop
./run.sh stop

# Rebuild after code changes
./run.sh rebuild

# View logs
./run.sh logs
```

---

## ☸️ Kubernetes

```bash
# Start minikube
minikube start --driver=docker

# Create GCP key secret
kubectl create secret generic gcp-key-secret \
  --from-file=gcp-key.json=./gcp-key.json

# Deploy
./run.sh k8s-deploy

# Open in browser
./run.sh k8s-open

# Check status
./run.sh k8s-status

# View logs
./run.sh k8s-logs

# Stop
./run.sh k8s-stop
```

---

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Login, get JWT token |
| POST | `/bots/create` | Yes | Create a new bot |
| GET | `/bots/list` | Yes | List your bots |
| GET | `/bots/{bot_id}` | Yes | Get bot details |
| DELETE | `/bots/{bot_id}` | Yes | Delete a bot |
| POST | `/upload` | Yes | Upload PDF to a bot |
| POST | `/chat` | Yes | Chat with a bot |
| GET | `/chat/{bot_id}/history` | Yes | Get conversation history |
| DELETE | `/chat/{bot_id}/history` | Yes | Clear conversation history |
| GET | `/bots/{bot_id}/files` | Yes | List files in a bot |
| GET | `/docs` | No | Interactive API documentation |

---

## 💡 How it works

### 1. Create a bot
```json
POST /bots/create
{
  "name": "HR Bot",
  "description": "Answers questions about HR policies"
}
```

### 2. Upload documents to the bot
```bash
POST /upload
form-data: bot_id=abc123, file=hr_policy.pdf
```
The document is chunked into 500-character pieces, embedded, and stored in ChromaDB.

### 3. Chat with your bot
```json
POST /chat
{
  "bot_id": "abc123",
  "message": "How many days of annual leave do I get?"
}
```
ChromaDB finds the most relevant chunks, Gemini answers using only those chunks.

---

## 🧠 Why ChromaDB + RAG?

| Simple Stuffing (bad) | Real RAG with ChromaDB (good) |
|----------------------|-------------------------------|
| Sends entire document to Gemini | Sends only relevant chunks |
| Fails on large documents | Works on any size document |
| Expensive — wastes tokens | Efficient — minimal tokens |
| Slow on big files | Fast — vector search is instant |
| Not production ready | Production ready ✅ |

---

## 👤 Author

**Priyank Jetani**
- LinkedIn: [priyank-jetani](https://www.linkedin.com/in/priyank-jetani)
- GitHub: [Priyankjetani](https://github.com/Priyankjetani)
