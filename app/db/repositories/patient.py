from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.db.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate

class PatientRepository(BaseRepository[Patient, PatientCreate, PatientUpdate]):
    def __init__(self):
        super().__init__(Patient)

    def get_by_user_id(self, db: Session, user_id: str) -> Optional[Patient]:
        return db.query(Patient).filter(Patient.user_id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Patient]:
        return db.query(Patient).join(Patient.user).filter(Patient.user.email == email).first()

    def get_active_patients(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Patient]:
        return (
            db.query(Patient)
            .filter(Patient.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_patients(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Patient]:
        return (
            db.query(Patient)
            .filter(
                (Patient.first_name.ilike(f"%{query}%")) |
                (Patient.last_name.ilike(f"%{query}%")) |
                (Patient.phone_number.ilike(f"%{query}%"))
            )
            .offset(skip)
            .limit(limit)
            .all()
        ) 