from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import time
from uuid import UUID, uuid4
from fastapi import HTTPException, status

from app.db.models.doctor_schedule import DoctorSchedule
from app.schemas.doctor_schedule import DoctorScheduleCreate, DoctorScheduleUpdate


class DoctorScheduleService:
    def __init__(self, db: Session):
        self.db = db

    def _format_schedule(self, schedule: DoctorSchedule) -> Dict:
        """Format schedule object for response."""
        return {
            "id": str(schedule.id),
            "doctor_id": str(schedule.doctor_id),
            "day_of_week": schedule.day_of_week,
            "start_time": schedule.start_time.isoformat(),
            "end_time": schedule.end_time.isoformat(),
            "is_available": schedule.is_available
        }

    def create(self, schedule_data: dict) -> dict:
        """Create a new doctor schedule."""
        try:
            # Convert string IDs to UUID objects
            doctor_id = UUID(schedule_data["doctor_id"])
            
            # Convert day_of_week to integer if it's a string
            day_of_week = int(schedule_data["day_of_week"])
            
            # Convert time strings to time objects
            start_time = time.fromisoformat(schedule_data["start_time"])
            end_time = time.fromisoformat(schedule_data["end_time"])
            
            schedule = DoctorSchedule(
                doctor_id=doctor_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                is_available=schedule_data.get("is_available", True)
            )
            
            self.db.add(schedule)
            self.db.commit()
            self.db.refresh(schedule)
            
            return {
                "id": str(schedule.id),
                "doctor_id": str(schedule.doctor_id),
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time.isoformat(),
                "end_time": schedule.end_time.isoformat(),
                "is_available": schedule.is_available
            }
            
        except ValueError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data format: {str(e)}"
            )
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating schedule: {str(e)}"
            )

    def get(self, schedule_id: str) -> Optional[dict]:
        """Get a schedule by ID."""
        try:
            schedule = self.db.query(DoctorSchedule).filter(
                DoctorSchedule.id == UUID(schedule_id)
            ).first()
            
            if not schedule:
                return None
                
            return {
                "id": str(schedule.id),
                "doctor_id": str(schedule.doctor_id),
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time.isoformat(),
                "end_time": schedule.end_time.isoformat(),
                "is_available": schedule.is_available
            }
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid UUID format"
            )

    def get_by_doctor(self, doctor_id: str, day_of_week: int) -> Optional[DoctorSchedule]:
        """Get doctor's schedule for a specific day of the week."""
        try:
            # Convert string to UUID if it's not already a UUID
            if isinstance(doctor_id, str):
                doctor_id = UUID(doctor_id)
                
            print(f"Looking for schedule with doctor_id={doctor_id}, day_of_week={day_of_week}")
            
            schedule = self.db.query(DoctorSchedule).filter(
                DoctorSchedule.doctor_id == doctor_id,
                DoctorSchedule.day_of_week == day_of_week
            ).first()
            
            if schedule:
                print(f"Found schedule: day={schedule.day_of_week}, start={schedule.start_time}, end={schedule.end_time}, available={schedule.is_available}")
            else:
                print(f"No schedule found for doctor {doctor_id} on day {day_of_week}")
                
            return schedule
            
        except ValueError as e:
            print(f"Invalid doctor ID format: {doctor_id}, error: {str(e)}")
            raise ValueError(f"Invalid doctor ID format: {str(e)}")
        except Exception as e:
            print(f"Error retrieving doctor schedule: {str(e)}")
            raise ValueError(f"Error retrieving doctor schedule: {str(e)}")

    def update(self, schedule_id: str, update_data: dict) -> Optional[dict]:
        """Update a schedule."""
        try:
            schedule = self.db.query(DoctorSchedule).filter(
                DoctorSchedule.id == UUID(schedule_id)
            ).first()
            
            if not schedule:
                return None
                
            # Update fields if provided
            if "day_of_week" in update_data:
                schedule.day_of_week = int(update_data["day_of_week"])
            if "start_time" in update_data:
                schedule.start_time = time.fromisoformat(update_data["start_time"])
            if "end_time" in update_data:
                schedule.end_time = time.fromisoformat(update_data["end_time"])
            if "is_available" in update_data:
                schedule.is_available = update_data["is_available"]
                
            self.db.commit()
            self.db.refresh(schedule)
            
            return {
                "id": str(schedule.id),
                "doctor_id": str(schedule.doctor_id),
                "day_of_week": schedule.day_of_week,
                "start_time": schedule.start_time.isoformat(),
                "end_time": schedule.end_time.isoformat(),
                "is_available": schedule.is_available
            }
            
        except ValueError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data format: {str(e)}"
            )
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating schedule: {str(e)}"
            )

    def delete(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        try:
            schedule = self.db.query(DoctorSchedule).filter(
                DoctorSchedule.id == UUID(schedule_id)
            ).first()
            
            if not schedule:
                return False
                
            self.db.delete(schedule)
            self.db.commit()
            return True
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid UUID format"
            )

    def check_availability(self, doctor_id: UUID, day_of_week: int, time: time) -> bool:
        """Check if doctor is available at specified time."""
        schedule = self.db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.day_of_week == day_of_week,
            DoctorSchedule.is_available == True
        ).first()
        
        if not schedule:
            return False
            
        return schedule.start_time <= time <= schedule.end_time 