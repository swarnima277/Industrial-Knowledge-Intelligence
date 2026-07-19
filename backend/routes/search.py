from fastapi import APIRouter
from pydantic import BaseModel

from vector_db.chroma_manager import ChromaManager
from graph.graph_manager import GraphManager

router = APIRouter()

chroma = ChromaManager()
graph = GraphManager()


class SearchRequest(BaseModel):
    query: str
    equipment_id: str


@router.post("/search")
def search_manual(data: SearchRequest):

    # Search manual from ChromaDB
    manual_result = chroma.search_manual(data.query)

    # Search equipment from Neo4j
    equipment_result = graph.get_equipment(data.equipment_id)

    # Get only the first manual text
    manual_text = ""

    if manual_result["documents"]:
        manual_text = manual_result["documents"][0][0]

    return {
        "equipment": equipment_result,
        "manual": manual_text
    }