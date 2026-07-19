from fastapi import APIRouter
from pydantic import BaseModel

from graph.graph_manager import GraphManager
from vector_db.chroma_manager import ChromaManager

router = APIRouter()

graph = GraphManager()
chroma = ChromaManager()


class EquipmentRequest(BaseModel):
    equipment_id: str
    equipment_name: str
    status: str
    engineer: str
    manual: str


@router.post("/upload-document")
def upload_document(data: EquipmentRequest):

    # Store Equipment
    graph.create_equipment(
        data.equipment_id,
        data.equipment_name,
        data.status
    )

    # Store Engineer
    graph.create_engineer(
        data.engineer,
        data.engineer
    )

    # Create Relationship
    graph.assign_engineer(
        data.equipment_id,
        data.engineer
    )

    # Store Manual in ChromaDB
    chroma.store_manual(
        data.equipment_id,
        data.manual
    )

    return {
        "message": "Everything stored successfully!"
    }