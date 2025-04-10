from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.schemas.auth import Token, TokenPayload, UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user_service = UserService(db)
    user = user_service.authenticate(
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, user.role, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user_service = UserService(db)
    
    # Check if user with this email exists
    if user_service.get_by_email(email=user_in.email):
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )
    
    # Check if user with this username exists
    if user_service.get_by_username(username=user_in.username):
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists.",
        )
    
    # Validate role
    if user_in.role not in ["admin", "doctor", "staff", "patient"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Must be one of: admin, doctor, staff, patient",
        )
    
    user = user_service.create(obj_in=user_in)
    return user 