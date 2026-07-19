from backend.routes.upload import router as upload_router
from backend.routes.search import router as search_router
from fastapi import FastAPI
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph.graph_manager import GraphManager

app = FastAPI()
app.include_router(upload_router)
app.include_router(search_router)

graph = GraphManager()


@app.get("/")
def home():
    return {
        "message": "ET Hackathon Backend Running"
    }


@app.get("/equipment/{equipment_id}")
def get_equipment(equipment_id: str):

    result = graph.get_equipment(equipment_id)

    if result:
        return result

    return {
        "error": "Equipment not found"
    }