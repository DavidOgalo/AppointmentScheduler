from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class AppointmentBase(BaseModel):
    doctor_id: UUID
    patient_id: UUID
    start_time: datetime
    end_time: datetime
    status: str = Field(..., pattern="^(scheduled|confirmed|completed|cancelled)$")
    reason: str
    notes: str

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(AppointmentBase):
    doctor_id: UUID = None
    patient_id: UUID = None
    start_time: datetime = None
    end_time: datetime = None
    status: str = None
    reason: str = None
    notes: str = None

class AppointmentInDB(AppointmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
