from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from fastapi import HTTPException, status

from app.db.models.doctor_patient_assignment import DoctorPatientAssignment
from app.schemas.doctor_patient_assignment import (
    DoctorPatientAssignmentCreate,
    DoctorPatientAssignmentUpdate
)
from app.db.models.doctor import Doctor
from app.db.models.patient import Patient

class DoctorPatientAssignmentService:
    def __init__(self, db: Session):
        self.db = db

    def _format_assignment(self, assignment: DoctorPatientAssignment) -> dict:
        """Format assignment for response."""
        return {
            "id": str(assignment.id),
            "doctor_id": str(assignment.doctor_id),
            "patient_id": str(assignment.patient_id),
            "is_active": assignment.is_active,
            "notes": assignment.notes,
            "assigned_date": assignment.assigned_date.isoformat(),
            "created_at": assignment.created_at.isoformat(),
            "updated_at": assignment.updated_at.isoformat()
        }

    def create(self, assignment_in: DoctorPatientAssignmentCreate, current_user: dict) -> dict:
        """Create a new doctor-patient assignment."""
        # Check if user has permission to create assignments
        if current_user.role not in ["admin", "doctor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to create doctor-patient assignments"
            )

        # Verify doctor exists
        doctor = self.db.query(Doctor).filter(Doctor.id == assignment_in.doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )

        # Verify patient exists
        patient = self.db.query(Patient).filter(Patient.id == assignment_in.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        # Check if assignment already exists
        existing = self.db.query(DoctorPatientAssignment).filter(
            DoctorPatientAssignment.doctor_id == assignment_in.doctor_id,
            DoctorPatientAssignment.patient_id == assignment_in.patient_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This doctor-patient assignment already exists"
            )

        assignment = DoctorPatientAssignment(
            doctor_id=assignment_in.doctor_id,
            patient_id=assignment_in.patient_id,
            is_active=assignment_in.is_active,
            notes=assignment_in.notes
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return self._format_assignment(assignment)

    def get(self, assignment_id: str, current_user: dict) -> Optional[dict]:
        """Get a doctor-patient assignment by ID."""
        assignment = self.db.query(DoctorPatientAssignment).filter(
            DoctorPatientAssignment.id == assignment_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor-patient assignment not found"
            )

        # Check if user has permission to view this assignment
        if current_user.role not in ["admin"] and str(current_user.doctor_id) != str(assignment.doctor_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this assignment"
            )

        return self._format_assignment(assignment)

    def get_by_doctor(self, doctor_id: str, current_user: dict) -> List[dict]:
        """Get all assignments for a doctor."""
        # Check if user has permission to view these assignments
        if current_user.role not in ["admin"] and str(current_user.doctor_id) != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view these assignments"
            )

        assignments = self.db.query(DoctorPatientAssignment).filter(
            DoctorPatientAssignment.doctor_id == doctor_id
        ).all()
        return [self._format_assignment(assignment) for assignment in assignments]

    def get_by_patient(self, patient_id: str, current_user: dict) -> List[dict]:
        """Get all assignments for a patient."""
        # Check if user has permission to view these assignments
        if current_user.role not in ["admin", "doctor"] and str(current_user.patient_id) != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view these assignments"
            )

        assignments = self.db.query(DoctorPatientAssignment).filter(
            DoctorPatientAssignment.patient_id == patient_id
        ).all()
        return [self._format_assignment(assignment) for assignment in assignments]

    def update(self, assignment_id: str, assignment_in: DoctorPatientAssignmentUpdate, current_user: dict) -> Optional[dict]:
        """Update a doctor-patient assignment."""
        assignment = self.db.query(DoctorPatientAssignment).filter(
            DoctorPatientAssignment.id == assignment_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor-patient assignment not found"
            )

        # Check if user has permission to update this assignment
        if current_user.role not in ["admin"] and str(current_user.doctor_id) != str(assignment.doctor_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this assignment"
            )

        for field, value in assignment_in.dict(exclude_unset=True).items():
            setattr(assignment, field, value)

        self.db.commit()
        self.db.refresh(assignment)
        return self._format_assignment(assignment)

    def delete(self, assignment_id: str, current_user: dict) -> bool:
        """Delete a doctor-patient assignment."""
        assignment = self.db.query(DoctorPatientAssignment).filter(
            DoctorPatientAssignment.id == assignment_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor-patient assignment not found"
            )

        # Check if user has permission to delete this assignment
        if current_user.role not in ["admin"] and str(current_user.doctor_id) != str(assignment.doctor_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this assignment"
            )

        self.db.delete(assignment)
        self.db.commit()
        return True 