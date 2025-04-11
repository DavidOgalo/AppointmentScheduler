from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

class DoctorPatientAssignmentBase(BaseModel):
    doctor_id: UUID
    patient_id: UUID
    is_active: bool = True
    notes: Optional[str] = None

class DoctorPatientAssignmentCreate(DoctorPatientAssignmentBase):
    pass

class DoctorPatientAssignmentUpdate(BaseModel):
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class DoctorPatientAssignmentInDB(DoctorPatientAssignmentBase):
    id: UUID
    assigned_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DoctorPatientAssignmentResponse(DoctorPatientAssignmentInDB):
    pass 