from sentence_transformers import SentenceTransformer

from document_loader import all_chunks

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(all_chunks)

print(len(embeddings))

knowledge_base = []

for chunk, embedding in zip(all_chunks, embeddings):

    knowledge_base.append({

        "text": chunk,

        "embedding": embedding

    })

