from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security.security import get_current_user
from app.db.session import get_db
from app.schemas.patient import PatientUpdate
from app.schemas.doctor import DoctorUpdate
from app.schemas.staff import StaffUpdate
from app.services.patient_service import PatientService
from app.services.doctor_service import DoctorService
from app.services.staff_service import StaffService
from app.db.models.user import User

router = APIRouter()

@router.put("/patient", response_model=Any)
def update_patient_profile(
    *,
    db: Session = Depends(get_db),
    profile_in: PatientUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update patient profile.
    """
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can update their profiles"
        )
    
    patient_service = PatientService(db)
    patient = patient_service.get_by_user_id(user_id=str(current_user.id))
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    patient = patient_service.update(db_obj=patient, obj_in=profile_in)
    return patient

@router.put("/doctor", response_model=Any)
def update_doctor_profile(
    *,
    db: Session = Depends(get_db),
    profile_in: DoctorUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update doctor profile.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update their profiles"
        )
    
    doctor_service = DoctorService(db)
    doctor = doctor_service.get_by_user_id(user_id=str(current_user.id))
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    doctor = doctor_service.update(db_obj=doctor, obj_in=profile_in)
    return doctor

@router.put("/staff/{staff_id}", response_model=Any)
def update_staff_profile(
    *,
    db: Session = Depends(get_db),
    staff_id: str,
    profile_in: StaffUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update staff profile (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update staff profiles"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.get(id=staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )
    
    staff = staff_service.update(db_obj=staff, obj_in=profile_in)
    return staff 