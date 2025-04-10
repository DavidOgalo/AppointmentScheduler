from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, UUID4

class StaffBase(BaseModel):
    department: str
    position: str
    status: str = "unverified"

class StaffCreate(StaffBase):
    user_id: UUID
    hire_date: datetime = datetime.utcnow()

class StaffUpdate(BaseModel):
    department: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    hire_date: Optional[datetime] = None

class StaffInDB(StaffBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StaffResponse(StaffBase):
    id: UUID
    user_id: UUID
    hire_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        } 