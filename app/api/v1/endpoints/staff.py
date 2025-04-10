from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.staff import StaffCreate, StaffUpdate, StaffResponse
from app.services.staff_service import StaffService

router = APIRouter()

@router.post("/", response_model=StaffResponse)
def create_staff(
    *,
    db: Session = Depends(get_db),
    staff_in: StaffCreate,
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Create new staff (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create staff"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.create(obj_in=staff_in)
    return staff

@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(
    *,
    db: Session = Depends(get_db),
    staff_id: str,
    staff_in: StaffUpdate,
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Update staff profile (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update staff"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.get(id=staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found"
        )
    
    staff = staff_service.update(id=staff_id, obj_in=staff_in)
    return staff

@router.get("/profile", response_model=StaffResponse)
def get_staff_profile(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Get staff profile (staff only).
    """
    if current_user.role != "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can view their profile"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.get_by_user_id(user_id=str(current_user.id))
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )
    return staff

@router.get("/", response_model=List[StaffResponse])
def read_staff(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Retrieve staff (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view staff"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.get_multi(skip=skip, limit=limit)
    return staff

@router.get("/{staff_id}", response_model=StaffResponse)
def read_staff_by_id(
    staff_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Get staff by ID (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view staff"
        )
    
    staff_service = StaffService(db)
    staff = staff_service.get(id=staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found"
        )
    return staff 