import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph.graph_manager import GraphManager

from graph.graph_manager import GraphManager
import chromadb
from sentence_transformers import SentenceTransformer

graph = GraphManager()

graph.create_equipment(
    "P600",
    "Cooling Pump",
    "Running"
)

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="equipment_manuals"
)

manual = """
Cooling Pump Manual

If vibration occurs,
check lubrication,
bearing wear
and shaft alignment.
"""

embedding = model.encode(manual).tolist()

collection.add(
    documents=[manual],
    embeddings=[embedding],
    ids=["manual_P600"]
)

print("Knowledge Graph + Vector DB Linked Successfully!")

graph.close()