from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(UUID, primary_key=True, default=uuid4)
    patient_id = Column(UUID, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(UUID, ForeignKey("appointments.id", ondelete="SET NULL"))
    doctor_id = Column(UUID, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    diagnosis = Column(Text)
    prescription = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    appointment = relationship("Appointment", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")

    def __repr__(self):
        return f"<MedicalRecord {self.id}: Patient {self.patient_id}, Doctor {self.doctor_id}>" 