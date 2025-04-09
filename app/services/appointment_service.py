from sqlalchemy.orm import Session
from app.db.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate
from app.db.models.user import User
from datetime import datetime
from uuid import UUID
from typing import List, Optional

class AppointmentService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: AppointmentCreate, user: User) -> Appointment:
        # Ensure the user is authorized to create an appointment
        if user.role not in ["doctor", "staff"]:
            raise ValueError("User is not authorized to create appointments")

        # Create the appointment
        db_obj = Appointment(
            doctor_id=obj_in.doctor_id,
            patient_id=obj_in.patient_id,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            status=obj_in.status,
            reason=obj_in.reason,
            notes=obj_in.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_appointments_by_doctor(self, doctor_id: UUID) -> List[Appointment]:
        return self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()

    def get_appointment_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def update_appointment_status(self, appointment_id: UUID, status: str, user: User) -> Optional[Appointment]:
        # Ensure the user is authorized to update appointment status
        if user.role not in ["doctor", "staff"]:
            raise ValueError("User is not authorized to update appointment status")

        appointment = self.get_appointment_by_id(appointment_id=appointment_id)
        if not appointment:
            return None
        appointment.status = status
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def get_appointments_by_patient(self, patient_id: UUID) -> List[Appointment]:
        return self.db.query(Appointment).filter(Appointment.patient_id == patient_id).all()