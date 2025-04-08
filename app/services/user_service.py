from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.core.security.security import get_password_hash, verify_password
from app.db.models.user import User
from app.schemas.auth import UserCreate, UserUpdate
from app.services.patient_service import PatientService
from app.schemas.patient import PatientCreate

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create(self, obj_in: UserCreate) -> User:
        # Create patient record if role is patient
        patient_id = None
        if obj_in.role == "patient":
            patient_service = PatientService(self.db)
            # Split full_name into first and last name
            name_parts = obj_in.full_name.split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            patient = patient_service.create(
                PatientCreate(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=datetime.now().date(),  # Default to today, should be provided in real app
                    email=obj_in.email,
                    phone="",  # Should be provided in real app
                    address="",  # Should be provided in real app
                )
            )
            patient_id = patient.id

        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            full_name=obj_in.full_name,
            password_hash=get_password_hash(obj_in.password),
            role=obj_in.role,
            patient_id=patient_id,
            is_active=True
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: UUID, obj_in: UserUpdate) -> Optional[User]:
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update_last_login(self, id: UUID) -> None:
        user = self.get(id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.add(user)
            self.db.commit() 