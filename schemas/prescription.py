from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class PrescriptionBase(BaseModel):
    medication_name: str | None = None
    pzn: str | None = None
    fhir_data: Dict[str, Any | None] | None = None


class PrescriptionCreate(PrescriptionBase):
    order_id: int
    medication_id: int | None = None


class PrescriptionUpdate(PrescriptionBase):
    pass


class PrescriptionInDBBase(PrescriptionBase):
    id: int
    order_id: int
    medication_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Prescription(PrescriptionInDBBase):
    pass
