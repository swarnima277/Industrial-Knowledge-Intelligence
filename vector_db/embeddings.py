from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

text = "Boiler pump leakage detected"

embedding = model.encode(text)

print("Embedding Length:", len(embedding))
print(embedding[:10])