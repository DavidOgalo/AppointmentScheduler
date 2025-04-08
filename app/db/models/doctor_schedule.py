from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base_class import Base

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doctor = relationship("Doctor", back_populates="schedules")

    def __repr__(self):
        return f"<DoctorSchedule {self.doctor_id} - Day {self.day_of_week}>" 