from sqlalchemy.orm import Session
from app.db.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.db.models.user import User
from datetime import datetime, timedelta
from uuid import UUID
from typing import List, Optional, Dict
from sqlalchemy.exc import IntegrityError
import uuid
from app.db.models.doctor_schedule import DoctorSchedule
from app.services.doctor_schedule_service import DoctorScheduleService

class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.doctor_schedule_service = DoctorScheduleService(db)

    def _format_appointment(self, appointment: Appointment) -> dict:
        """Format an appointment object for response"""
        return {
            "id": str(appointment.id),
            "patient_id": str(appointment.patient_id),
            "doctor_id": str(appointment.doctor_id),
            "start_time": appointment.start_time,
            "end_time": appointment.end_time,
            "status": appointment.status,
            "reason": appointment.reason,
            "notes": appointment.notes,
            "is_recurring": appointment.is_recurring,
            "recurrence_pattern": appointment.recurrence_pattern,
            "recurrence_end_date": appointment.recurrence_end_date,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at
        }

    def _check_availability(self, doctor_id: str, start_time: datetime, end_time: datetime) -> bool:
        """Check if a doctor is available at the specified time"""
        # Get the day of week (0=Monday, 6=Sunday)
        day_of_week = start_time.weekday()
        
        # Check if the doctor has a schedule for this day
        schedules = self.doctor_schedule_service.get_by_doctor(doctor_id)
        day_schedule = next((s for s in schedules if s["day_of_week"] == day_of_week), None)
        
        if not day_schedule or not day_schedule["is_available"]:
            return False
        
        # Convert schedule times to datetime for comparison
        schedule_start = datetime.combine(start_time.date(), day_schedule["start_time"])
        schedule_end = datetime.combine(start_time.date(), day_schedule["end_time"])
        
        # Check if appointment is within doctor's schedule
        if start_time < schedule_start or end_time > schedule_end:
            return False
        
        # Check for conflicts with existing appointments
        conflicts = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status != "cancelled",
            (
                (Appointment.start_time < end_time) &
                (Appointment.end_time > start_time)
            )
        ).first()
        
        return conflicts is None

    def _generate_recurring_dates(self, start_time: datetime, pattern: str, end_date: datetime) -> List[datetime]:
        """Generate recurring appointment dates based on pattern"""
        dates = []
        current = start_time
        
        while current <= end_date:
            dates.append(current)
            if pattern == "daily":
                current += timedelta(days=1)
            elif pattern == "weekly":
                current += timedelta(weeks=1)
            elif pattern == "monthly":
                # Add one month, preserving the day of month
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
        
        return dates

    def create(self, obj_in: AppointmentCreate) -> dict:
        try:
            # Validate doctor and patient IDs
            doctor_uuid = str(uuid.UUID(obj_in.doctor_id))
            patient_uuid = str(uuid.UUID(obj_in.patient_id))
            
            # Check availability for the initial appointment
            if not self._check_availability(doctor_uuid, obj_in.start_time, obj_in.end_time):
                raise ValueError("Doctor is not available at the specified time")
            
            appointments = []
            
            if obj_in.is_recurring:
                # Generate recurring appointment dates
                dates = self._generate_recurring_dates(
                    obj_in.start_time,
                    obj_in.recurrence_pattern,
                    obj_in.recurrence_end_date
                )
                
                # Create appointments for each date
                for date in dates:
                    # Calculate duration
                    duration = obj_in.end_time - obj_in.start_time
                    
                    # Create new appointment
                    appointment = Appointment(
                        patient_id=patient_uuid,
                        doctor_id=doctor_uuid,
                        start_time=date,
                        end_time=date + duration,
                        status="scheduled",
                        reason=obj_in.reason,
                        notes=obj_in.notes,
                        is_recurring=True,
                        recurrence_pattern=obj_in.recurrence_pattern,
                        recurrence_end_date=obj_in.recurrence_end_date
                    )
                    
                    # Check availability for this specific occurrence
                    if not self._check_availability(doctor_uuid, date, date + duration):
                        raise ValueError(f"Doctor is not available on {date}")
                    
                    self.db.add(appointment)
                    appointments.append(appointment)
            else:
                # Create single appointment
                appointment = Appointment(
                    patient_id=patient_uuid,
                    doctor_id=doctor_uuid,
                    start_time=obj_in.start_time,
                    end_time=obj_in.end_time,
                    status="scheduled",
                    reason=obj_in.reason,
                    notes=obj_in.notes
                )
                self.db.add(appointment)
                appointments.append(appointment)
            
            self.db.commit()
            
            # Return the first appointment (or all if recurring)
            return [self._format_appointment(a) for a in appointments]
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error creating appointment: {str(e)}")

    def get(self, id: str) -> Optional[dict]:
        try:
            appointment_uuid = str(uuid.UUID(id))
            appointment = self.db.query(Appointment).filter(Appointment.id == appointment_uuid).first()
            return self._format_appointment(appointment) if appointment else None
        except ValueError:
            raise ValueError("Invalid appointment ID format")

    def get_by_doctor(self, doctor_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        try:
            doctor_uuid = str(uuid.UUID(doctor_id))
            query = self.db.query(Appointment).filter(Appointment.doctor_id == doctor_uuid)
            
            if start_date:
                query = query.filter(Appointment.start_time >= start_date)
            if end_date:
                query = query.filter(Appointment.end_time <= end_date)
            
            appointments = query.all()
            return [self._format_appointment(a) for a in appointments]
        except ValueError:
            raise ValueError("Invalid doctor ID format")

    def get_by_patient(self, patient_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        try:
            patient_uuid = str(uuid.UUID(patient_id))
            query = self.db.query(Appointment).filter(Appointment.patient_id == patient_uuid)
            
            if start_date:
                query = query.filter(Appointment.start_time >= start_date)
            if end_date:
                query = query.filter(Appointment.end_time <= end_date)
            
            appointments = query.all()
            return [self._format_appointment(a) for a in appointments]
        except ValueError:
            raise ValueError("Invalid patient ID format")

    def update(self, id: str, obj_in: AppointmentUpdate) -> dict:
        try:
            appointment_uuid = str(uuid.UUID(id))
            appointment = self.db.query(Appointment).filter(Appointment.id == appointment_uuid).first()
            
            if not appointment:
                raise ValueError("Appointment not found")
            
            # If updating time, check availability
            if obj_in.start_time or obj_in.end_time:
                new_start = obj_in.start_time or appointment.start_time
                new_end = obj_in.end_time or appointment.end_time
                
                if not self._check_availability(str(appointment.doctor_id), new_start, new_end):
                    raise ValueError("Doctor is not available at the specified time")
            
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(appointment, field, value)
            
            self.db.commit()
            self.db.refresh(appointment)
            return self._format_appointment(appointment)
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error updating appointment: {str(e)}")

    def delete(self, id: str) -> bool:
        try:
            appointment_uuid = str(uuid.UUID(id))
            appointment = self.db.query(Appointment).filter(Appointment.id == appointment_uuid).first()
            
            if not appointment:
                return False
            
            self.db.delete(appointment)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error deleting appointment: {str(e)}")

    def check_availability(self, doctor_id: str, start_time: datetime, end_time: datetime) -> Dict[str, bool]:
        """Check if a doctor is available at the specified time"""
        try:
            doctor_uuid = str(uuid.UUID(doctor_id))
            is_available = self._check_availability(doctor_uuid, start_time, end_time)
            return {"available": is_available}
        except ValueError:
            raise ValueError("Invalid doctor ID format")