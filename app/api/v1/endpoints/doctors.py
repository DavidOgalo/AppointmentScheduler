from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.doctor import DoctorCreate, DoctorInDB, DoctorUpdate, DoctorResponse
from app.services.doctor_service import DoctorService
from app.db.models.user import User

router = APIRouter()

@router.post("/", response_model=DoctorInDB)
def create_doctor_profile(
    *,
    db: Session = Depends(get_db),
    doctor_in: DoctorCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create doctor profile.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create doctor profiles"
        )
    
    # Check if user already has a doctor profile
    if current_user.doctor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a doctor profile"
        )
    
    doctor_service = DoctorService(db)
    doctor = doctor_service.create(obj_in=doctor_in)
    
    # Link doctor to user
    current_user.doctor_id = doctor.id
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return doctor

@router.get("/profile", response_model=DoctorInDB)
def get_doctor_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get doctor profile.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view their profiles"
        )
    
    doctor_service = DoctorService(db)
    doctor = doctor_service.get_by_user_id(user_id=str(current_user.id))
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    return doctor 