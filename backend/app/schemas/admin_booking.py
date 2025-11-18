"""Admin booking schemas for management endpoints."""
from datetime import date as date_type
from datetime import time as time_type
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AdminBookingUpdate(BaseModel):
    """Schema for admin updating a booking."""

    booking_date: Optional[date_type] = Field(None, description="New booking date")
    booking_time: Optional[time_type] = Field(None, description="New booking time")
    location_id: Optional[UUID] = Field(None, description="New location ID")
    num_brides: Optional[int] = Field(None, ge=0, description="Number of brides")
    num_maids: Optional[int] = Field(None, ge=0, description="Number of maids")
    num_mothers: Optional[int] = Field(None, ge=0, description="Number of mothers")
    num_others: Optional[int] = Field(None, ge=0, description="Number of others")
    wedding_theme: Optional[str] = Field(None, max_length=255)
    special_requests: Optional[str] = Field(None)
    admin_notes: Optional[str] = Field(None)


class AdminBookingStatusUpdate(BaseModel):
    """Schema for updating booking status."""

    status: str = Field(
        ...,
        description="Booking status",
        pattern="^(pending|confirmed|deposit_paid|completed|cancelled)$",
    )
    admin_notes: Optional[str] = Field(None, description="Admin notes about the status change")


class AdminBookingDepositUpdate(BaseModel):
    """Schema for marking deposit as paid."""

    deposit_paid: bool = Field(..., description="Deposit paid status")
    admin_notes: Optional[str] = Field(None, description="Admin notes about the deposit payment")
