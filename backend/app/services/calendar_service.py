"""Calendar availability service for business logic."""
from datetime import date, time
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.service import CalendarAvailability


class SlotAlreadyExistsError(Exception):
    """Raised when trying to create a slot that already exists."""
    pass


def get_availability_for_date_range(
    db: Session,
    start_date: date,
    end_date: date,
    available_only: bool = False
) -> List[CalendarAvailability]:
    """
    Get calendar availability for a date range.

    Args:
        db: Database session
        start_date: Start date of range (inclusive)
        end_date: End date of range (inclusive)
        available_only: Only return available slots

    Returns:
        List of calendar availability slots
    """
    query = db.query(CalendarAvailability).filter(
        and_(
            CalendarAvailability.date >= start_date,
            CalendarAvailability.date <= end_date
        )
    )

    if available_only:
        query = query.filter(CalendarAvailability.is_available == True)

    return query.order_by(
        CalendarAvailability.date,
        CalendarAvailability.time_slot
    ).all()


def get_slot_by_id(
    db: Session,
    slot_id: UUID
) -> Optional[CalendarAvailability]:
    """Get a calendar slot by ID."""
    return db.query(CalendarAvailability).filter(
        CalendarAvailability.id == slot_id
    ).first()


def get_slot_by_datetime(
    db: Session,
    date_value: date,
    time_value: time
) -> Optional[CalendarAvailability]:
    """Get a calendar slot by date and time."""
    return db.query(CalendarAvailability).filter(
        and_(
            CalendarAvailability.date == date_value,
            CalendarAvailability.time_slot == time_value
        )
    ).first()


def block_time_slot(
    db: Session,
    date_value: date,
    time_value: time,
    reason: Optional[str] = None
) -> CalendarAvailability:
    """
    Block a time slot (mark as unavailable).

    Args:
        db: Database session
        date_value: Date to block
        time_value: Time slot to block
        reason: Optional reason for blocking

    Returns:
        Created or updated calendar availability slot

    Raises:
        SlotAlreadyExistsError: If slot already blocked
    """
    # Check if slot already exists
    existing_slot = get_slot_by_datetime(db, date_value, time_value)

    if existing_slot:
        # If already blocked, raise error
        if not existing_slot.is_available:
            raise SlotAlreadyExistsError(
                f"Time slot {date_value} {time_value} is already blocked"
            )

        # If available, update to blocked
        existing_slot.is_available = False
        existing_slot.reason = reason
        db.commit()
        db.refresh(existing_slot)
        return existing_slot

    # Create new blocked slot
    slot = CalendarAvailability(
        date=date_value,
        time_slot=time_value,
        is_available=False,
        reason=reason
    )

    db.add(slot)
    try:
        db.commit()
        db.refresh(slot)
        return slot
    except IntegrityError:
        db.rollback()
        raise SlotAlreadyExistsError(
            f"Time slot {date_value} {time_value} already exists"
        )


def unblock_time_slot(
    db: Session,
    slot_id: UUID
) -> bool:
    """
    Unblock a time slot (delete the blocked slot record).

    Args:
        db: Database session
        slot_id: ID of the slot to unblock

    Returns:
        True if unblocked, False if not found
    """
    slot = get_slot_by_id(db, slot_id)
    if not slot:
        return False

    db.delete(slot)
    db.commit()
    return True


def update_slot_availability(
    db: Session,
    slot_id: UUID,
    is_available: bool,
    reason: Optional[str] = None
) -> Optional[CalendarAvailability]:
    """
    Update a slot's availability status.

    Args:
        db: Database session
        slot_id: ID of the slot to update
        is_available: New availability status
        reason: Optional reason

    Returns:
        Updated slot or None if not found
    """
    slot = get_slot_by_id(db, slot_id)
    if not slot:
        return None

    slot.is_available = is_available
    if reason is not None:
        slot.reason = reason

    db.commit()
    db.refresh(slot)
    return slot


def is_slot_available(
    db: Session,
    date_value: date,
    time_value: time
) -> bool:
    """
    Check if a specific time slot is available for booking.

    Args:
        db: Database session
        date_value: Date to check
        time_value: Time to check

    Returns:
        True if available, False if blocked
    """
    slot = get_slot_by_datetime(db, date_value, time_value)

    # If no record exists, slot is available
    if not slot:
        return True

    # Return the availability status
    return slot.is_available
