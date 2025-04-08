from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False)  # admin, doctor, staff, patient
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="user", uselist=False)
    doctor = relationship("Doctor", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>" 