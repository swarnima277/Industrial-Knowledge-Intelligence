import chromadb
import uuid

client = chromadb.PersistentClient(path="./chroma_store")

collection = client.get_or_create_collection(
    name="industrial_manual"
)



def add_chunks(chunks, embeddings, metadatas):

    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )


def search(query_embedding, n_results=3):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


def reset_collection():
    global collection

    client.delete_collection("industrial_manual")

    collection = client.get_or_create_collection(
        name="industrial_manual"
    )

