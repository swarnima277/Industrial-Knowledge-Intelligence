from fastapi import APIRouter, UploadFile, File
import shutil
import os


from app.services.pdf_loader import read_pdf
from app.services.text_splitter import split_text
from app.services.embeddings import get_embedding
from app.services.chroma_db import add_chunks

router = APIRouter()

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = read_pdf(file_path)

    chunks = []
    metadatas = []

    for page in pages:

        page_chunks = split_text(page["text"])

        for chunk in page_chunks:

            chunks.append(chunk)

            metadatas.append(
                {
                    "source": file.filename,
                    "page": page["page"]
                }
            )

    embeddings = [
        get_embedding(chunk).tolist()
        for chunk in chunks
    ]

    metadatas = []

    for chunk in chunks:
        metadatas.append(
            {
             "source": file.filename
           }
    )

    add_chunks(chunks, embeddings, metadatas)

    return {
        "message": "Document added successfully",
        "chunks_added": len(chunks)

    }