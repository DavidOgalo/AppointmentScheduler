from sqlalchemy import Column, Integer, Time, Boolean, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    doctor_id = Column(UUID, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
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
        return f"<DoctorSchedule {self.doctor_id} - Day {self.day_of_week}>" 