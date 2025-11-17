"""
Booking service
Business logic for booking availability and management
"""
from datetime import datetime, timedelta
from datetime import date as date_type
from datetime import time as time_type
from typing import Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.booking import Booking
from app.models.service import CalendarAvailability, ServicePackage, TransportLocation
from app.models.user import User
from app.schemas.booking import DateAvailability, TimeSlot, AvailabilityResponse, BookingCreate


# Define working hours
WORKING_HOURS_START = time_type(8, 0)  # 8:00 AM
WORKING_HOURS_END = time_type(18, 0)   # 6:00 PM
SLOT_DURATION_MINUTES = 60             # 1-hour slots


def get_time_slots() -> list[time_type]:
    """
    Generate list of available time slots within working hours

    Returns:
        List of time slots (hourly intervals)
    """
    slots = []
    current_time = datetime.combine(date_type.today(), WORKING_HOURS_START)
    end_time = datetime.combine(date_type.today(), WORKING_HOURS_END)

    while current_time < end_time:
        slots.append(current_time.time())
        current_time += timedelta(minutes=SLOT_DURATION_MINUTES)

    return slots


def is_slot_available(
    db: Session,
    check_date: date_type,
    check_time: time_type
) -> tuple[bool, Optional[str]]:
    """
    Check if a specific date and time slot is available

    Args:
        db: Database session
        check_date: Date to check
        check_time: Time to check

    Returns:
        Tuple of (is_available, reason)
    """
    # Check if the date is in the past
    if check_date < date_type.today():
        return False, "Past date"

    # Check calendar availability (manually blocked dates)
    calendar_block = db.query(CalendarAvailability).filter(
        and_(
            CalendarAvailability.date == check_date,
            CalendarAvailability.time_slot == check_time,
            CalendarAvailability.is_available == False
        )
    ).first()

    if calendar_block:
        return False, calendar_block.reason or "Unavailable"

    # Check if there's already a booking for this slot
    existing_booking = db.query(Booking).filter(
        and_(
            Booking.booking_date == check_date,
            Booking.booking_time == check_time,
            Booking.status.in_(['pending', 'confirmed', 'deposit_paid'])
        )
    ).first()

    if existing_booking:
        return False, "Booked"

    return True, None


def get_availability(
    db: Session,
    start_date: date_type,
    end_date: Optional[date_type] = None,
    days: int = 7
) -> AvailabilityResponse:
    """
    Get booking availability for a date range

    Args:
        db: Database session
        start_date: Start date for availability check
        end_date: End date for availability check (optional)
        days: Number of days to check if end_date not provided (default: 7)

    Returns:
        AvailabilityResponse with date and time slot availability
    """
    # Determine end date
    if end_date is None:
        end_date = start_date + timedelta(days=days - 1)

    # Ensure we don't check too far in advance (max 90 days)
    max_end_date = date_type.today() + timedelta(days=90)
    if end_date > max_end_date:
        end_date = max_end_date

    # Get all time slots
    time_slots = get_time_slots()

    # Check availability for each date
    date_availability_list = []
    current_date = start_date

    while current_date <= end_date:
        slots = []
        has_available_slot = False

        for slot_time in time_slots:
            is_available, reason = is_slot_available(db, current_date, slot_time)

            if is_available:
                has_available_slot = True

            slots.append(TimeSlot(
                time=slot_time,
                is_available=is_available,
                reason=reason
            ))

        date_availability_list.append(DateAvailability(
            date=current_date,
            is_available=has_available_slot,
            slots=slots
        ))

        current_date += timedelta(days=1)

    return AvailabilityResponse(
        dates=date_availability_list,
        working_hours_start=WORKING_HOURS_START,
        working_hours_end=WORKING_HOURS_END
    )


def generate_booking_number(db: Session) -> str:
    """
    Generate a unique booking number

    Format: BK{YYYYMMDD}{####} where #### is a 4-digit counter

    Args:
        db: Database session

    Returns:
        Unique booking number
    """
    today = date_type.today()
    date_prefix = f"BK{today.strftime('%Y%m%d')}"

    # Get the count of bookings created today
    count = db.query(func.count(Booking.id)).filter(
        Booking.booking_number.like(f"{date_prefix}%")
    ).scalar() or 0

    # Generate number with padding
    booking_number = f"{date_prefix}{(count + 1):04d}"

    # Ensure uniqueness (in case of concurrent requests)
    while db.query(Booking).filter(Booking.booking_number == booking_number).first():
        count += 1
        booking_number = f"{date_prefix}{(count + 1):04d}"

    return booking_number


