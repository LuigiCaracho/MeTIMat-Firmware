from typing import Optional

from pydantic import BaseModel


# Medication Schemas
class MedicationBase(BaseModel):
    name: str
    pzn: str
    description: str | None = None
    dosage_form: str | None = None
    manufacturer: str | None = None
    package_size: str | None = None
    price: float | None = 0.0
    is_active: bool | None = True


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(MedicationBase):
    name: str | None = None
    pzn: str | None = None
    price: float | None = None


class MedicationInDBBase(MedicationBase):
    id: int

    class Config:
        from_attributes = True


class Medication(MedicationInDBBase):
    pass
