"""
Public Booking API routes
Publicly accessible endpoints for booking availability and creation
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date as date_type, timedelta
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.schemas.booking import AvailabilityResponse, BookingCreate, BookingResponse
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/availability", response_model=AvailabilityResponse)
async def get_booking_availability(
    start_date: date_type = Query(..., description="Start date for availability check"),
    end_date: Optional[date_type] = Query(None, description="End date for availability check"),
    days: int = Query(7, ge=1, le=30, description="Number of days to check (if end_date not provided)"),
    db: Session = Depends(get_db)
):
    """
    Get booking availability for a date range (public endpoint)

    **Publicly accessible - No authentication required**

    Returns available time slots for booking, excluding:
    - Past dates
    - Manually blocked dates (from calendar_availability table)
    - Already booked slots

    Query parameters:
    - **start_date**: Start date for availability check (required)
    - **end_date**: End date for availability check (optional)
    - **days**: Number of days to check if end_date not provided (default: 7, max: 30)

    Returns:
    - List of dates with available time slots
    - Working hours information
    - Reasons for unavailable slots

    Working Hours:
    - Start: 8:00 AM
    - End: 6:00 PM
    - Slot duration: 1 hour
    """
    # Validate date range
    if end_date and end_date < start_date:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be after start_date"
        )

    # Get availability
    availability = booking_service.get_availability(
        db=db,
        start_date=start_date,
        end_date=end_date,
        days=days
    )

    return availability


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Create a new booking (public endpoint with optional authentication)

    **Publicly accessible - Authentication optional**

    Creates a booking for a makeup service. Can be used by both authenticated users
    and guests. Guest bookings require email, name, and phone number.

    Validation:
    - Package must exist and be active
    - Location must exist and be active
    - Number of maids must be within package limits (min/max)
    - Selected time slot must be available
    - Guest bookings require contact information

    Pricing:
    - Automatically calculated based on package rates and attendee counts
    - Transport cost added from location
    - 50% deposit calculated

    Booking Number:
    - Automatically generated in format: BK{YYYYMMDD}{####}
    - Example: BK202511170001

    Returns:
    - Created booking with status "pending"
    - Booking number for reference
    - Complete pricing breakdown
    - Deposit amount (50% of total)

    Raises:
    - 400: Validation error (invalid package, location, rules, or unavailable slot)
    - 401: Missing guest information for non-authenticated booking
    """
    try:
        # Get user ID if authenticated
        user_id = current_user.id if current_user else None

        # Create booking
        booking = booking_service.create_booking(
            db=db,
            booking_data=booking_data,
            user_id=user_id
        )

        return booking

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
