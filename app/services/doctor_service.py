from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate

class DoctorService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: str) -> Optional[Doctor]:
        return self.db.query(Doctor).filter(Doctor.id == id).first()

    def get_by_user_id(self, user_id: str) -> Optional[Doctor]:
        return self.db.query(Doctor).filter(Doctor.user_id == user_id).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Doctor]:
        return self.db.query(Doctor).offset(skip).limit(limit).all()

    def create(self, obj_in: DoctorCreate) -> Doctor:
        db_obj = Doctor(
            id=obj_in.id,
            user_id=obj_in.user_id,
            specialization=obj_in.specialization,
            license_number=obj_in.license_number,
            years_of_experience=obj_in.years_of_experience,
            education=obj_in.education,
            certifications=obj_in.certifications
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: Doctor, obj_in: DoctorUpdate) -> Doctor:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, id: str) -> Doctor:
        obj = self.db.query(Doctor).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj 