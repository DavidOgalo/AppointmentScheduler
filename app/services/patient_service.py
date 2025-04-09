from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.patient import Patient
from app.schemas.patient import PatientCreate

class PatientService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: PatientCreate) -> Patient:
        db_obj = Patient(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            date_of_birth=obj_in.date_of_birth,
            email=obj_in.email,
            phone=obj_in.phone,
            address=obj_in.address,
            insurance_info=obj_in.insurance_info,
            blood_group=obj_in.blood_group,
            allergies=obj_in.allergies,
            medical_history=obj_in.medical_history
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj 