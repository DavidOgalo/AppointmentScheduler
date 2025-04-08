from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.repositories.base import BaseRepository
from app.db.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

class AppointmentRepository(BaseRepository[Appointment, AppointmentCreate, AppointmentUpdate]):
    def __init__(self):
        super().__init__(Appointment)

    def get_by_patient(
        self, db: Session, patient_id: str, *, skip: int = 0, limit: int = 100
    ) -> List[Appointment]:
        return (
            db.query(Appointment)
            .filter(Appointment.patient_id == patient_id)
            .order_by(Appointment.appointment_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_doctor(
        self, db: Session, doctor_id: str, *, skip: int = 0, limit: int = 100
    ) -> List[Appointment]:
        return (
            db.query(Appointment)
            .filter(Appointment.doctor_id == doctor_id)
            .order_by(Appointment.appointment_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_upcoming_appointments(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Appointment]:
        return (
            db.query(Appointment)
            .filter(
                and_(
                    Appointment.appointment_date > datetime.utcnow(),
                    Appointment.status == AppointmentStatus.SCHEDULED
                )
            )
            .order_by(Appointment.appointment_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_doctor_schedule(
        self, db: Session, doctor_id: str, date: datetime
    ) -> List[Appointment]:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return (
            db.query(Appointment)
            .filter(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date >= start_of_day,
                    Appointment.appointment_date < end_of_day,
                    Appointment.status != AppointmentStatus.CANCELLED
                )
            )
            .order_by(Appointment.appointment_date.asc())
            .all()
        )

    def check_availability(
        self,
        db: Session,
        doctor_id: str,
        appointment_date: datetime,
        duration_minutes: int
    ) -> bool:
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        conflicting_appointments = (
            db.query(Appointment)
            .filter(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.status != AppointmentStatus.CANCELLED,
                    or_(
                        and_(
                            Appointment.appointment_date <= appointment_date,
                            Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) > appointment_date
                        ),
                        and_(
                            Appointment.appointment_date < end_time,
                            Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) >= end_time
                        ),
                        and_(
                            Appointment.appointment_date >= appointment_date,
                            Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) <= end_time
                        )
                    )
                )
            )
            .first()
        )
        
        return conflicting_appointments is None

    def cancel_appointment(self, db: Session, appointment_id: str) -> Optional[Appointment]:
        appointment = self.get(db, id=appointment_id)
        if appointment and appointment.status == AppointmentStatus.SCHEDULED:
            appointment.status = AppointmentStatus.CANCELLED
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            return appointment
        return None 