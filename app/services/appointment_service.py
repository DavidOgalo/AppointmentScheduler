from sqlalchemy.orm import Session
from app.db.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.db.models.user import User
from datetime import datetime, timedelta, time, date, timezone
from uuid import UUID, uuid4
from typing import List, Optional, Dict
from sqlalchemy.exc import IntegrityError
import uuid
from app.db.models.doctor_schedule import DoctorSchedule
from app.services.doctor_schedule_service import DoctorScheduleService
from fastapi import HTTPException, status

class AppointmentService:
    def __init__(self, db: Session, doctor_schedule_service: DoctorScheduleService):
        self.db = db
        self.doctor_schedule_service = doctor_schedule_service

    def _format_appointment(self, appointment: Appointment) -> Dict:
        """Format appointment object for response."""
        return {
            "id": str(appointment.id),
            "doctor_id": str(appointment.doctor_id),
            "patient_id": str(appointment.patient_id),
            "start_time": appointment.start_time.isoformat(),
            "end_time": appointment.end_time.isoformat(),
            "status": appointment.status,
            "reason": appointment.reason,
            "notes": appointment.notes,
            "created_at": appointment.created_at.isoformat(),
            "updated_at": appointment.updated_at.isoformat()
        }

    def _check_availability(self, doctor_id: str, start_time: datetime, end_time: datetime) -> tuple[bool, str]:
        """Check if doctor is available at the specified time."""
        try:
            # Get the day of week (0 = Monday, 6 = Sunday)
            day_of_week = start_time.weekday()
            
            print(f"Checking availability for doctor {doctor_id} on day {day_of_week} (date: {start_time.date()}) between {start_time.time()} and {end_time.time()}")
            
            # Get doctor's schedule for the day
            schedule = self.doctor_schedule_service.get_by_doctor(doctor_id, day_of_week)
            
            if not schedule:
                return False, f"Doctor does not have a schedule for {start_time.strftime('%A')}."
                
            if not schedule.is_available:
                return False, f"Doctor is not available on {start_time.strftime('%A')}."
                
            # Convert schedule times to datetime for comparison
            schedule_start = datetime.combine(start_time.date(), schedule.start_time)
            schedule_end = datetime.combine(start_time.date(), schedule.end_time)
            
            # Make all times timezone-aware using the same timezone
            if start_time.tzinfo is not None:
                tz = start_time.tzinfo
                schedule_start = schedule_start.replace(tzinfo=tz)
                schedule_end = schedule_end.replace(tzinfo=tz)
            else:
                # If start_time is naive, make it aware using UTC
                tz = timezone.utc
                start_time = start_time.replace(tzinfo=tz)
                end_time = end_time.replace(tzinfo=tz)
                schedule_start = schedule_start.replace(tzinfo=tz)
                schedule_end = schedule_end.replace(tzinfo=tz)
            
            print(f"Doctor schedule: {schedule_start.time()} to {schedule_end.time()}")
            print(f"Requested time: {start_time.time()} to {end_time.time()}")
            
            # Check if appointment time falls within doctor's schedule
            if start_time < schedule_start or end_time > schedule_end:
                return False, f"Requested time ({start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}) is outside doctor's working hours ({schedule_start.strftime('%H:%M')} to {schedule_end.strftime('%H:%M')})."
                
            # Check for existing appointments that overlap
            existing_appointments = self.db.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.start_time <= end_time,
                Appointment.end_time >= start_time,
                Appointment.status != "cancelled"
            ).first()
            
            if existing_appointments:
                print(f"Found overlapping appointment: {existing_appointments.id}")
                # Ensure existing appointment times are in the same timezone
                existing_start = existing_appointments.start_time
                existing_end = existing_appointments.end_time
                
                if existing_start.tzinfo is None:
                    existing_start = existing_start.replace(tzinfo=start_time.tzinfo)
                if existing_end.tzinfo is None:
                    existing_end = existing_end.replace(tzinfo=start_time.tzinfo)
                
                overlap_start = max(existing_start, start_time)
                overlap_end = min(existing_end, end_time)
                return False, f"Time slot conflicts with existing appointment from {overlap_start.strftime('%H:%M')} to {overlap_end.strftime('%H:%M')} on {start_time.strftime('%Y-%m-%d')}. Please choose a different time."
            
            print(f"Doctor is available at the requested time")
            return True, "Doctor is available at the requested time."
            
        except Exception as e:
            print(f"Error checking availability: {str(e)}")
            return False, f"Error checking availability: {str(e)}"

    def _generate_recurring_dates(self, start_date: datetime, pattern: str, end_date: datetime) -> List[datetime]:
        """Generate dates for recurring appointments."""
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            dates.append(current_date)
            
            if pattern == "daily":
                current_date += timedelta(days=1)
            elif pattern == "weekly":
                current_date += timedelta(weeks=1)
            elif pattern == "monthly":
                # Move to same day next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        return dates

    def create(self, appointment: AppointmentCreate) -> Dict:
        """Create a new appointment."""
        try:
            # Convert string IDs to UUIDs
            doctor_id = str(uuid.UUID(str(appointment.doctor_id)))
            patient_id = str(uuid.UUID(str(appointment.patient_id)))

            # Parse start_time and end_time
            try:
                # Try parsing as full datetime
                start_time = datetime.fromisoformat(appointment.start_time)
            except ValueError:
                # If not full datetime, assume it's just time and use today's date
                try:
                    time_only = time.fromisoformat(appointment.start_time)
                    start_time = datetime.combine(datetime.now().date(), time_only)
                except ValueError:
                    raise ValueError(f"Invalid start time format: {appointment.start_time}")
            
            try:
                # Try parsing as full datetime
                end_time = datetime.fromisoformat(appointment.end_time)
            except ValueError:
                # If not full datetime, assume it's just time and use today's date
                try:
                    time_only = time.fromisoformat(appointment.end_time)
                    end_time = datetime.combine(datetime.now().date(), time_only)
                except ValueError:
                    raise ValueError(f"Invalid end time format: {appointment.end_time}")

            # Check availability
            availability, message = self._check_availability(doctor_id, start_time, end_time)
            if not availability:
                raise ValueError(message)

            # Create appointment
            db_appointment = Appointment(
                doctor_id=doctor_id,
                patient_id=patient_id,
                start_time=start_time,
                end_time=end_time,
                status="scheduled",
                reason=appointment.reason or "General appointment",
                notes=appointment.notes
            )

            self.db.add(db_appointment)
            self.db.commit()
            self.db.refresh(db_appointment)
            
            return self._format_appointment(db_appointment)

        except ValueError as e:
            self.db.rollback()
            raise ValueError(f"Error creating appointment: {str(e)}")
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database error creating appointment: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Unexpected error creating appointment: {str(e)}")

    def get(self, appointment_id: str) -> Optional[Dict]:
        """Get an appointment by ID."""
        try:
            appointment = self.db.query(Appointment).filter(
                Appointment.id == UUID(str(appointment_id))
            ).first()
            
            if not appointment:
                return None
                
            return self._format_appointment(appointment)
            
        except ValueError as e:
            raise ValueError(f"Invalid appointment ID format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error retrieving appointment: {str(e)}")

    def get_by_doctor(self, doctor_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        """Get all appointments for a doctor, optionally filtered by date range."""
        try:
            doctor_id_uuid = UUID(str(doctor_id))
            
            # Start with base query
            query = self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id_uuid)
            
            # Apply date filters if provided
            if start_date:
                query = query.filter(Appointment.start_time >= start_date)
            if end_date:
                query = query.filter(Appointment.start_time <= end_date)
                
            # Order by start time
            query = query.order_by(Appointment.start_time)
            
            appointments = query.all()
            return [self._format_appointment(appointment) for appointment in appointments]
            
        except ValueError as e:
            raise ValueError(f"Invalid doctor ID format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error retrieving appointments: {str(e)}")

    def get_by_patient(self, patient_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        """Get all appointments for a patient, optionally filtered by date range."""
        try:
            patient_id_uuid = UUID(str(patient_id))
            
            # Start with base query
            query = self.db.query(Appointment).filter(Appointment.patient_id == patient_id_uuid)
            
            # Apply date filters if provided
            if start_date:
                query = query.filter(Appointment.start_time >= start_date)
            if end_date:
                query = query.filter(Appointment.start_time <= end_date)
                
            # Order by start time
            query = query.order_by(Appointment.start_time)
            
            appointments = query.all()
            return [self._format_appointment(appointment) for appointment in appointments]
            
        except ValueError as e:
            raise ValueError(f"Invalid patient ID format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error retrieving appointments: {str(e)}")

    def update(self, appointment_id: str, update_data: dict) -> Optional[Dict]:
        """Update an appointment."""
        try:
            appointment = self.db.query(Appointment).filter(
                Appointment.id == UUID(appointment_id)
            ).first()
            
            if not appointment:
                return None
                
            # If updating time, check availability
            if "start_time" in update_data or "end_time" in update_data:
                # Get new start and end times
                if "start_time" in update_data:
                    try:
                        start_time = datetime.fromisoformat(update_data["start_time"])
                    except ValueError:
                        raise ValueError("Invalid start_time format")
                else:
                    start_time = appointment.start_time
                    
                if "end_time" in update_data:
                    try:
                        end_time = datetime.fromisoformat(update_data["end_time"])
                    except ValueError:
                        raise ValueError("Invalid end_time format")
                else:
                    end_time = appointment.end_time
                
                # Check if the time change would cause a conflict
                availability, message = self._check_availability(str(appointment.doctor_id), start_time, end_time)
                if not availability:
                    raise ValueError(message)
                
                appointment.start_time = start_time
                appointment.end_time = end_time
            
            # Update other fields if provided
            if "status" in update_data:
                appointment.status = update_data["status"]
            if "reason" in update_data:
                appointment.reason = update_data["reason"]
            if "notes" in update_data:
                appointment.notes = update_data["notes"]
                
            self.db.commit()
            self.db.refresh(appointment)
            
            return self._format_appointment(appointment)
            
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
                detail=f"Error updating appointment: {str(e)}"
            )

    def delete(self, appointment_id: str) -> bool:
        """Delete an appointment."""
        try:
            appointment = self.db.query(Appointment).filter(
                Appointment.id == UUID(str(appointment_id))
            ).first()
            
            if not appointment:
                return False
            
            # Instead of hard delete, update status to cancelled
            appointment.status = "cancelled"
            self.db.commit()
            
            return True
            
        except ValueError as e:
            raise ValueError(f"Invalid appointment ID format: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error cancelling appointment: {str(e)}")

    def check_availability(self, doctor_id: str, start_time_str: str, end_time_str: str) -> tuple[bool, str]:
        """Check if a doctor is available at the specified time."""
        try:
            # Parse datetime strings
            try:
                start_time = datetime.fromisoformat(start_time_str)
            except ValueError:
                # If just a time is provided, combine with today's date
                try:
                    start_time = datetime.combine(
                        datetime.now().date(),
                        time.fromisoformat(start_time_str)
                    )
                except ValueError:
                    return False, f"Invalid start time format: {start_time_str}. Use ISO datetime (YYYY-MM-DDTHH:MM:SS) or time (HH:MM)."
                
            try:
                end_time = datetime.fromisoformat(end_time_str)
            except ValueError:
                # If just a time is provided, combine with today's date
                try:
                    end_time = datetime.combine(
                        datetime.now().date(),
                        time.fromisoformat(end_time_str)
                    )
                except ValueError:
                    return False, f"Invalid end time format: {end_time_str}. Use ISO datetime (YYYY-MM-DDTHH:MM:SS) or time (HH:MM)."
            
            if start_time >= end_time:
                return False, "End time must be after start time."
                
            return self._check_availability(doctor_id, start_time, end_time)
            
        except Exception as e:
            return False, f"Error checking availability: {str(e)}"