from datetime import time
from typing import Optional
from pydantic import BaseModel, Field, validator
import re
import uuid

class DoctorScheduleBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: str = Field(..., description="Time in HH:MM:SS format")
    end_time: str = Field(..., description="Time in HH:MM:SS format")
    is_available: bool = True

    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        if not re.match(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$', v):
            raise ValueError('Time must be in HH:MM:SS format')
        return v

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values:
            start = time.fromisoformat(values['start_time'])
            end = time.fromisoformat(v)
            if end <= start:
                raise ValueError('end_time must be after start_time')
        return v

class DoctorScheduleCreate(DoctorScheduleBase):
    pass

class DoctorScheduleUpdate(DoctorScheduleBase):
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_available: Optional[bool] = None

class DoctorScheduleInDB(DoctorScheduleBase):
    id: str
    doctor_id: str

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v)
        }

class DoctorScheduleResponse(DoctorScheduleInDB):
    pass 