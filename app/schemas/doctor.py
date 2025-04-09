from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    specialization: str
    email: EmailStr
    phone: str
    license_number: str

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(DoctorBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialization: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = None

class DoctorInDB(DoctorBase):
    id: UUID
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {
        "from_attributes": True
    } 