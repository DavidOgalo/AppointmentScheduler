from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models.doctor import Doctor
from app.db.models.user import User
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.services.base import BaseService
import uuid

class DoctorService(BaseService[Doctor, DoctorCreate, DoctorUpdate]):
    def __init__(self, db: Session):
        super().__init__(db, Doctor)

    def _format_doctor(self, doctor: Doctor) -> dict:
        """Format a doctor object for response"""
        return {
            "id": str(doctor.id),
            "first_name": doctor.first_name,
            "last_name": doctor.last_name,
            "specialization": doctor.specialization,
            "email": doctor.email,
            "phone": doctor.phone,
            "license_number": doctor.license_number,
            "is_active": doctor.is_active
        }

    def get(self, id: str) -> Optional[dict]:
        try:
            # If id is already a UUID object, convert it to string
            if hasattr(id, 'hex'):
                doctor_uuid = str(id)
            else:
                doctor_uuid = str(uuid.UUID(id))
            doctor = self.db.query(Doctor).filter(Doctor.id == doctor_uuid).first()
            return self._format_doctor(doctor) if doctor else None
        except ValueError:
            return None

    def get_by_user_id(self, user_id: str) -> Optional[dict]:
        try:
            # If user_id is already a UUID object, convert it to string
            if hasattr(user_id, 'hex'):
                user_uuid = str(user_id)
            else:
                user_uuid = str(uuid.UUID(user_id))
            doctor = self.db.query(Doctor).join(User).filter(User.id == user_uuid).first()
            return self._format_doctor(doctor) if doctor else None
        except ValueError:
            return None

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[dict]:
        doctors = self.db.query(Doctor).offset(skip).limit(limit).all()
        return [self._format_doctor(doctor) for doctor in doctors]

    def create(self, obj_in: DoctorCreate) -> dict:
        db_obj = Doctor(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            specialization=obj_in.specialization,
            email=obj_in.email,
            phone=obj_in.phone,
            license_number=obj_in.license_number,
            is_active=obj_in.is_active
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return self._format_doctor(db_obj)

    def update(self, id: str, obj_in: DoctorUpdate) -> dict:
        try:
            # If id is already a UUID object, convert it to string
            if hasattr(id, 'hex'):
                doctor_uuid = str(id)
            else:
                doctor_uuid = str(uuid.UUID(id))
            db_obj = self.db.query(Doctor).filter(Doctor.id == doctor_uuid).first()
            if db_obj:
                update_data = obj_in.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(db_obj, field, value)
                self.db.commit()
                self.db.refresh(db_obj)
            return self._format_doctor(db_obj) if db_obj else None
        except ValueError:
            return None

    def remove(self, id: str) -> dict:
        try:
            # If id is already a UUID object, convert it to string
            if hasattr(id, 'hex'):
                doctor_uuid = str(id)
            else:
                doctor_uuid = str(uuid.UUID(id))
            obj = self.db.query(Doctor).filter(Doctor.id == doctor_uuid).first()
            if obj:
                self.db.delete(obj)
                self.db.commit()
            return self._format_doctor(obj) if obj else None
        except ValueError:
            return None 