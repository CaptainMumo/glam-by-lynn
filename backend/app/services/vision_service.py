"""Vision registration service for business logic."""
from typing import Optional
from uuid import UUID

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
