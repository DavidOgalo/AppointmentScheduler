from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.core.security import get_password_hash, verify_password
from app.db.models.user import User
from app.db.models.patient import Patient
from app.db.models.doctor import Doctor
from app.db.models.staff import Staff
from app.schemas.auth import UserCreate, UserUpdate
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
        # Create role-specific profile first
        if obj_in.role == "patient":
            patient = Patient(
                first_name=obj_in.full_name.split()[0],
                last_name=" ".join(obj_in.full_name.split()[1:]) if len(obj_in.full_name.split()) > 1 else "",
                date_of_birth=datetime.now().date(),
                email=obj_in.email,
                phone="",
                address="",
                insurance_info={}
            )
            self.db.add(patient)
            self.db.flush()  # Get the patient ID without committing
            
            # Create user with patient_id
            db_obj = User(
                username=obj_in.username,
                email=obj_in.email,
                full_name=obj_in.full_name,
                password_hash=get_password_hash(obj_in.password),
                role=obj_in.role,
                is_active=True,
                patient_id=patient.id
            )
            
        elif obj_in.role == "doctor":
            doctor = Doctor(
                first_name=obj_in.full_name.split()[0],
                last_name=" ".join(obj_in.full_name.split()[1:]) if len(obj_in.full_name.split()) > 1 else "",
                specialization="General",
                email=obj_in.email,
                phone="",
                license_number="TBD"
            )
            self.db.add(doctor)
            self.db.flush()  # Get the doctor ID without committing
            
            # Create user with doctor_id
            db_obj = User(
                username=obj_in.username,
                email=obj_in.email,
                full_name=obj_in.full_name,
                password_hash=get_password_hash(obj_in.password),
                role=obj_in.role,
                is_active=True,
                doctor_id=doctor.id
            )
            
        elif obj_in.role == "staff":
            # Create user first for staff
            db_obj = User(
                username=obj_in.username,
                email=obj_in.email,
                full_name=obj_in.full_name,
                password_hash=get_password_hash(obj_in.password),
                role=obj_in.role,
                is_active=True
            )
            self.db.add(db_obj)
            self.db.flush()  # Get the user ID without committing
            
            # Create staff profile
            staff = Staff(
                user_id=db_obj.id,
                department="General",
                position="Staff",
                status="unverified"
            )
            self.db.add(staff)
            
        else:
            raise ValueError(f"Invalid role: {obj_in.role}")

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