import chromadb
from chromadb.utils import embedding_functions
from core.config import CHROMA_DB_PATH
import uuid

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Use default embedding function
embedding_fn = embedding_functions.DefaultEmbeddingFunction()


def get_or_create_collection(bot_id: str):
    """Gets or creates a ChromaDB collection for a bot"""
    return client.get_or_create_collection(
        name=f"bot_{bot_id}",
        embedding_function=embedding_fn
    )


def add_document_to_bot(bot_id: str, filename: str, text: str):
    """Splits text into chunks and adds to ChromaDB"""
    collection = get_or_create_collection(bot_id)

    # Split text into chunks of 500 characters with 50 overlap
    chunk_size    = 500
    overlap       = 50
    chunks        = []
    start         = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    # Add chunks to ChromaDB
    collection.add(
        documents=chunks,
        ids=[f"{filename}_{i}" for i in range(len(chunks))],
        metadatas=[{"filename": filename, "chunk": i} for i in range(len(chunks))]
    )

    return len(chunks)


def search_documents(bot_id: str, query: str, n_results: int = 5) -> str:
    """Searches ChromaDB for most relevant chunks for a query"""
    collection = get_or_create_collection(bot_id)

    # Check if collection has any documents
    if collection.count() == 0:
        return "No documents found in this bot."

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count())
    )

    # Join the most relevant chunks into one context string
    relevant_chunks = results["documents"][0]
    return "\n\n---\n\n".join(relevant_chunks)


def delete_bot_collection(bot_id: str):
    """Deletes all documents for a bot"""
    try:
        client.delete_collection(f"bot_{bot_id}")
    except Exception:
        pass


def get_bot_file_count(bot_id: str) -> int:
    """Returns number of chunks stored for a bot"""
    try:
        collection = get_or_create_collection(bot_id)
        return collection.count()
    except Exception:
        return 0