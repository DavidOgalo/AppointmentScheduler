from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    patient_id = Column(UUID, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(UUID, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)  # scheduled, confirmed, completed, cancelled
    reason = Column(Text, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    medical_records = relationship("MedicalRecord", back_populates="appointment", uselist=False)

    def __repr__(self):
        return f"<Appointment {self.id}>" 