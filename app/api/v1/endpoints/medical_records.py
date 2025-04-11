from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
    MedicalRecordListResponse
)
from app.services.medical_record_service import MedicalRecordService

router = APIRouter()

@router.post("/", response_model=MedicalRecordResponse)
def create_medical_record(
    record_in: MedicalRecordCreate,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Create new medical record."""
    medical_record_service = MedicalRecordService(db)
    try:
        record = medical_record_service.create(record_in, current_user)
        return record
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{record_id}", response_model=MedicalRecordResponse)
def get_medical_record(
    record_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get medical record by ID."""
    medical_record_service = MedicalRecordService(db)
    record = medical_record_service.get(record_id, current_user)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    return record

@router.get("/patient/{patient_id}", response_model=List[MedicalRecordResponse])
def get_patient_records(
    patient_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get all medical records for a patient."""
    medical_record_service = MedicalRecordService(db)
    records = medical_record_service.get_by_patient(patient_id, current_user)
    return records

@router.get("/doctor/{doctor_id}", response_model=List[MedicalRecordResponse])
def get_doctor_records(
    doctor_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get all medical records for a doctor."""
    medical_record_service = MedicalRecordService(db)
    records = medical_record_service.get_by_doctor(doctor_id, current_user)
    return records

@router.put("/{record_id}", response_model=MedicalRecordResponse)
def update_medical_record(
    record_id: str,
    record_in: MedicalRecordUpdate,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Update medical record."""
    medical_record_service = MedicalRecordService(db)
    record = medical_record_service.update(record_id, record_in, current_user)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    return record

@router.delete("/{record_id}")
def delete_medical_record(
    record_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Delete medical record."""
    medical_record_service = MedicalRecordService(db)
    success = medical_record_service.delete(record_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    return {"message": "Medical record deleted successfully"} 