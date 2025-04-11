from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.api import deps
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.services.appointment_service import AppointmentService
from app.services.doctor_schedule_service import DoctorScheduleService


router = APIRouter()


@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    appointment_in: AppointmentCreate,
):
    """Create new appointment."""
    doctor_schedule_service = DoctorScheduleService(db)
    appointment_service = AppointmentService(db, doctor_schedule_service)
    try:
        appointment = appointment_service.create(appointment_in)
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    appointment_id: str,
):
    """Get appointment by ID."""
    doctor_schedule_service = DoctorScheduleService(db)
    appointment_service = AppointmentService(db, doctor_schedule_service)
    appointment = appointment_service.get(appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment


@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse])
def get_doctor_appointments(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    doctor_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Get all appointments for a doctor, optionally filtered by date range."""
    doctor_schedule_service = DoctorScheduleService(db)
    appointment_service = AppointmentService(db, doctor_schedule_service)
    
    try:
        # Verify role permissions - must be doctor, admin, or staff
        if current_user.role not in ["doctor", "admin", "staff"]:
            # If not doctor/admin/staff, verify it's the doctor requesting their own appointments
            if current_user.role == "doctor" and str(current_user.id) != doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own appointments"
                )
                
        # Convert date strings to datetime objects if provided
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
                
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
        
        appointments = appointment_service.get_by_doctor(doctor_id, start_datetime, end_datetime)
        return appointments
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
def get_patient_appointments(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    patient_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Get all appointments for a patient, optionally filtered by date range."""
    doctor_schedule_service = DoctorScheduleService(db)
    appointment_service = AppointmentService(db, doctor_schedule_service)
    
    try:
        # Verify role permissions - must be patient, doctor, admin, or staff
        if current_user.role not in ["doctor", "admin", "staff"]:
            # If not doctor/admin/staff, verify it's the patient requesting their own appointments
            if current_user.role == "patient" and str(current_user.id) != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own appointments"
                )
                
        # Convert date strings to datetime objects if provided
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
                
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
                
        appointments = appointment_service.get_by_patient(patient_id, start_datetime, end_datetime)
        return appointments
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    appointment_id: str,
    appointment_in: AppointmentUpdate,
):
    """Update appointment."""
    doctor_schedule_service = DoctorScheduleService(db)
    appointment_service = AppointmentService(db, doctor_schedule_service)
    appointment = appointment_service.update(appointment_id, appointment_in)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_200_OK)
def delete_appointment(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    appointment_id: str,
):
    """Delete (cancel) an appointment."""
    doctor_schedule_service = DoctorScheduleService(db)
    appointment_service = AppointmentService(db, doctor_schedule_service)
    success = appointment_service.delete(appointment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return {"message": "Appointment cancelled successfully"}


@router.get("/check-availability/{doctor_id}", response_model=dict)
def check_availability(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    doctor_id: str,
    start_time: str,
    end_time: str,
):
    """Check if a doctor is available at a specific time."""
    doctor_schedule_service = DoctorScheduleService(db)
    appointment_service = AppointmentService(db, doctor_schedule_service)
    try:
        is_available, message = appointment_service.check_availability(
            doctor_id, start_time, end_time
        )
        return {"available": is_available, "message": message}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
