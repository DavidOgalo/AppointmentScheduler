from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.user import UserUpdate
from app.services.user_service import UserService
from app.db.models.user import User

router = APIRouter()

@router.put("/profile", response_model=Any)
def update_user_profile(
    *,
    db: Session = Depends(get_db),
    profile_in: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update user profile (basic info like email, username, etc.).
    """
    user_service = UserService(db)
    user = user_service.update(db_obj=current_user, obj_in=profile_in)
    return user 