import chromadb
from sentence_transformers import SentenceTransformer


class ChromaManager:

    def __init__(self):

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="equipment_manuals"
        )

    # ----------------------------
    # Store Manual
    # ----------------------------
    def store_manual(self, equipment_id, manual):

        embedding = self.model.encode(manual).tolist()

        self.collection.upsert(
            ids=[equipment_id],
            documents=[manual],
            embeddings=[embedding]
        )

        print("Manual Stored Successfully")

    # ----------------------------
    # Search Manual
    # ----------------------------
    def search_manual(self, query):

        embedding = self.model.encode(query).tolist()

        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=2
        )

        return result