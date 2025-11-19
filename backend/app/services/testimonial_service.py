"""Testimonial service for business logic."""
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.content import Testimonial


def get_approved_testimonials(
    db: Session,
    featured_only: bool = False,
    related_service_id: Optional[UUID] = None,
    related_product_id: Optional[UUID] = None,
) -> List[Testimonial]:
    """
    Get approved testimonials with optional filters.

    Args:
        db: Database session
        featured_only: Return only featured testimonials
        related_service_id: Filter by service package ID
        related_product_id: Filter by product ID

    Returns:
        List of approved testimonials
    """
    # Build base query - only approved testimonials
    query = db.query(Testimonial).filter(Testimonial.is_approved == True)

    # Apply filters
    if featured_only:
        query = query.filter(Testimonial.is_featured == True)

    if related_service_id:
        query = query.filter(Testimonial.related_service_id == related_service_id)

    if related_product_id:
        query = query.filter(Testimonial.related_product_id == related_product_id)

    # Order by featured status, display order, and creation date
    query = query.order_by(
        Testimonial.is_featured.desc(),
        Testimonial.display_order.asc(),
        Testimonial.created_at.desc(),
    )

    return query.all()


def get_testimonial_by_id(db: Session, testimonial_id: UUID) -> Optional[Testimonial]:
    """Get a single approved testimonial by ID."""
    return (
        db.query(Testimonial)
        .filter(
            Testimonial.id == testimonial_id,
            Testimonial.is_approved == True,
        )
        .first()
    )


# Admin functions

def admin_get_all_testimonials(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_approved: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    related_service_id: Optional[UUID] = None,
    related_product_id: Optional[UUID] = None,
) -> Tuple[List[Testimonial], int]:
    """
    Get all testimonials (including unapproved) with pagination and filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_approved: Filter by approval status
        is_featured: Filter by featured status
        related_service_id: Filter by service package ID
        related_product_id: Filter by product ID

    Returns:
        Tuple of (testimonials list, total count)
    """
    query = db.query(Testimonial)

    # Apply filters
    if is_approved is not None:
        query = query.filter(Testimonial.is_approved == is_approved)

    if is_featured is not None:
        query = query.filter(Testimonial.is_featured == is_featured)

    if related_service_id:
        query = query.filter(Testimonial.related_service_id == related_service_id)

    if related_product_id:
        query = query.filter(Testimonial.related_product_id == related_product_id)

    # Get total count
    total = query.count()

    # Order by creation date (newest first)
    query = query.order_by(Testimonial.created_at.desc())

    # Apply pagination
    testimonials = query.offset(skip).limit(limit).all()

    return testimonials, total


def admin_get_testimonial_by_id(db: Session, testimonial_id: UUID) -> Optional[Testimonial]:
    """Get a single testimonial by ID (no approval filter)."""
    return db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()


def create_testimonial(
    db: Session,
    customer_name: str,
    testimonial_text: str,
    rating: int,
    customer_photo_url: Optional[str] = None,
    location: Optional[str] = None,
    related_service_id: Optional[UUID] = None,
    related_product_id: Optional[UUID] = None,
    is_featured: bool = False,
    is_approved: bool = True,
    display_order: int = 0,
) -> Testimonial:
    """
    Create a new testimonial.

    Args:
        db: Database session
        customer_name: Customer's name
        testimonial_text: Testimonial content
        rating: Rating (1-5)
        customer_photo_url: Optional photo URL
        location: Optional location
        related_service_id: Optional service package ID
        related_product_id: Optional product ID
        is_featured: Whether testimonial is featured
        is_approved: Whether testimonial is approved
        display_order: Display order

    Returns:
        Created testimonial
    """
    testimonial = Testimonial(
        customer_name=customer_name,
        customer_photo_url=customer_photo_url,
        location=location,
        rating=rating,
        testimonial_text=testimonial_text,
        related_service_id=related_service_id,
        related_product_id=related_product_id,
        is_featured=is_featured,
        is_approved=is_approved,
        display_order=display_order,
    )

    db.add(testimonial)
    db.commit()
    db.refresh(testimonial)

    return testimonial


def update_testimonial(
    db: Session,
    testimonial_id: UUID,
    customer_name: Optional[str] = None,
    customer_photo_url: Optional[str] = None,
    location: Optional[str] = None,
    rating: Optional[int] = None,
    testimonial_text: Optional[str] = None,
    related_service_id: Optional[UUID] = None,
    related_product_id: Optional[UUID] = None,
    is_featured: Optional[bool] = None,
    is_approved: Optional[bool] = None,
    display_order: Optional[int] = None,
) -> Optional[Testimonial]:
    """
    Update a testimonial.

    Args:
        db: Database session
        testimonial_id: Testimonial ID
        **kwargs: Fields to update

    Returns:
        Updated testimonial or None if not found
    """
    testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()

    if not testimonial:
        return None

    # Update fields if provided
    if customer_name is not None:
        testimonial.customer_name = customer_name
    if customer_photo_url is not None:
        testimonial.customer_photo_url = customer_photo_url
    if location is not None:
        testimonial.location = location
    if rating is not None:
        testimonial.rating = rating
    if testimonial_text is not None:
        testimonial.testimonial_text = testimonial_text
    if related_service_id is not None:
        testimonial.related_service_id = related_service_id
    if related_product_id is not None:
        testimonial.related_product_id = related_product_id
    if is_featured is not None:
        testimonial.is_featured = is_featured
    if is_approved is not None:
        testimonial.is_approved = is_approved
    if display_order is not None:
        testimonial.display_order = display_order

    db.commit()
    db.refresh(testimonial)

    return testimonial


def delete_testimonial(db: Session, testimonial_id: UUID) -> bool:
    """
    Delete a testimonial.

    Args:
        db: Database session
        testimonial_id: Testimonial ID

    Returns:
        True if deleted, False if not found
    """
    testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()

    if not testimonial:
        return False

    db.delete(testimonial)
    db.commit()

    return True
