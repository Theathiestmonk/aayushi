"""
User management endpoints for the AI Dietitian Agent System
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class UserProfile(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None

class UpdateUserProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None

@router.get("/", response_model=List[UserProfile])
async def get_users():
    """Get all users (admin only)"""
    # TODO: Implement actual user retrieval
    return [
        UserProfile(
            id="user_123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            height_cm=170.0,
            weight_kg=70.0,
            activity_level="moderately_active"
        )
    ]

@router.get("/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    """Get user by ID"""
    # TODO: Implement actual user retrieval
    return UserProfile(
        id=user_id,
        email="test@example.com",
        first_name="Test",
        last_name="User",
        height_cm=170.0,
        weight_kg=70.0,
        activity_level="moderately_active"
    )

@router.put("/{user_id}", response_model=UserProfile)
async def update_user(user_id: str, user_data: UpdateUserProfile):
    """Update user profile"""
    # TODO: Implement actual user update
    return UserProfile(
        id=user_id,
        email="test@example.com",
        first_name=user_data.first_name or "Test",
        last_name=user_data.last_name or "User",
        height_cm=user_data.height_cm or 170.0,
        weight_kg=user_data.weight_kg or 70.0,
        activity_level=user_data.activity_level or "moderately_active"
    )

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete user"""
    # TODO: Implement actual user deletion
    return {"message": f"User {user_id} deleted successfully"}





