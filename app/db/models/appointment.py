from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String, Text, Boolean, DateTime, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID, primary_key=True, default=uuid4)
    doctor_id = Column(UUID, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(UUID, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False, default="scheduled")
    reason = Column(Text, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    medical_records = relationship("MedicalRecord", back_populates="appointment", cascade="all, delete-orphan")

    # Add check constraints using proper SQLAlchemy syntax
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="check_end_time_after_start_time"),
        CheckConstraint("status IN ('scheduled', 'confirmed', 'completed', 'cancelled')", name="check_valid_status"),
    )

    def __repr__(self):
        return f"<Appointment {self.id}: {self.patient_id} with Dr. {self.doctor_id} from {self.start_time} to {self.end_time}>" 