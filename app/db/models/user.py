from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    
    # Foreign keys as per database schema
    patient_id = Column(UUID, ForeignKey("patients.id", ondelete="SET NULL"))
    doctor_id = Column(UUID, ForeignKey("doctors.id", ondelete="SET NULL"))
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One-to-one relationships
    patient = relationship(
        "Patient",
        foreign_keys=[patient_id],
        back_populates="user",
        uselist=False
    )
    doctor = relationship(
        "Doctor",
        foreign_keys=[doctor_id],
        back_populates="user",
        uselist=False
    )
    staff_profile = relationship(
        "Staff",
        back_populates="user",
        uselist=False
    )

    def __repr__(self):
        return f"<User {self.email}>" 