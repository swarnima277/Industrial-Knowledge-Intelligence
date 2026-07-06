from sentence_transformers import SentenceTransformer

# Load the embedding model only once
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text):
    embedding = model.encode(text)

    return embedding