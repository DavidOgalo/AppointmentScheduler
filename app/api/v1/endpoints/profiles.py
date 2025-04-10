from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.patient import PatientUpdate, PatientResponse
from app.schemas.doctor import DoctorUpdate, DoctorResponse
from app.schemas.staff import StaffUpdate, StaffResponse
from app.services.patient_service import PatientService
from app.services.doctor_service import DoctorService
from app.services.staff_service import StaffService

router = APIRouter()

@router.get("/patient", response_model=PatientResponse)
def get_patient_profile(
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get patient profile.
    """
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view their profile"
        )
    
    patient_service = PatientService(db)
    patient = patient_service.get_by_user_id(user_id=str(current_user.id))
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    return patient

@router.get("/doctor", response_model=DoctorResponse)
def get_doctor_profile(
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get doctor profile.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view their profile"
        )
    
    doctor_service = DoctorService(db)
    doctor = doctor_service.get_by_user_id(user_id=str(current_user.id))
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    return doctor

@router.put("/patient", response_model=PatientResponse)
def update_patient_profile(
    profile_in: PatientUpdate,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update patient profile.
    """
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can update their profile"
        )
    
    patient_service = PatientService(db)
    patient = patient_service.get_by_user_id(user_id=str(current_user.id))
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    patient = patient_service.update(id=patient.id, obj_in=profile_in)
    return patient

@router.put("/doctor", response_model=DoctorResponse)
def update_doctor_profile(
    profile_in: DoctorUpdate,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update doctor profile.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update their profile"
        )
    
    doctor_service = DoctorService(db)
    doctor = doctor_service.get_by_user_id(user_id=str(current_user.id))
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    doctor = doctor_service.update(id=doctor.id, obj_in=profile_in)
    return doctor

@router.put("/staff", response_model=StaffResponse)
def update_staff_profile(
    profile_in: StaffUpdate,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update staff profile.
    """
    if current_user.role != "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update their profile"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.get_by_user_id(user_id=str(current_user.id))
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )
    
    staff = staff_service.update(id=staff.id, obj_in=profile_in)
    return staff 