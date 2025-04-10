from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, UUID4

class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    specialization: str
    email: str
    phone: str
    license_number: str
    is_active: bool = True
    years_of_experience: Optional[int] = None
    education: Optional[str] = None
    certifications: Optional[str] = None

class DoctorCreate(DoctorBase):
    id: UUID4
    user_id: UUID4

class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialization: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = None
    years_of_experience: Optional[int] = None
    education: Optional[str] = None
    certifications: Optional[str] = None

class DoctorResponse(DoctorBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        }

class DoctorInDB(DoctorBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 