from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import uuid

class AppointmentBase(BaseModel):
    start_time: datetime
    end_time: datetime
    reason: str
    notes: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly
    recurrence_end_date: Optional[datetime] = None

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

    @validator('recurrence_pattern')
    def validate_recurrence_pattern(cls, v, values):
        if values.get('is_recurring') and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('recurrence_pattern must be one of: daily, weekly, monthly')
        return v

    @validator('recurrence_end_date')
    def validate_recurrence_end_date(cls, v, values):
        if values.get('is_recurring') and not v:
            raise ValueError('recurrence_end_date is required for recurring appointments')
        if v and 'start_time' in values and v <= values['start_time']:
            raise ValueError('recurrence_end_date must be after start_time')
        return v

class AppointmentCreate(AppointmentBase):
    patient_id: str
    doctor_id: str

    @validator('patient_id', 'doctor_id')
    def validate_uuids(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('Invalid UUID format')

class AppointmentUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None

    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['scheduled', 'confirmed', 'completed', 'cancelled']:
            raise ValueError('status must be one of: scheduled, confirmed, completed, cancelled')
        return v

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class AppointmentInDB(AppointmentBase):
    id: str
    patient_id: str
    doctor_id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v)
        }

class AppointmentResponse(AppointmentInDB):
    pass

class AppointmentListResponse(BaseModel):
    items: List[AppointmentResponse]
    total: int
    page: int
    size: int
