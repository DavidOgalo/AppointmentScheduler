from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models.doctor_schedule import DoctorSchedule
from app.schemas.doctor_schedule import DoctorScheduleCreate, DoctorScheduleUpdate
import uuid
from datetime import time

class DoctorScheduleService:
    def __init__(self, db: Session):
        self.db = db

    def _format_schedule(self, schedule: DoctorSchedule) -> dict:
        """Format a schedule object for response"""
        return {
            "id": str(schedule.id),
            "doctor_id": str(schedule.doctor_id),
            "day_of_week": schedule.day_of_week,
            "start_time": schedule.start_time.strftime("%H:%M:%S"),
            "end_time": schedule.end_time.strftime("%H:%M:%S"),
            "is_available": schedule.is_available
        }

    def create(self, doctor_id: str, obj_in: DoctorScheduleCreate) -> dict:
        try:
            # Convert doctor_id to string UUID
            doctor_uuid = str(uuid.UUID(doctor_id))
            
            # Convert time strings to time objects
            start_time = time.fromisoformat(obj_in.start_time)
            end_time = time.fromisoformat(obj_in.end_time)
            
            # Check for existing schedule on the same day
            existing = self.db.query(DoctorSchedule).filter(
                DoctorSchedule.doctor_id == doctor_uuid,
                DoctorSchedule.day_of_week == obj_in.day_of_week
            ).first()
            
            if existing:
                raise ValueError(f"Schedule already exists for day {obj_in.day_of_week}")
            
            db_obj = DoctorSchedule(
                doctor_id=doctor_uuid,
                day_of_week=obj_in.day_of_week,
                start_time=start_time,
                end_time=end_time,
                is_available=obj_in.is_available
            )
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return self._format_schedule(db_obj)
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error creating schedule: {str(e)}")

    def get(self, id: str) -> Optional[dict]:
        try:
            schedule_uuid = str(uuid.UUID(id))
            schedule = self.db.query(DoctorSchedule).filter(DoctorSchedule.id == schedule_uuid).first()
            return self._format_schedule(schedule) if schedule else None
        except ValueError:
            raise ValueError("Invalid schedule ID format")

    def get_by_doctor(self, doctor_id: str) -> List[dict]:
        try:
            # If doctor_id is already a UUID object, convert it to string
            if hasattr(doctor_id, 'hex'):
                doctor_uuid = str(doctor_id)
            else:
                doctor_uuid = str(uuid.UUID(doctor_id))
            
            schedules = self.db.query(DoctorSchedule).filter(
                DoctorSchedule.doctor_id == doctor_uuid
            ).all()
            return [self._format_schedule(schedule) for schedule in schedules]
        except ValueError:
            raise ValueError("Invalid doctor ID format")

    def update(self, id: str, obj_in: DoctorScheduleUpdate) -> dict:
        try:
            schedule_uuid = str(uuid.UUID(id))
            db_obj = self.db.query(DoctorSchedule).filter(DoctorSchedule.id == schedule_uuid).first()
            if not db_obj:
                raise ValueError("Schedule not found")
            
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field in ['start_time', 'end_time'] and value is not None:
                    value = time.fromisoformat(value)
                setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            return self._format_schedule(db_obj)
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error updating schedule: {str(e)}")

    def delete(self, id: str) -> bool:
        try:
            schedule_uuid = str(uuid.UUID(id))
            db_obj = self.db.query(DoctorSchedule).filter(DoctorSchedule.id == schedule_uuid).first()
            if not db_obj:
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error deleting schedule: {str(e)}")

    def check_availability(self, doctor_id: str, day_of_week: int, time_str: str) -> bool:
        """Check if a doctor is available at a specific time on a specific day"""
        try:
            # If doctor_id is already a UUID object, convert it to string
            if hasattr(doctor_id, 'hex'):
                doctor_uuid = str(doctor_id)
            else:
                doctor_uuid = str(uuid.UUID(doctor_id))
                
            check_time = time.fromisoformat(time_str)
            schedule = self.db.query(DoctorSchedule).filter(
                DoctorSchedule.doctor_id == doctor_uuid,
                DoctorSchedule.day_of_week == day_of_week,
                DoctorSchedule.is_available == True
            ).first()
            
            if not schedule:
                return False
            
            return schedule.start_time <= check_time <= schedule.end_time
        except ValueError:
            raise ValueError("Invalid doctor ID or time format") 