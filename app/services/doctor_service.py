from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate

class DoctorService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: DoctorCreate) -> Doctor:
        db_obj = Doctor(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            specialization=obj_in.specialization,
            email=obj_in.email,
            phone=obj_in.phone,
            license_number=obj_in.license_number,
            is_active=True
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj 