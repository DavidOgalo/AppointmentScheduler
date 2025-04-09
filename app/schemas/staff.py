from typing import Optional
from datetime import datetime
from pydantic import BaseModel, UUID4

class StaffBase(BaseModel):
    department: str
    position: str
    status: str = "unverified"
    hire_date: datetime

class StaffCreate(StaffBase):
    id: UUID4
    user_id: UUID4

class StaffUpdate(BaseModel):
    department: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None

class StaffInDB(StaffBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 