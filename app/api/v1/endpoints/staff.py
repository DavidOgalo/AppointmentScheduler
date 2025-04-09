from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security.security import get_current_user
from app.db.session import get_db
from app.schemas.staff import StaffCreate, StaffInDB, StaffUpdate
from app.services.staff_service import StaffService
from app.db.models.user import User

router = APIRouter()

@router.post("/", response_model=StaffInDB)
def create_staff_profile(
    *,
    db: Session = Depends(get_db),
    staff_in: StaffCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create staff profile.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create staff profiles"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.create(obj_in=staff_in)
    return staff

@router.put("/profile", response_model=StaffInDB)
def update_staff_profile(
    *,
    db: Session = Depends(get_db),
    staff_in: StaffUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update staff profile.
    """
    if current_user.role != "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update their profiles"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.get_by_user_id(user_id=str(current_user.id))
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )
    
    staff = staff_service.update(db_obj=staff, obj_in=staff_in)
    return staff

@router.get("/profile", response_model=StaffInDB)
def get_staff_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get staff profile.
    """
    if current_user.role != "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can view their profiles"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.get_by_user_id(user_id=str(current_user.id))
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )
    
    return staff 