from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import date, datetime
from uuid import UUID

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    phone: str
    address: str
    insurance_info: Optional[Dict] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    insurance_info: Optional[Dict] = None
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

class PatientResponse(PatientBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        } 