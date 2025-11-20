"""Vision registration schemas for API requests and responses."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class VisionRegistrationCreate(BaseModel):
    """Schema for creating a vision registration."""

    full_name: str = Field(..., min_length=2, max_length=255, alias="fullName")
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20, alias="phoneNumber")
    location: Optional[str] = Field(None, max_length=100)
    interested_in_salon: bool = Field(default=False, alias="interestedInSalon")
    interested_in_barbershop: bool = Field(default=False, alias="interestedInBarbershop")
    interested_in_spa: bool = Field(default=False, alias="interestedInSpa")
    interested_in_mobile_van: bool = Field(default=False, alias="interestedInMobileVan")
    additional_comments: Optional[str] = Field(None, max_length=2000, alias="additionalComments")

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validate and clean full name."""
        v = v.strip()
        if not v:
            raise ValueError("Full name cannot be empty")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and clean phone number."""
        # Remove common formatting characters
        cleaned = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not cleaned.isdigit() and not cleaned.startswith("+"):
            raise ValueError("Phone number must contain only digits and optional + prefix")
        return v

    model_config = {"populate_by_name": True}


class VisionRegistrationResponse(BaseModel):
    """Schema for vision registration response."""

    id: UUID
    full_name: str = Field(..., alias="fullName")
    email: str
    phone_number: str = Field(..., alias="phoneNumber")
    location: Optional[str] = None
    interested_in_salon: bool = Field(..., alias="interestedInSalon")
    interested_in_barbershop: bool = Field(..., alias="interestedInBarbershop")
    interested_in_spa: bool = Field(..., alias="interestedInSpa")
    interested_in_mobile_van: bool = Field(..., alias="interestedInMobileVan")
    additional_comments: Optional[str] = Field(None, alias="additionalComments")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"from_attributes": True, "populate_by_name": True}
