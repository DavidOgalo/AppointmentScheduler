from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentInDB, AppointmentUpdate
from app.services.appointment_service import AppointmentService
from app.core.security.security import get_current_user
from app.db.models.user import User
from typing import Any, List
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=AppointmentInDB)
def create_appointment(
    *,
    db: Session = Depends(get_db),
    appointment_in: AppointmentCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new appointment.
    """
    appointment_service = AppointmentService(db)
    appointment = appointment_service.create(obj_in=appointment_in, user=current_user)
    return appointment

@router.get("/", response_model=List[AppointmentInDB])
def get_appointments(
    *,
    db: Session = Depends(get_db),
    doctor_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get all appointments for a specific doctor.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view their appointments"
        )
    
    appointment_service = AppointmentService(db)
    appointments = appointment_service.get_appointments_by_doctor(doctor_id=doctor_id)
    return appointments

@router.get("/{appointment_id}", response_model=AppointmentInDB)
def get_appointment(
    *,
    db: Session = Depends(get_db),
    appointment_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific appointment by ID.
    """
    appointment_service = AppointmentService(db)
    appointment = appointment_service.get_appointment_by_id(appointment_id=appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment

@router.put("/{appointment_id}/status", response_model=AppointmentInDB)
def update_appointment_status(
    *,
    db: Session = Depends(get_db),
    appointment_id: UUID,
    status: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update the status of a specific appointment.
    """
    appointment_service = AppointmentService(db)
    appointment = appointment_service.update_appointment_status(appointment_id=appointment_id, status=status, user=current_user)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment

@router.get("/doctor/{doctor_id}/schedule", response_model=List[AppointmentInDB])
def get_doctor_schedule(
    *,
    db: Session = Depends(get_db),
    doctor_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get the schedule for a specific doctor.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view their schedule"
        )
    
    appointment_service = AppointmentService(db)
    appointments = appointment_service.get_appointments_by_doctor(doctor_id=doctor_id)
    return appointments

@router.get("/patient/{patient_id}", response_model=List[AppointmentInDB])
def get_patient_appointments(
    *,
    db: Session = Depends(get_db),
    patient_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get all appointments for a specific patient.
    """
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view their appointments"
        )
    
    appointment_service = AppointmentService(db)
    appointments = appointment_service.get_appointments_by_patient(patient_id=patient_id)
    return appointments
