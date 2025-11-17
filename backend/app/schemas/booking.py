"""
Booking schemas for request/response validation
"""
from datetime import datetime
from datetime import date as date_type
from datetime import time as time_type
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TimeSlot(BaseModel):
    """Time slot schema"""
    time: time_type = Field(..., description="Time slot")
    is_available: bool = Field(..., description="Whether the slot is available")
    reason: Optional[str] = Field(None, description="Reason if unavailable")


class DateAvailability(BaseModel):
    """Availability for a specific date"""
    date: date_type = Field(..., description="Date")
    is_available: bool = Field(..., description="Whether the date has any available slots")
    slots: list[TimeSlot] = Field(default_factory=list, description="Available time slots")


class AvailabilityResponse(BaseModel):
    """Response schema for availability check"""
    dates: list[DateAvailability] = Field(..., description="Availability by date")
    working_hours_start: time_type = Field(..., description="Working hours start time")
    working_hours_end: time_type = Field(..., description="Working hours end time")


class BookingCreate(BaseModel):
    """Schema for creating a booking"""
    package_id: UUID = Field(..., description="Service package ID")
    booking_date: date_type = Field(..., description="Booking date")
    booking_time: time_type = Field(..., description="Booking time")
    location_id: UUID = Field(..., description="Transport location ID")
    num_brides: int = Field(1, ge=0, description="Number of brides")
    num_maids: int = Field(0, ge=0, description="Number of maids/bridesmaids")
    num_mothers: int = Field(0, ge=0, description="Number of mothers")
    num_others: int = Field(0, ge=0, description="Number of other attendees")
    wedding_theme: Optional[str] = Field(None, max_length=255, description="Wedding theme")
    special_requests: Optional[str] = Field(None, description="Special requests")
    guest_email: Optional[str] = Field(None, description="Guest email (for non-authenticated users)")
    guest_name: Optional[str] = Field(None, description="Guest name (for non-authenticated users)")
    guest_phone: Optional[str] = Field(None, description="Guest phone (for non-authenticated users)")


class BookingResponse(BaseModel):
    """Schema for booking response"""
    id: UUID
    booking_number: str
    user_id: Optional[UUID]
    guest_email: Optional[str]
    guest_name: Optional[str]
    guest_phone: Optional[str]
    package_id: UUID
    booking_date: date_type
    booking_time: time_type
    location_id: UUID
    num_brides: int
    num_maids: int
    num_mothers: int
    num_others: int
    wedding_theme: Optional[str]
    special_requests: Optional[str]
    subtotal: float
    transport_cost: float
    total_amount: float
    deposit_amount: Optional[float]
    deposit_paid: bool
    deposit_paid_at: Optional[datetime]
    status: str
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookingListResponse(BaseModel):
    """Schema for paginated booking list response"""
    items: list[BookingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
