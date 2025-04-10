from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.db.models.patient import Patient
from app.db.models.user import User
from app.schemas.patient import PatientCreate, PatientUpdate

class PatientService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: UUID) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.id == id).first()

    def get_by_user_id(self, user_id: str) -> Optional[Patient]:
        return self.db.query(Patient).join(User.patient).filter(User.id == user_id).first()

    def get_all(self) -> List[Patient]:
        return self.db.query(Patient).all()

    def create(self, obj_in: PatientCreate) -> Patient:
        db_obj = Patient(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            date_of_birth=obj_in.date_of_birth,
            email=obj_in.email,
            phone=obj_in.phone,
            address=obj_in.address,
            insurance_info=obj_in.insurance_info
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: UUID, obj_in: PatientUpdate) -> Optional[Patient]:
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: UUID) -> bool:
        db_obj = self.get(id)
        if not db_obj:
            return False
        self.db.delete(db_obj)
        self.db.commit()
        return True 