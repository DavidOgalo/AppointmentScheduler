from typing import Optional
from pydantic import BaseModel, Field, validator
from uuid import UUID
from datetime import datetime


class MedicalRecordBase(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    appointment_id: Optional[UUID] = None
    diagnosis: str
    prescription: str
    notes: Optional[str] = None


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordInDB(MedicalRecordBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalRecordResponse(MedicalRecordInDB):
    pass


class MedicalRecordListResponse(BaseModel):
    items: list[MedicalRecordResponse]
    total: int
    page: int
    size: int 