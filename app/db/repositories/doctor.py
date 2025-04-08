from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.db.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate

class DoctorRepository(BaseRepository[Doctor, DoctorCreate, DoctorUpdate]):
    def __init__(self):
        super().__init__(Doctor)

    def get_by_user_id(self, db: Session, user_id: str) -> Optional[Doctor]:
        return db.query(Doctor).filter(Doctor.user_id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Doctor]:
        return db.query(Doctor).filter(Doctor.email == email).first()

    def get_by_specialization(
        self, db: Session, specialization: str, *, skip: int = 0, limit: int = 100
    ) -> List[Doctor]:
        return (
            db.query(Doctor)
            .filter(Doctor.specialization == specialization)
            .filter(Doctor.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_doctors(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Doctor]:
        return (
            db.query(Doctor)
            .filter(Doctor.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_doctors(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Doctor]:
        return (
            db.query(Doctor)
            .filter(
                (Doctor.first_name.ilike(f"%{query}%")) |
                (Doctor.last_name.ilike(f"%{query}%")) |
                (Doctor.specialization.ilike(f"%{query}%")) |
                (Doctor.email.ilike(f"%{query}%"))
            )
            .offset(skip)
            .limit(limit)
            .all()
        ) 