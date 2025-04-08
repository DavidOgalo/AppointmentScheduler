from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.repositories.base import BaseRepository
from app.db.models.doctor_schedule import DoctorSchedule
from app.schemas.doctor_schedule import DoctorScheduleCreate, DoctorScheduleUpdate

class DoctorScheduleRepository(BaseRepository[DoctorSchedule, DoctorScheduleCreate, DoctorScheduleUpdate]):
    def __init__(self):
        super().__init__(DoctorSchedule)

    def get_by_doctor(
        self, db: Session, doctor_id: str, *, skip: int = 0, limit: int = 100
    ) -> List[DoctorSchedule]:
        return (
            db.query(DoctorSchedule)
            .filter(DoctorSchedule.doctor_id == doctor_id)
            .order_by(DoctorSchedule.day_of_week.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_doctor_availability(
        self, db: Session, doctor_id: str, date: datetime
    ) -> List[DoctorSchedule]:
        day_of_week = date.weekday()
        return (
            db.query(DoctorSchedule)
            .filter(
                and_(
                    DoctorSchedule.doctor_id == doctor_id,
                    DoctorSchedule.day_of_week == day_of_week,
                    DoctorSchedule.is_available == True
                )
            )
            .all()
        )

    def get_available_slots(
        self,
        db: Session,
        doctor_id: str,
        date: datetime,
        duration_minutes: int
    ) -> List[datetime]:
        schedules = self.get_doctor_availability(db, doctor_id, date)
        if not schedules:
            return []

        available_slots = []
        for schedule in schedules:
            current_time = schedule.start_time
            while current_time + timedelta(minutes=duration_minutes) <= schedule.end_time:
                available_slots.append(current_time)
                current_time += timedelta(minutes=30)  # Default slot duration

        return available_slots

    def update_availability(
        self, db: Session, schedule_id: str, is_available: bool
    ) -> Optional[DoctorSchedule]:
        schedule = self.get(db, id=schedule_id)
        if schedule:
            schedule.is_available = is_available
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
            return schedule
        return None 