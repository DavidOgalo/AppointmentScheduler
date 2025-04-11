from datetime import time
from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Integer, Boolean, Time, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(UUID, primary_key=True, default=uuid4)
    doctor_id = Column(UUID, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)

    # Relationships
    doctor = relationship("Doctor", back_populates="schedules")

    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="valid_day_of_week"),
        CheckConstraint("start_time < end_time", name="valid_time_range"),
        UniqueConstraint("doctor_id", "day_of_week", name="unique_doctor_day")
    )

    def __repr__(self):
        return f"<DoctorSchedule(doctor_id={self.doctor_id}, day={self.day_of_week}, time={self.start_time}-{self.end_time})>" 