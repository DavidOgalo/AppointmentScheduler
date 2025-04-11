from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from fastapi import HTTPException, status

from app.db.models.medical_record import MedicalRecord
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate
from app.db.models.user import User
from app.core.permissions import MedicalRecordPermissions
from app.db.models.doctor_patient_assignment import DoctorPatientAssignment

class MedicalRecordService:
    def __init__(self, db: Session):
        self.db = db

    def _format_record(self, record: MedicalRecord) -> dict:
        """Format medical record for response."""
        return {
            "id": str(record.id),
            "patient_id": str(record.patient_id),
            "doctor_id": str(record.doctor_id),
            "appointment_id": str(record.appointment_id) if record.appointment_id else None,
            "diagnosis": record.diagnosis,
            "prescription": record.prescription,
            "notes": record.notes,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat()
        }

    def create(self, record_in: MedicalRecordCreate, current_user: dict) -> dict:
        """Create a new medical record."""
        # Check if user has permission to create record
        if not MedicalRecordPermissions.can_create_record(current_user, str(record_in.patient_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to create medical records"
            )

        # If user is a doctor, verify they are assigned to the patient
        if current_user.role == "doctor":
            assignment = self.db.query(DoctorPatientAssignment).filter(
                DoctorPatientAssignment.doctor_id == record_in.doctor_id,
                DoctorPatientAssignment.patient_id == record_in.patient_id,
                DoctorPatientAssignment.is_active == True
            ).first()
            
            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not assigned to this patient"
                )

        record = MedicalRecord(
            patient_id=record_in.patient_id,
            doctor_id=record_in.doctor_id,
            appointment_id=record_in.appointment_id,
            diagnosis=record_in.diagnosis,
            prescription=record_in.prescription,
            notes=record_in.notes
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._format_record(record)

    def get(self, record_id: str, current_user: dict) -> Optional[dict]:
        """Get a medical record by ID."""
        record = self.db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )

        if not MedicalRecordPermissions.can_view_record(current_user, record):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this record"
            )

        return self._format_record(record)

    def get_by_patient(self, patient_id: str, current_user: dict) -> List[dict]:
        """Get all medical records for a patient."""
        # Check if user has permission to view patient's records
        if current_user.role not in ["admin", "doctor"] and str(current_user.patient_id) != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view these records"
            )

        records = self.db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient_id
        ).all()
        return [self._format_record(record) for record in records]

    def get_by_doctor(self, doctor_id: str, current_user: dict) -> List[dict]:
        """Get all medical records for a doctor."""
        # Check if user has permission to view doctor's records
        if current_user.role not in ["admin"] and str(current_user.doctor_id) != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view these records"
            )

        records = self.db.query(MedicalRecord).filter(
            MedicalRecord.doctor_id == doctor_id
        ).all()
        return [self._format_record(record) for record in records]

    def update(self, record_id: str, record_in: MedicalRecordUpdate, current_user: dict) -> Optional[dict]:
        """Update a medical record."""
        record = self.db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )

        if not MedicalRecordPermissions.can_update_record(current_user, record):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this record"
            )

        for field, value in record_in.dict(exclude_unset=True).items():
            setattr(record, field, value)

        self.db.commit()
        self.db.refresh(record)
        return self._format_record(record)

    def delete(self, record_id: str, current_user: dict) -> bool:
        """Delete a medical record."""
        record = self.db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )

        if not MedicalRecordPermissions.can_delete_record(current_user, record):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this record"
            )

        self.db.delete(record)
        self.db.commit()
        return True 