from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.doctor_schedule import (
    DoctorScheduleCreate,
    DoctorScheduleUpdate,
    DoctorScheduleResponse
)
from app.services.doctor_schedule_service import DoctorScheduleService
from app.services.doctor_service import DoctorService

router = APIRouter()

@router.post("/", response_model=DoctorScheduleResponse)
def create_schedule(
    schedule_in: DoctorScheduleCreate,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new schedule for the current doctor.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create schedules"
        )
    
    doctor_service = DoctorService(db)
    doctor = doctor_service.get_by_user_id(user_id=str(current_user.id))
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    schedule_service = DoctorScheduleService(db)
    try:
        schedule = schedule_service.create(doctor_id=doctor["id"], obj_in=schedule_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return schedule

@router.get("/", response_model=List[DoctorScheduleResponse])
def get_schedules(
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all schedules for the current doctor.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view schedules"
        )
    
    doctor_service = DoctorService(db)
    doctor = doctor_service.get_by_user_id(user_id=str(current_user.id))
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    schedule_service = DoctorScheduleService(db)
    schedules = schedule_service.get_by_doctor(doctor_id=doctor["id"])
    return schedules

@router.put("/{schedule_id}", response_model=DoctorScheduleResponse)
def update_schedule(
    schedule_id: str,
    schedule_in: DoctorScheduleUpdate,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a schedule for the current doctor.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update schedules"
        )
    
    doctor_service = DoctorService(db)
    doctor = doctor_service.get_by_user_id(user_id=str(current_user.id))
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    schedule_service = DoctorScheduleService(db)
    schedule = schedule_service.get(schedule_id)
    if not schedule or schedule["doctor_id"] != doctor["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    try:
        updated_schedule = schedule_service.update(id=schedule_id, obj_in=schedule_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return updated_schedule

@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: str,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a schedule for the current doctor.
    """
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can delete schedules"
        )
    
    doctor_service = DoctorService(db)
    doctor = doctor_service.get_by_user_id(user_id=str(current_user.id))
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    schedule_service = DoctorScheduleService(db)
    schedule = schedule_service.get(schedule_id)
    if not schedule or schedule["doctor_id"] != doctor["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    if not schedule_service.delete(schedule_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete schedule"
        )
    
    return {"message": "Schedule deleted successfully"} 