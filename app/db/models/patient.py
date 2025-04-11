from datetime import datetime, date
from uuid import uuid4

from sqlalchemy import Column, String, Text, DateTime, Date, JSON, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID, primary_key=True, default=uuid4)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    insurance_info = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    user = relationship("User", back_populates="patient", uselist=False)
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    doctor_assignments = relationship("DoctorPatientAssignment", back_populates="patient")

    def __repr__(self):
        return f"<Patient {self.id}: {self.first_name} {self.last_name}>" 