from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from uuid import UUID

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    email: EmailStr
    phone: str
    address: str
    insurance_info: Optional[dict] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    insurance_info: Optional[dict] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None

class PatientInDB(PatientBase):
    id: UUID
    created_at: str
    updated_at: str

    model_config = {
        "from_attributes": True
    } 