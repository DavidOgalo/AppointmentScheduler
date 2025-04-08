from sqlalchemy import Column, String, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base_class import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    phone_number = Column(String(20), nullable=False)
    address = Column(String(200))
    emergency_contact = Column(String(100))
    emergency_phone = Column(String(20))
    medical_history = Column(String(500))
    insurance_info = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")

    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>" 