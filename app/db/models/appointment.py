from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base_class import Base

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=30)
    status = Column(Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED)
    reason = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

    __table_args__ = (
        # Ensure appointment duration is between 15 and 120 minutes
        CheckConstraint('duration_minutes >= 15 AND duration_minutes <= 120', 
                       name='check_duration_minutes'),
        # Ensure appointment date is in the future
        CheckConstraint('appointment_date > created_at', 
                       name='check_appointment_date'),
    )

    def __repr__(self):
        return f"<Appointment {self.id} - {self.patient_id} with {self.doctor_id}>" 