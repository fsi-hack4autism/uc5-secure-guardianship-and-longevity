"""
User profile routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from database import get_db
from models import User, UserProfile
from routes.auth import get_current_user

router = APIRouter()


class UserProfileResponse(BaseModel):
    """User profile response"""
    user_id: str
    full_name: Optional[str]
    email: str
    user_type: str
    diagnosed_conditions: Optional[list]
    accessibility_needs: Optional[list]
    is_active: bool
    
    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """Update profile request"""
    full_name: Optional[str] = None
    diagnosed_conditions: Optional[list] = None
    accessibility_needs: Optional[list] = None


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user profile"""
    user = db.query(User).filter(User.user_id == uuid.UUID(current_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        user_id=str(user.user_id),
        full_name=user.profile.full_name if user.profile else None,
        email=user.email,
        user_type=user.user_type,
        diagnosed_conditions=user.profile.diagnosed_conditions if user.profile else None,
        accessibility_needs=user.profile.accessibility_needs if user.profile else None,
        is_active=user.is_active,
    )


@router.put("/me", response_model=UserProfileResponse)
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile"""
    user = db.query(User).filter(User.user_id == uuid.UUID(current_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create profile
    profile = user.profile
    if not profile:
        profile = UserProfile(user_id=user.user_id)
        db.add(profile)
    
    # Update fields
    if request.full_name is not None:
        profile.full_name = request.full_name
    if request.diagnosed_conditions is not None:
        profile.diagnosed_conditions = request.diagnosed_conditions
    if request.accessibility_needs is not None:
        profile.accessibility_needs = request.accessibility_needs
    
    db.commit()
    db.refresh(user)
    
    return UserProfileResponse(
        user_id=str(user.user_id),
        full_name=user.profile.full_name if user.profile else None,
        email=user.email,
        user_type=user.user_type,
        diagnosed_conditions=user.profile.diagnosed_conditions if user.profile else None,
        accessibility_needs=user.profile.accessibility_needs if user.profile else None,
        is_active=user.is_active,
    )


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user profile by ID (only guardians/advisors can view others)"""
    user = db.query(User).filter(User.user_id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        user_id=str(user.user_id),
        full_name=user.profile.full_name if user.profile else None,
        email=user.email,
        user_type=user.user_type,
        diagnosed_conditions=user.profile.diagnosed_conditions if user.profile else None,
        accessibility_needs=user.profile.accessibility_needs if user.profile else None,
        is_active=user.is_active,
    )
