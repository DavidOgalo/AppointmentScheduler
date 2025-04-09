from typing import Optional
from datetime import datetime
from pydantic import BaseModel, UUID4

class DoctorBase(BaseModel):
    specialization: str
    license_number: str
    years_of_experience: Optional[int] = None
    education: Optional[str] = None
    certifications: Optional[str] = None

class DoctorCreate(DoctorBase):
    id: UUID4
    user_id: UUID4

class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    years_of_experience: Optional[int] = None
    education: Optional[str] = None
    certifications: Optional[str] = None

class DoctorInDB(DoctorBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 