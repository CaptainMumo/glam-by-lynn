"""Calendar availability schemas for API requests and responses."""
from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CalendarAvailabilityCreate(BaseModel):
    """Schema for creating/blocking a calendar slot."""

    date: date
    time_slot: time = Field(..., alias="timeSlot")
    reason: Optional[str] = Field(None, max_length=255)

    class Config:
        populate_by_name = True


class CalendarAvailabilityUpdate(BaseModel):
    """Schema for updating a calendar slot."""

    is_available: bool = Field(..., alias="isAvailable")
    reason: Optional[str] = Field(None, max_length=255)

    class Config:
        populate_by_name = True


class CalendarAvailabilityResponse(BaseModel):
    """Schema for calendar availability response."""

    id: UUID
    date: date
    time_slot: time = Field(..., alias="timeSlot")
    is_available: bool = Field(..., alias="isAvailable")
    reason: Optional[str] = None
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class CalendarAvailabilityListResponse(BaseModel):
    """Schema for list of calendar availability slots."""

    items: List[CalendarAvailabilityResponse]
    total: int

    class Config:
        populate_by_name = True


class DateRangeQuery(BaseModel):
    """Schema for date range query parameters."""

    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date, info) -> date:
        """Validate that end_date is after start_date."""
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v

    class Config:
        populate_by_name = True
