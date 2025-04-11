from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Boolean, Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class DoctorPatientAssignment(Base):
    __tablename__ = "doctor_patient_assignments"

    id = Column(UUID, primary_key=True, default=uuid4)
    doctor_id = Column(UUID, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(UUID, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    assigned_date = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    is_active = Column(Boolean, nullable=False, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    doctor = relationship("Doctor", back_populates="patient_assignments")
    patient = relationship("Patient", back_populates="doctor_assignments")

    def __repr__(self):
        return f"<DoctorPatientAssignment {self.id}: Dr. {self.doctor_id} -> Patient {self.patient_id}>" 