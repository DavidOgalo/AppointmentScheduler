from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse
)
from app.services.appointment_service import AppointmentService
from app.core.auth import get_current_user
from app.schemas.user import User

router = APIRouter()

@router.post("/", response_model=List[AppointmentResponse])
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new appointment"""
    service = AppointmentService(db)
    try:
        return service.create(appointment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=AppointmentResponse)
def get_appointment(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get an appointment by ID"""
    service = AppointmentService(db)
    appointment = service.get(id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.get("/doctor/{doctor_id}", response_model=AppointmentListResponse)
def get_doctor_appointments(
    doctor_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all appointments for a doctor"""
    service = AppointmentService(db)
    try:
        appointments = service.get_by_doctor(doctor_id, start_date, end_date)
        return {"items": appointments, "total": len(appointments)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/patient/{patient_id}", response_model=AppointmentListResponse)
def get_patient_appointments(
    patient_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all appointments for a patient"""
    service = AppointmentService(db)
    try:
        appointments = service.get_by_patient(patient_id, start_date, end_date)
        return {"items": appointments, "total": len(appointments)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=AppointmentResponse)
def update_appointment(
    id: str,
    appointment: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an appointment"""
    service = AppointmentService(db)
    try:
        return service.update(id, appointment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
def delete_appointment(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an appointment"""
    service = AppointmentService(db)
    try:
        success = service.delete(id)
        if not success:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return {"message": "Appointment deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/availability/{doctor_id}")
def check_availability(
    doctor_id: str,
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if a doctor is available at a specific time"""
    service = AppointmentService(db)
    try:
        return service.check_availability(doctor_id, start_time, end_time)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
