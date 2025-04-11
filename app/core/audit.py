from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models.audit_log import AuditLog
from app.db.models.user import User

class AuditLogger:
    @staticmethod
    def log_action(
        db: Session,
        user: User,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """Log an action to the audit log."""
        audit_log = AuditLog(
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            created_at=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()

    @staticmethod
    def log_medical_record_access(
        db: Session,
        user: User,
        action: str,
        record_id: str,
        ip_address: Optional[str] = None
    ) -> None:
        """Log medical record access."""
        AuditLogger.log_action(
            db=db,
            user=user,
            action=action,
            resource_type="medical_record",
            resource_id=record_id,
            details={
                "user_role": user.role,
                "user_id": str(user.id)
            },
            ip_address=ip_address
        ) 