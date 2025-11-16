"""
Auth schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth authentication"""
    email: EmailStr
    google_id: str = Field(..., alias="googleId")
    name: Optional[str] = None
    image: Optional[str] = None

    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    """Response model for token endpoints"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str


class UserResponse(BaseModel):
    """Response model for user information"""
    id: UUID
    email: str
    google_id: Optional[str] = None
    name: Optional[str] = None
    image: Optional[str] = None
    is_admin: bool = Field(..., alias="isAdmin")
    admin_role: Optional[str] = Field(None, alias="adminRole")
    is_active: bool = Field(..., alias="isActive")

    class Config:
        from_attributes = True
        populate_by_name = True
