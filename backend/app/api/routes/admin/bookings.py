"""Admin booking management API endpoints."""
from datetime import date as date_type
from typing import Optional
from uuid import UUID
import math
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.booking import BookingListResponse, BookingResponse
from app.schemas.admin_booking import (
    AdminBookingUpdate,
    AdminBookingStatusUpdate,
    AdminBookingDepositUpdate,
)
from app.services import booking_service

router = APIRouter(prefix="/admin/bookings", tags=["admin", "bookings"])


@router.get("", response_model=BookingListResponse)
def list_all_bookings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    booking_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    start_date: Optional[date_type] = Query(None, alias="startDate", description="Filter by booking date >= start_date"),
    end_date: Optional[date_type] = Query(None, alias="endDate", description="Filter by booking date <= end_date"),
    location_id: Optional[UUID] = Query(None, alias="locationId", description="Filter by location ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get list of all bookings with filters (admin only).

    **Authentication required - Admin only**

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status**: Filter by booking status (optional)
    - **startDate**: Filter by booking date >= start_date (optional)
    - **endDate**: Filter by booking date <= end_date (optional)
    - **locationId**: Filter by location ID (optional)

    Returns:
    - List of all bookings with full details
    - Pagination metadata
    """
    if end_date and start_date and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be after start_date"
        )

    skip = (page - 1) * page_size

    bookings, total = booking_service.get_all_bookings(
        db=db,
        skip=skip,
        limit=page_size,
        status=booking_status,
        start_date=start_date,
        end_date=end_date,
        location_id=location_id
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return BookingListResponse(
        items=bookings,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get specific booking details (admin only).

    **Authentication required - Admin only**

    Returns detailed information for any booking (bypasses ownership check).
    """
    booking = booking_service.get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )

    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: UUID,
    booking_data: AdminBookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Update a booking (admin only).

    **Authentication required - Admin only**

    Allows admin to update booking details including:
    - Date and time (with availability check)
    - Location (with pricing recalculation)
    - Participant counts (with pricing recalculation)
    - Wedding theme and special requests
    - Admin notes

    Raises:
    - 404: Booking not found
    - 400: Validation error (invalid location, unavailable slot, etc.)
    """
    try:
        booking = booking_service.admin_update_booking(
            db=db,
            booking_id=booking_id,
            booking_date=booking_data.booking_date,
            booking_time=booking_data.booking_time,
            location_id=booking_data.location_id,
            num_brides=booking_data.num_brides,
            num_maids=booking_data.num_maids,
            num_mothers=booking_data.num_mothers,
            num_others=booking_data.num_others,
            wedding_theme=booking_data.wedding_theme,
            special_requests=booking_data.special_requests,
            admin_notes=booking_data.admin_notes,
        )
        return booking
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )


@router.put("/{booking_id}/deposit", response_model=BookingResponse)
def mark_deposit_paid(
    booking_id: UUID,
    deposit_data: AdminBookingDepositUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Mark deposit as paid/unpaid (admin only).

    **Authentication required - Admin only**

    Effects:
    - Updates deposit_paid flag
    - Sets deposit_paid_at timestamp if marked as paid
    - Updates status to "deposit_paid" if currently "pending" and marking as paid
    - Adds admin note with timestamp

    Raises:
    - 404: Booking not found
    """
    try:
        booking = booking_service.admin_mark_deposit_paid(
            db=db,
            booking_id=booking_id,
            deposit_paid=deposit_data.deposit_paid,
            admin_notes=deposit_data.admin_notes
        )
        return booking
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: UUID,
    status_data: AdminBookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Update booking status (admin only).

    **Authentication required - Admin only**

    Valid statuses:
    - pending: Awaiting confirmation
    - confirmed: Confirmed booking
    - deposit_paid: Deposit received
    - completed: Service completed
    - cancelled: Booking cancelled

    Adds admin note with status change timestamp.

    Raises:
    - 404: Booking not found
    - 400: Invalid status value
    """
    try:
        booking = booking_service.admin_update_booking_status(
            db=db,
            booking_id=booking_id,
            status=status_data.status,
            admin_notes=status_data.admin_notes
        )
        return booking
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: UUID,
    admin_notes: Optional[str] = Query(None, description="Admin notes for cancellation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Cancel a booking (admin only).

    **Authentication required - Admin only**

    Admin cancellation bypasses:
    - 24-hour cancellation policy
    - Ownership check
    - Completed booking restriction

    Effects:
    - Changes status to "cancelled"
    - Frees calendar slot
    - Adds cancellation note with timestamp

    Raises:
    - 404: Booking not found
    - 400: Booking already cancelled
    """
    try:
        booking_service.admin_cancel_booking(
            db=db,
            booking_id=booking_id,
            admin_notes=admin_notes
        )
        return None
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )


@router.get("/export/csv", response_class=StreamingResponse)
def export_bookings_csv(
    booking_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    start_date: Optional[date_type] = Query(None, alias="startDate", description="Filter by booking date >= start_date"),
    end_date: Optional[date_type] = Query(None, alias="endDate", description="Filter by booking date <= end_date"),
    location_id: Optional[UUID] = Query(None, alias="locationId", description="Filter by location ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Export bookings to CSV (admin only).

    **Authentication required - Admin only**

    Exports all bookings matching the filters to a CSV file.

    Query parameters (same as list endpoint):
    - **status**: Filter by booking status (optional)
    - **startDate**: Filter by booking date >= start_date (optional)
    - **endDate**: Filter by booking date <= end_date (optional)
    - **locationId**: Filter by location ID (optional)

    Returns:
    - CSV file download with booking data
    """
    # Get all bookings (no pagination for export)
    bookings, _ = booking_service.get_all_bookings(
        db=db,
        skip=0,
        limit=10000,  # High limit for export
        status=booking_status,
        start_date=start_date,
        end_date=end_date,
        location_id=location_id
    )

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Booking Number",
        "Status",
        "Date",
        "Time",
        "Customer Name",
        "Customer Email",
        "Customer Phone",
        "Package ID",
        "Location ID",
        "Num Brides",
        "Num Maids",
        "Num Mothers",
        "Num Others",
        "Wedding Theme",
        "Subtotal",
        "Transport Cost",
        "Total Amount",
        "Deposit Amount",
        "Deposit Paid",
        "Deposit Paid At",
        "Admin Notes",
        "Created At",
    ])

    # Write booking data
    for booking in bookings:
        customer_name = booking.guest_name if booking.guest_name else f"User ID: {booking.user_id}"
        customer_email = booking.guest_email if booking.guest_email else "N/A"
        customer_phone = booking.guest_phone if booking.guest_phone else "N/A"

        writer.writerow([
            booking.booking_number,
            booking.status,
            booking.booking_date,
            booking.booking_time,
            customer_name,
            customer_email,
            customer_phone,
            str(booking.package_id),
            str(booking.location_id),
            booking.num_brides,
            booking.num_maids,
            booking.num_mothers,
            booking.num_others,
            booking.wedding_theme or "",
            float(booking.subtotal),
            float(booking.transport_cost),
            float(booking.total_amount),
            float(booking.deposit_amount) if booking.deposit_amount else 0,
            booking.deposit_paid,
            booking.deposit_paid_at.isoformat() if booking.deposit_paid_at else "",
            booking.admin_notes or "",
            booking.created_at.isoformat(),
        ])

    # Prepare response
    output.seek(0)
    filename = f"bookings_export_{date_type.today().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
