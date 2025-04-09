from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    patient_id = Column(UUID, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(UUID, ForeignKey("appointments.id", ondelete="SET NULL"))
    diagnosis = Column(Text)
    prescription = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    appointment = relationship("Appointment", back_populates="medical_records")

    def __repr__(self):
        return f"<MedicalRecord {self.id}>" 