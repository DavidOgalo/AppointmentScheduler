from sqlalchemy import Column, String, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String, nullable=False)
    insurance_info = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship(
        "User",
        back_populates="patient",
        primaryjoin="and_(Patient.id==User.patient_id)",
        uselist=False
    )
    appointments = relationship("Appointment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")

    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>" 