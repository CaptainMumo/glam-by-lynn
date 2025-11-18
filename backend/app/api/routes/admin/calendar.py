"""Admin API endpoints for calendar availability management."""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.calendar import (
    CalendarAvailabilityCreate,
    CalendarAvailabilityListResponse,
    CalendarAvailabilityResponse,
)
from app.services.calendar_service import (
    SlotAlreadyExistsError,
    block_time_slot,
    get_availability_for_date_range,
    get_slot_by_id,
    unblock_time_slot,
)

router = APIRouter(prefix="/admin/calendar", tags=["admin", "calendar"])


@router.get("", response_model=CalendarAvailabilityListResponse)
def get_calendar_availability(
    start_date: date = Query(..., alias="startDate", description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., alias="endDate", description="End date (YYYY-MM-DD)"),
    available_only: bool = Query(False, alias="availableOnly", description="Only show available slots"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get calendar availability for a date range (admin only).

    - **startDate**: Start date in YYYY-MM-DD format
    - **endDate**: End date in YYYY-MM-DD format
    - **availableOnly**: If true, only return available slots

    Returns blocked slots ordered by date and time.
    """
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be after start_date"
        )

    slots = get_availability_for_date_range(
        db,
        start_date=start_date,
        end_date=end_date,
        available_only=available_only
    )

    return CalendarAvailabilityListResponse(
        items=[CalendarAvailabilityResponse.model_validate(slot) for slot in slots],
        total=len(slots)
    )


@router.post("/block", response_model=CalendarAvailabilityResponse, status_code=status.HTTP_201_CREATED)
def block_calendar_slot(
    slot_data: CalendarAvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Block a time slot (admin only).

    Creates a blocked slot in the calendar to prevent bookings
    at the specified date and time.

    - **date**: Date to block (YYYY-MM-DD)
    - **timeSlot**: Time to block (HH:MM:SS)
    - **reason**: Optional reason for blocking
    """
    try:
        slot = block_time_slot(
            db,
            date_value=slot_data.date,
            time_value=slot_data.time_slot,
            reason=slot_data.reason
        )
        return slot
    except SlotAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/block/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def unblock_calendar_slot(
    slot_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Unblock a time slot (admin only).

    Removes a blocked slot from the calendar, making it available for bookings again.
    """
    deleted = unblock_time_slot(db, slot_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )
    return None


@router.get("/{slot_id}", response_model=CalendarAvailabilityResponse)
def get_calendar_slot(
    slot_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get a specific calendar slot by ID (admin only)."""
    slot = get_slot_by_id(db, slot_id)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )
    return slot
