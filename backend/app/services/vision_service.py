"""Vision registration service for business logic."""
import csv
import io
from collections import defaultdict
from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.content import VisionRegistration


def create_vision_registration(
    db: Session,
    full_name: str,
    email: str,
    phone_number: str,
    location: Optional[str] = None,
    interested_in_salon: bool = False,
    interested_in_barbershop: bool = False,
    interested_in_spa: bool = False,
    interested_in_mobile_van: bool = False,
    additional_comments: Optional[str] = None,
) -> VisionRegistration:
    """
    Create a new vision registration.

    Args:
        db: Database session
        full_name: Full name
        email: Email address
        phone_number: Phone number
        location: Location (optional)
        interested_in_salon: Interest in salon services
        interested_in_barbershop: Interest in barbershop services
        interested_in_spa: Interest in spa services
        interested_in_mobile_van: Interest in mobile van services
        additional_comments: Additional comments (optional)

    Returns:
        Created vision registration

    Raises:
        ValueError: If no interest selected or email already registered
    """
    # Validate at least one interest is selected
    if not any([interested_in_salon, interested_in_barbershop, interested_in_spa, interested_in_mobile_van]):
        raise ValueError("Please select at least one area of interest")

    # Check if email already registered
    existing = db.query(VisionRegistration).filter(VisionRegistration.email == email.lower()).first()
    if existing:
        raise ValueError("This email has already registered interest")

    # Create registration
    registration = VisionRegistration(
        full_name=full_name,
        email=email.lower(),
        phone_number=phone_number,
        location=location,
        interested_in_salon=interested_in_salon,
        interested_in_barbershop=interested_in_barbershop,
        interested_in_spa=interested_in_spa,
        interested_in_mobile_van=interested_in_mobile_van,
        additional_comments=additional_comments,
    )

    db.add(registration)
    db.commit()
    db.refresh(registration)

    return registration


def get_vision_registration_by_id(db: Session, registration_id: UUID) -> Optional[VisionRegistration]:
    """Get a vision registration by ID."""
    return db.query(VisionRegistration).filter(VisionRegistration.id == registration_id).first()


def get_vision_registration_by_email(db: Session, email: str) -> Optional[VisionRegistration]:
    """Get a vision registration by email."""
    return db.query(VisionRegistration).filter(VisionRegistration.email == email.lower()).first()


def get_all_vision_registrations(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    service_filter: Optional[str] = None,
    location_filter: Optional[str] = None,
) -> Tuple[list[VisionRegistration], int]:
    """
    Get all vision registrations with pagination and filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        service_filter: Filter by service interest (salon, barbershop, spa, mobile_van)
        location_filter: Filter by location (partial match)

    Returns:
        Tuple of (registrations list, total count)
    """
    query = db.query(VisionRegistration)

    # Apply service filter
    if service_filter:
        if service_filter == "salon":
            query = query.filter(VisionRegistration.interested_in_salon == True)
        elif service_filter == "barbershop":
            query = query.filter(VisionRegistration.interested_in_barbershop == True)
        elif service_filter == "spa":
            query = query.filter(VisionRegistration.interested_in_spa == True)
        elif service_filter == "mobile_van":
            query = query.filter(VisionRegistration.interested_in_mobile_van == True)

    # Apply location filter
    if location_filter:
        query = query.filter(VisionRegistration.location.ilike(f"%{location_filter}%"))

    total = query.count()
    registrations = query.order_by(VisionRegistration.created_at.desc()).offset(skip).limit(limit).all()

    return registrations, total


def get_vision_analytics(db: Session) -> dict:
    """
    Calculate vision registration analytics.

    Returns:
        Dictionary with analytics data including service interests,
        location distribution, and monthly registrations
    """
    # Get all registrations
    all_registrations = db.query(VisionRegistration).all()
    total = len(all_registrations)

    if total == 0:
        return {
            "total_registrations": 0,
            "service_interests": [],
            "location_distribution": [],
            "registrations_by_month": {},
        }

    # Calculate service interests
    salon_count = sum(1 for r in all_registrations if r.interested_in_salon)
    barbershop_count = sum(1 for r in all_registrations if r.interested_in_barbershop)
    spa_count = sum(1 for r in all_registrations if r.interested_in_spa)
    mobile_van_count = sum(1 for r in all_registrations if r.interested_in_mobile_van)

    service_interests = [
        {
            "service_name": "Full-service Salon",
            "count": salon_count,
            "percentage": round((salon_count / total) * 100, 1),
        },
        {
            "service_name": "Barbershop Services",
            "count": barbershop_count,
            "percentage": round((barbershop_count / total) * 100, 1),
        },
        {
            "service_name": "Spa Treatments",
            "count": spa_count,
            "percentage": round((spa_count / total) * 100, 1),
        },
        {
            "service_name": "Mobile Beauty Van",
            "count": mobile_van_count,
            "percentage": round((mobile_van_count / total) * 100, 1),
        },
    ]

    # Calculate location distribution
    location_counts = defaultdict(int)
    for registration in all_registrations:
        if registration.location:
            location_counts[registration.location] += 1
        else:
            location_counts["Not specified"] += 1

    location_distribution = [
        {"location": location, "count": count}
        for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    # Calculate registrations by month
    month_counts = defaultdict(int)
    for registration in all_registrations:
        month_key = registration.created_at.strftime("%Y-%m")
        month_counts[month_key] += 1

    return {
        "total_registrations": total,
        "service_interests": service_interests,
        "location_distribution": location_distribution,
        "registrations_by_month": dict(sorted(month_counts.items())),
    }


def export_vision_registrations_csv(db: Session) -> str:
    """
    Export all vision registrations to CSV format.

    Returns:
        CSV content as string
    """
    registrations = db.query(VisionRegistration).order_by(VisionRegistration.created_at.desc()).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "ID",
        "Full Name",
        "Email",
        "Phone Number",
        "Location",
        "Interested in Salon",
        "Interested in Barbershop",
        "Interested in Spa",
        "Interested in Mobile Van",
        "Additional Comments",
        "Created At",
    ])

    # Write data
    for registration in registrations:
        writer.writerow([
            str(registration.id),
            registration.full_name,
            registration.email,
            registration.phone_number,
            registration.location or "",
            "Yes" if registration.interested_in_salon else "No",
            "Yes" if registration.interested_in_barbershop else "No",
            "Yes" if registration.interested_in_spa else "No",
            "Yes" if registration.interested_in_mobile_van else "No",
            registration.additional_comments or "",
            registration.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return output.getvalue()