def calculate_booking_price(
    db: Session,
    package_id: UUID,
    location_id: UUID,
    num_brides: int,
    num_maids: int,
    num_mothers: int,
    num_others: int
) -> tuple[Decimal, Decimal, Decimal]:
    """
    Calculate booking pricing

    Args:
        db: Database session
        package_id: Service package ID
        location_id: Transport location ID
        num_brides: Number of brides
        num_maids: Number of maids
        num_mothers: Number of mothers
        num_others: Number of other attendees

    Returns:
        Tuple of (subtotal, transport_cost, total_amount)

    Raises:
        ValueError: If package or location not found
    """
    # Get package
    package = db.query(ServicePackage).filter(ServicePackage.id == package_id).first()
    if not package:
        raise ValueError(f"Service package with ID {package_id} not found")

    # Get location
    location = db.query(TransportLocation).filter(TransportLocation.id == location_id).first()
    if not location:
        raise ValueError(f"Transport location with ID {location_id} not found")

    # Calculate subtotal
    subtotal = Decimal(0)

    if package.base_bride_price and num_brides > 0:
        subtotal += package.base_bride_price * num_brides

    if package.base_maid_price and num_maids > 0:
        subtotal += package.base_maid_price * num_maids

    if package.base_mother_price and num_mothers > 0:
        subtotal += package.base_mother_price * num_mothers

    if package.base_other_price and num_others > 0:
        subtotal += package.base_other_price * num_others

    # Get transport cost
    transport_cost = location.transport_cost or Decimal(0)

    # Calculate total
    total_amount = subtotal + transport_cost

    return subtotal, transport_cost, total_amount


def create_booking(
    db: Session,
    booking_data: BookingCreate,
    user_id: Optional[UUID] = None
) -> Booking:
    """
    Create a new booking

    Args:
        db: Database session
        booking_data: Booking creation data
        user_id: User ID (optional, for authenticated users)

    Returns:
        Created booking

    Raises:
        ValueError: If validation fails or slot is not available
    """
    # Validate package exists and is active
    package = db.query(ServicePackage).filter(
        ServicePackage.id == booking_data.package_id
    ).first()

    if not package:
        raise ValueError(f"Service package with ID {booking_data.package_id} not found")

    if not package.is_active:
        raise ValueError(f"Service package '{package.name}' is not currently available")

    # Validate location exists and is active
    location = db.query(TransportLocation).filter(
        TransportLocation.id == booking_data.location_id
    ).first()

    if not location:
        raise ValueError(f"Transport location with ID {booking_data.location_id} not found")

    if not location.is_active:
        raise ValueError(f"Transport location '{location.location_name}' is not currently available")

    # Validate package rules (maid count)
    if package.max_maids is not None and booking_data.num_maids > package.max_maids:
        raise ValueError(
            f"Number of maids ({booking_data.num_maids}) exceeds maximum allowed "
            f"({package.max_maids}) for package '{package.name}'"
        )

    if package.min_maids is not None and booking_data.num_maids < package.min_maids:
        raise ValueError(
            f"Number of maids ({booking_data.num_maids}) is below minimum required "
            f"({package.min_maids}) for package '{package.name}'"
        )

    # Check availability
    is_available, reason = is_slot_available(
        db,
        booking_data.booking_date,
        booking_data.booking_time
    )

    if not is_available:
        raise ValueError(
            f"Selected time slot is not available. Reason: {reason}"
        )

    # Validate user or guest information
    if not user_id:
        # Guest booking - require guest information
        if not all([booking_data.guest_email, booking_data.guest_name, booking_data.guest_phone]):
            raise ValueError(
                "Guest bookings require email, name, and phone number"
            )

    # Calculate pricing
    subtotal, transport_cost, total_amount = calculate_booking_price(
        db=db,
        package_id=booking_data.package_id,
        location_id=booking_data.location_id,
        num_brides=booking_data.num_brides,
        num_maids=booking_data.num_maids,
        num_mothers=booking_data.num_mothers,
        num_others=booking_data.num_others
    )

    # Calculate 50% deposit
    deposit_amount = round(total_amount * Decimal('0.5'), 2)

    # Generate booking number
    booking_number = generate_booking_number(db)

    # Create booking
    booking = Booking(
        booking_number=booking_number,
        user_id=user_id,
        guest_email=booking_data.guest_email,
        guest_name=booking_data.guest_name,
        guest_phone=booking_data.guest_phone,
        package_id=booking_data.package_id,
        booking_date=booking_data.booking_date,
        booking_time=booking_data.booking_time,
        location_id=booking_data.location_id,
        num_brides=booking_data.num_brides,
        num_maids=booking_data.num_maids,
        num_mothers=booking_data.num_mothers,
        num_others=booking_data.num_others,
        wedding_theme=booking_data.wedding_theme,
        special_requests=booking_data.special_requests,
        subtotal=subtotal,
        transport_cost=transport_cost,
        total_amount=total_amount,
        deposit_amount=deposit_amount,
        status="pending"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    # TODO: Send confirmation email (implement email service)
    # send_booking_confirmation_email(booking)

    return booking
