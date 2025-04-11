from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.doctor_patient_assignment import (
    DoctorPatientAssignmentCreate,
    DoctorPatientAssignmentUpdate,
    DoctorPatientAssignmentResponse
)
from app.services.doctor_patient_assignment_service import DoctorPatientAssignmentService

router = APIRouter()

@router.post("/", response_model=DoctorPatientAssignmentResponse)
def create_assignment(
    assignment_in: DoctorPatientAssignmentCreate,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Create new doctor-patient assignment."""
    assignment_service = DoctorPatientAssignmentService(db)
    try:
        assignment = assignment_service.create(assignment_in, current_user)
        return assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{assignment_id}", response_model=DoctorPatientAssignmentResponse)
def get_assignment(
    assignment_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get doctor-patient assignment by ID."""
    assignment_service = DoctorPatientAssignmentService(db)
    assignment = assignment_service.get(assignment_id, current_user)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor-patient assignment not found"
        )
    return assignment

@router.get("/doctor/{doctor_id}", response_model=List[DoctorPatientAssignmentResponse])
def get_doctor_assignments(
    doctor_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get all assignments for a doctor."""
    assignment_service = DoctorPatientAssignmentService(db)
    assignments = assignment_service.get_by_doctor(doctor_id, current_user)
    return assignments

@router.get("/patient/{patient_id}", response_model=List[DoctorPatientAssignmentResponse])
def get_patient_assignments(
    patient_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Get all assignments for a patient."""
    assignment_service = DoctorPatientAssignmentService(db)
    assignments = assignment_service.get_by_patient(patient_id, current_user)
    return assignments

@router.put("/{assignment_id}", response_model=DoctorPatientAssignmentResponse)
def update_assignment(
    assignment_id: str,
    assignment_in: DoctorPatientAssignmentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Update doctor-patient assignment."""
    assignment_service = DoctorPatientAssignmentService(db)
    assignment = assignment_service.update(assignment_id, assignment_in, current_user)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor-patient assignment not found"
        )
    return assignment

@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """Delete doctor-patient assignment."""
    assignment_service = DoctorPatientAssignmentService(db)
    success = assignment_service.delete(assignment_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor-patient assignment not found"
        )
    return {"message": "Doctor-patient assignment deleted successfully"} 