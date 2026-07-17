from fastapi import APIRouter

from app.schemas.chat import ChatRequest

from app.services.llm import get_ai_response
from app.services.embeddings import get_embedding
from app.services.chroma_db import search

router = APIRouter()

@router.post("/chat")
def chat(request: ChatRequest):

    # Step 1: Convert the question into an embedding
    question_embedding = get_embedding(request.message).tolist()

    # Step 2: Search ChromaDB
    results = search(question_embedding)

    print("Documents:")
    print(results["documents"])

    print("Metadata:")
    print(results["metadatas"])
    metadata = None

    for item in results["metadatas"][0]:
        if item is not None:
            metadata = item
            break
    


    # Step 3: Build the context from the retrieved chunks
    context = "\n\n".join(results["documents"][0])

    # Step 4: Ask Gemini using the retrieved context
    response = get_ai_response(
        request.message,
        context
    )

    return {
        "user_message": request.message,
        "retrieved_context": context,
        "ai_response": response,
        "source": metadata
    }

    