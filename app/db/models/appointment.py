from sqlalchemy import Column, ForeignKey, String, DateTime, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.base_class import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False, default="scheduled")  # scheduled, confirmed, completed, cancelled
    reason = Column(Text, nullable=False)
    notes = Column(Text)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # daily, weekly, monthly
    recurrence_end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    medical_records = relationship("MedicalRecord", back_populates="appointment", cascade="all, delete-orphan")

    __table_args__ = (
        # Ensure end_time is after start_time
        "CHECK (end_time > start_time)",
        # Ensure status is one of the allowed values
        "CHECK (status IN ('scheduled', 'confirmed', 'completed', 'cancelled'))",
    )

    def __repr__(self):
        return f"<Appointment {self.id}: {self.patient_id} with Dr. {self.doctor_id} from {self.start_time} to {self.end_time}>" 