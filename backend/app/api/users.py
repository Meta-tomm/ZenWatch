"""User profile API routes"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.database import get_db
from app.auth.deps import get_current_user
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Pydantic schemas for users
class UserProfileResponse(BaseModel):
    """Public user profile response"""
    id: int
    username: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserMeResponse(BaseModel):
    """Current user profile response (includes private data)"""
    id: int
    email: str
    username: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    role: str
    is_active: bool
    email_verified: bool = False
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """User profile update request"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


class DataExportResponse(BaseModel):
    """Data export request response"""
    message: str
    export_id: int
    status: str


@router.get("/users/me", response_model=UserMeResponse)
async def get_current_user_profile(
    current_user = Depends(get_current_user)
):
    """
    Get current authenticated user profile

    - Returns full user data including private fields
    """
    return UserMeResponse.model_validate(current_user)


@router.patch("/users/me", response_model=UserMeResponse)
async def update_current_user_profile(
    update_data: UserUpdateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile

    - Can update username, display_name, bio, avatar_url
    - Username must be unique
    """
    from app.models.user import User

    # Check if username is being changed and if it is unique
    if update_data.username and update_data.username != current_user.username:
        existing = db.query(User).filter(
            User.username == update_data.username,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Update fields that were provided
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    logger.info(f"User profile updated: {current_user.email}")

    return UserMeResponse.model_validate(current_user)


@router.delete("/users/me", response_model=MessageResponse)
async def delete_current_user(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account (GDPR right to erasure)

    - Soft deletes user account
    - Anonymizes user data
    - Keeps audit trail
    """
    # Soft delete: mark as inactive and anonymize
    current_user.is_active = False
    current_user.email = f"deleted_{current_user.id}@deleted.local"
    current_user.username = f"deleted_{current_user.id}"
    current_user.display_name = "Deleted User"
    current_user.password_hash = None
    current_user.avatar_url = None
    current_user.bio = None
    current_user.deleted_at = datetime.utcnow()

    db.commit()

    logger.info(f"User account deleted (soft): {current_user.id}")

    return MessageResponse(message="Account successfully deleted")


@router.get("/users/me/export", response_model=DataExportResponse)
async def request_data_export(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request data export (GDPR right to data portability)

    - Creates a data export request
    - Export will be processed asynchronously
    - User will receive email when ready
    """
    from app.models.consent import DataExportRequest

    # Check if there is a pending export request
    pending_request = db.query(DataExportRequest).filter(
        DataExportRequest.user_id == current_user.id,
        DataExportRequest.status == "pending"
    ).first()

    if pending_request:
        return DataExportResponse(
            message="Export request already pending",
            export_id=pending_request.id,
            status="pending"
        )

    # Create new export request
    export_request = DataExportRequest(
        user_id=current_user.id,
        status="pending",
        requested_at=datetime.utcnow(),
    )

    db.add(export_request)
    db.commit()
    db.refresh(export_request)

    logger.info(f"Data export requested: user_id={current_user.id}")

    return DataExportResponse(
        message="Data export requested. You will receive an email when ready.",
        export_id=export_request.id,
        status="pending"
    )


@router.get("/users/{username}/profile", response_model=UserProfileResponse)
async def get_user_public_profile(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Get public profile of a user by username

    - Returns only public data
    - Does not require authentication
    """
    from app.models.user import User

    user = db.query(User).filter(
        User.username == username,
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserProfileResponse.model_validate(user)
