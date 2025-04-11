from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID
import uuid

class AppointmentBase(BaseModel):
    doctor_id: UUID
    patient_id: UUID
    appointment_date: date
    start_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    end_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    reason: str
    notes: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[date] = None

    @validator('recurrence_pattern')
    def validate_recurrence_pattern(cls, v):
        if v is not None and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('Recurrence pattern must be daily, weekly, or monthly')
        return v

    @validator('recurrence_end_date')
    def validate_recurrence_end_date(cls, v, values):
        if values.get('is_recurring') and not v:
            raise ValueError('Recurrence end date is required for recurring appointments')
        return v

class AppointmentCreate(BaseModel):
    doctor_id: str = Field(..., description="ID of the doctor (UUID format)")
    patient_id: str = Field(..., description="ID of the patient (UUID format)")
    start_time: str = Field(..., description="Start time: either time only (HH:MM) or full datetime (YYYY-MM-DDTHH:MM:SS)")
    end_time: str = Field(..., description="End time: either time only (HH:MM) or full datetime (YYYY-MM-DDTHH:MM:SS)")
    reason: str = Field("General appointment", description="Reason for the appointment")
    notes: Optional[str] = Field(None, description="Additional notes")
    status: Optional[str] = Field("scheduled", description="Appointment status")

    @validator('doctor_id', 'patient_id')
    def validate_uuid(cls, v):
        try:
            uuid.UUID(str(v))
            return v
        except ValueError:
            raise ValueError("Invalid UUID format")

    @validator('start_time', 'end_time')
    def validate_datetime(cls, v):
        if not v:
            raise ValueError("Time cannot be empty")
            
        try:
            # Try parsing as full datetime
            datetime.fromisoformat(v)
            return v
        except ValueError:
            try:
                # Try parsing as time only (HH:MM or HH:MM:SS)
                if len(v.split(':')) >= 2:
                    parts = v.split(':')
                    if len(parts) == 2:
                        v = f"{v}:00"  # Add seconds if not provided
                    time.fromisoformat(v)
                    return v
                raise ValueError("Invalid time format")
            except ValueError:
                raise ValueError("Invalid time format. Use either time format (HH:MM) or ISO datetime (YYYY-MM-DDTHH:MM:SS)")

    @validator('status')
    def validate_status(cls, v):
        if v not in ['scheduled', 'confirmed', 'completed', 'cancelled']:
            raise ValueError("Status must be 'scheduled', 'confirmed', 'completed', or 'cancelled'")
        return v

class AppointmentUpdate(BaseModel):
    start_time: Optional[str] = Field(None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    end_time: Optional[str] = Field(None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    reason: Optional[str] = Field(None, description="Reason for the appointment")
    notes: Optional[str] = Field(None, description="Additional notes")
    status: Optional[str] = Field(None, description="Appointment status (scheduled, completed, cancelled, no_show)")
    is_recurring: Optional[bool] = Field(None, description="Whether the appointment is recurring")
    recurrence_pattern: Optional[str] = Field(None, description="Pattern of recurrence (daily, weekly, monthly)")
    recurrence_end_date: Optional[str] = Field(None, description="End date for recurring appointments in ISO format")

    @validator('start_time', 'end_time')
    def validate_datetime(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v)
                return v
            except ValueError:
                raise ValueError("Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in ['scheduled', 'completed', 'cancelled', 'no_show']:
            raise ValueError("Status must be 'scheduled', 'completed', 'cancelled', or 'no_show'")
        return v

    @validator('recurrence_pattern')
    def validate_recurrence_pattern(cls, v):
        if v is not None and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError("Recurrence pattern must be 'daily', 'weekly', or 'monthly'")
        return v

    @validator('recurrence_end_date')
    def validate_recurrence_end_date(cls, v, values):
        if v is not None:
            try:
                end_date = datetime.fromisoformat(v)
                start_time = datetime.fromisoformat(values.get('start_time', ''))
                if end_date <= start_time:
                    raise ValueError("Recurrence end date must be after start time")
                return v
            except ValueError:
                raise ValueError("Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        return v

class AppointmentInDB(BaseModel):
    id: UUID
    doctor_id: UUID
    patient_id: UUID
    start_time: datetime
    end_time: datetime
    status: str
    reason: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AppointmentResponse(BaseModel):
    id: str
    doctor_id: str
    patient_id: str
    start_time: str
    end_time: str
    status: str
    reason: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

class AppointmentListResponse(BaseModel):
    items: List[AppointmentResponse]
    total: int
    page: int
    size: int
