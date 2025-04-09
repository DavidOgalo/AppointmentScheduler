from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security.security import get_current_user
from app.db.session import get_db
from app.schemas.patient import PatientCreate, PatientInDB
from app.services.patient_service import PatientService
from app.db.models.user import User

router = APIRouter()

@router.post("/", response_model=PatientInDB)
def create_patient_profile(
    *,
    db: Session = Depends(get_db),
    patient_in: PatientCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create patient profile.
    """
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can create patient profiles"
        )
    
    # Check if user already has a patient profile
    if current_user.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a patient profile"
        )
    
    patient_service = PatientService(db)
    patient = patient_service.create(obj_in=patient_in)
    
    # Link patient to user
    current_user.patient_id = patient.id
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return patient 