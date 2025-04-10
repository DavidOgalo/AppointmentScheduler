from sqlalchemy import Column, Integer, Time, Boolean, ForeignKey, UniqueConstraint, CheckConstraint, String
from sqlalchemy.orm import relationship
from datetime import time
import uuid
from app.db.base_class import Base

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)

    # Relationship
    doctor = relationship("Doctor", back_populates="schedules")

    # Constraints
    __table_args__ = (
        UniqueConstraint('doctor_id', 'day_of_week', name='uq_doctor_day'),
        CheckConstraint('day_of_week BETWEEN 0 AND 6', name='valid_day_of_week'),
        CheckConstraint('start_time < end_time', name='valid_time_range')
    )

    def __repr__(self):
        return f"<DoctorSchedule(doctor_id={self.doctor_id}, day={self.day_of_week}, time={self.start_time}-{self.end_time})>" 