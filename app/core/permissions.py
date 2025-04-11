from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.medical_record import MedicalRecord
from app.db.models.user import User

class MedicalRecordPermissions:
    @staticmethod
    def can_view_record(user: User, record: MedicalRecord) -> bool:
        """Check if user can view a medical record."""
        if user.role == "admin":
            return True
        if user.role == "doctor" and record.doctor_id == user.doctor_id:
            return True
        if user.role == "patient" and record.patient_id == user.patient_id:
            return True
        if user.role == "staff":
            # Staff can view records if they're in the same department as the doctor
            return True  # TODO: Implement department-based access in future version 
        return False

    @staticmethod
    def can_create_record(user: User, patient_id: str) -> bool:
        """Check if user can create a medical record."""
        if user.role == "admin":
            return True
        if user.role == "doctor":
            # TODO: Check if doctor is assigned to the patient, future version
            return True
        return False

    @staticmethod
    def can_update_record(user: User, record: MedicalRecord) -> bool:
        """Check if user can update a medical record."""
        if user.role == "admin":
            return True
        if user.role == "doctor" and record.doctor_id == user.doctor_id:
            return True
        return False

    @staticmethod
    def can_delete_record(user: User, record: MedicalRecord) -> bool:
        """Check if user can delete a medical record."""
        if user.role == "admin":
            return True
        if user.role == "doctor" and record.doctor_id == user.doctor_id:
            return True
        return False

def check_medical_record_permission(
    db: Session,
    user: User,
    record_id: Optional[str] = None,
    record: Optional[MedicalRecord] = None,
    action: str = "view"
) -> MedicalRecord:
    """Check if user has permission to perform action on medical record."""
    if not record and record_id:
        record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )

    has_permission = False
    if action == "view":
        has_permission = MedicalRecordPermissions.can_view_record(user, record)
    elif action == "create":
        has_permission = MedicalRecordPermissions.can_create_record(user, record.patient_id)
    elif action == "update":
        has_permission = MedicalRecordPermissions.can_update_record(user, record)
    elif action == "delete":
        has_permission = MedicalRecordPermissions.can_delete_record(user, record)

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action"
        )

    return record 