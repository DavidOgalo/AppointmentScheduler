from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base_class import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    office_address = Column(String(200))
    bio = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    schedules = relationship("DoctorSchedule", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor {self.first_name} {self.last_name} ({self.specialization})>" 