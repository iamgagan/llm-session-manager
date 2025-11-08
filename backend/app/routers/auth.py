"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from typing import Optional

from ..database import get_db
from ..models import User, Team
from ..auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user
)
from ..config import get_settings

router = APIRouter()
settings = get_settings()


# Request/Response models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    team_name: Optional[str] = None  # Optional: create/join team


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    team_id: Optional[str]
    role: str
    is_active: bool


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        JWT token and user info

    Raises:
        HTTPException: If email or username already exists
    """
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Handle team creation/joining
    team_id = None
    if user_data.team_name:
        # Check if team exists
        team = db.query(Team).filter(Team.name == user_data.team_name).first()
        if team:
            team_id = team.id
        else:
            # Create new team
            team = Team(
                name=user_data.team_name,
                description=f"Team created by {user_data.username}"
            )
            db.add(team)
            db.flush()  # Get team ID
            team_id = team.id

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        team_id=team_id,
        role="admin" if team_id and not db.query(User).filter(User.team_id == team_id).first() else "member",
        is_active=True,
        is_verified=False  # Could send verification email
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "team_id": user.team_id,
            "role": user.role
        }
    }


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token.

    Args:
        credentials: Login credentials
        db: Database session

    Returns:
        JWT token and user info

    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "team_id": user.team_id,
            "role": user.role
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "team_id": current_user.team_id,
        "role": current_user.role,
        "is_active": current_user.is_active
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard token).

    Args:
        current_user: Current authenticated user

    Returns:
        Success message
    """
    # In JWT, we don't actually invalidate tokens server-side
    # Client should discard the token
    # Could implement token blacklist if needed

    return {
        "message": "Successfully logged out",
        "username": current_user.username
    }


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password.

    Args:
        current_password: Current password
        new_password: New password
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If current password is incorrect
    """
    from ..auth import verify_password

    # Verify current password
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    # Update password
    current_user.password_hash = get_password_hash(new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.delete("/account")
async def delete_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account.

    Args:
        password: User password for confirmation
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If password is incorrect
    """
    from ..auth import verify_password

    # Verify password
    if not verify_password(password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    # Soft delete (deactivate)
    current_user.is_active = False
    db.commit()

    return {"message": "Account deactivated successfully"}


@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Verify if token is valid.

    Args:
        current_user: Current authenticated user

    Returns:
        Validation status
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username
    }
