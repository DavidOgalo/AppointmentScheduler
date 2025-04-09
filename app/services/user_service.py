from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.core.security.security import get_password_hash, verify_password
from app.db.models.user import User
from app.db.models.staff import Staff
from app.schemas.auth import UserCreate, UserUpdate
from app.services.patient_service import PatientService
from app.services.doctor_service import DoctorService
from app.schemas.patient import PatientCreate
from app.schemas.doctor import DoctorCreate

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
        # Split full name into first and last name
        name_parts = obj_in.full_name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Create user object first
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            full_name=obj_in.full_name,
            password_hash=get_password_hash(obj_in.password),
            role=obj_in.role,
            is_active=True
        )
        self.db.add(db_obj)
        self.db.flush()  # This assigns the ID to db_obj without committing

        # Create role-specific records based on role
        if obj_in.role == "patient":
            patient_service = PatientService(self.db)
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
            db_obj.patient_id = patient.id
        elif obj_in.role == "doctor":
            doctor_service = DoctorService(self.db)
            doctor = doctor_service.create(
                DoctorCreate(
                    first_name=first_name,
                    last_name=last_name,
                    specialization="General",  # Should be provided in real app
                    email=obj_in.email,
                    phone="",  # Should be provided in real app
                    license_number="TBD",  # Should be provided in real app
                )
            )
            db_obj.doctor_id = doctor.id
        elif obj_in.role == "staff":
            staff = Staff(
                user_id=db_obj.id,
                department="General",  # Should be provided in real app
                position="Staff",  # Should be provided in real app
                status="unverified"
            )
            self.db.add(staff)

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