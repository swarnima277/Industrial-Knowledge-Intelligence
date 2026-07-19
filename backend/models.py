from pydantic import BaseModel

class EquipmentData(BaseModel):
    equipment_id: str
    equipment_name: str
    status: str
    engineer: str
    manual: str