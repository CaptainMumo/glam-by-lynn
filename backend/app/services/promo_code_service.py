"""Promo code service for business logic."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.order import PromoCode


def get_all_promo_codes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> Tuple[List[PromoCode], int]:
    """
    Get all promo codes with pagination and filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        search: Search by code or description

    Returns:
        Tuple of (promo codes list, total count)
    """
    query = db.query(PromoCode)

    # Apply filters
    if is_active is not None:
        query = query.filter(PromoCode.is_active == is_active)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                PromoCode.code.ilike(search_term),
                PromoCode.description.ilike(search_term),
            )
        )

    # Get total count
    total = query.count()

    # Order by creation date (newest first)
    query = query.order_by(PromoCode.created_at.desc())

    # Apply pagination
    promo_codes = query.offset(skip).limit(limit).all()

    return promo_codes, total


def get_promo_code_by_id(db: Session, promo_code_id: UUID) -> Optional[PromoCode]:
    """Get a single promo code by ID."""
    return db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()


def get_promo_code_by_code(db: Session, code: str) -> Optional[PromoCode]:
    """Get a promo code by its code string."""
    return db.query(PromoCode).filter(PromoCode.code == code.upper()).first()


def create_promo_code(
    db: Session,
    code: str,
    discount_type: str,
    discount_value: Decimal,
    description: Optional[str] = None,
    min_order_amount: Optional[Decimal] = None,
    max_discount_amount: Optional[Decimal] = None,
    usage_limit: Optional[int] = None,
    valid_from: Optional[datetime] = None,
    valid_until: Optional[datetime] = None,
    is_active: bool = True,
) -> PromoCode:
    """
    Create a new promo code.

    Args:
        db: Database session
        code: Promo code string (will be uppercased)
        discount_type: Type of discount ('percentage' or 'fixed')
        discount_value: Discount amount
        description: Optional description
        min_order_amount: Minimum order amount required
        max_discount_amount: Maximum discount cap
        usage_limit: Maximum number of uses
        valid_from: Start date for validity
        valid_until: End date for validity
        is_active: Whether the promo code is active

    Returns:
        Created promo code
    """
    promo_code = PromoCode(
        code=code.upper(),
        description=description,
        discount_type=discount_type,
        discount_value=discount_value,
        min_order_amount=min_order_amount,
        max_discount_amount=max_discount_amount,
        usage_limit=usage_limit,
        usage_count=0,
        valid_from=valid_from,
        valid_until=valid_until,
        is_active=is_active,
    )

    db.add(promo_code)
    db.commit()
    db.refresh(promo_code)

    return promo_code


def update_promo_code(
    db: Session,
    promo_code_id: UUID,
    code: Optional[str] = None,
    description: Optional[str] = None,
    discount_type: Optional[str] = None,
    discount_value: Optional[Decimal] = None,
    min_order_amount: Optional[Decimal] = None,
    max_discount_amount: Optional[Decimal] = None,
    usage_limit: Optional[int] = None,
    valid_from: Optional[datetime] = None,
    valid_until: Optional[datetime] = None,
    is_active: Optional[bool] = None,
) -> Optional[PromoCode]:
    """
    Update a promo code.

    Args:
        db: Database session
        promo_code_id: Promo code ID
        **kwargs: Fields to update

    Returns:
        Updated promo code or None if not found
    """
    promo_code = db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()

    if not promo_code:
        return None

    # Update fields if provided
    if code is not None:
        promo_code.code = code.upper()
    if description is not None:
        promo_code.description = description
    if discount_type is not None:
        promo_code.discount_type = discount_type
    if discount_value is not None:
        promo_code.discount_value = discount_value
    if min_order_amount is not None:
        promo_code.min_order_amount = min_order_amount
    if max_discount_amount is not None:
        promo_code.max_discount_amount = max_discount_amount
    if usage_limit is not None:
        promo_code.usage_limit = usage_limit
    if valid_from is not None:
        promo_code.valid_from = valid_from
    if valid_until is not None:
        promo_code.valid_until = valid_until
    if is_active is not None:
        promo_code.is_active = is_active

    db.commit()
    db.refresh(promo_code)

    return promo_code


def delete_promo_code(db: Session, promo_code_id: UUID) -> bool:
    """
    Delete a promo code.

    Args:
        db: Database session
        promo_code_id: Promo code ID

    Returns:
        True if deleted, False if not found
    """
    promo_code = db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()

    if not promo_code:
        return False

    db.delete(promo_code)
    db.commit()

    return True


def validate_promo_code(
    db: Session, code: str, order_amount: Decimal
) -> Tuple[bool, str, Optional[Decimal], Optional[PromoCode]]:
    """
    Validate a promo code and calculate discount.

    Args:
        db: Database session
        code: Promo code string
        order_amount: Order total amount

    Returns:
        Tuple of (is_valid, message, discount_amount, promo_code)
    """
    promo_code = get_promo_code_by_code(db, code)

    if not promo_code:
        return False, "Invalid promo code", None, None

    if not promo_code.is_active:
        return False, "This promo code is inactive", None, promo_code

    # Check expiration
    now = datetime.now(timezone.utc)
    if promo_code.valid_from and now < promo_code.valid_from:
        return False, "This promo code is not yet valid", None, promo_code

    if promo_code.valid_until and now > promo_code.valid_until:
        return False, "This promo code has expired", None, promo_code

    # Check usage limit
    if promo_code.usage_limit and promo_code.usage_count >= promo_code.usage_limit:
        return False, "This promo code has reached its usage limit", None, promo_code

    # Check minimum order amount
    if promo_code.min_order_amount and order_amount < promo_code.min_order_amount:
        return (
            False,
            f"Minimum order amount of {promo_code.min_order_amount} required",
            None,
            promo_code,
        )

    # Calculate discount
    if promo_code.discount_type == "percentage":
        discount = (order_amount * promo_code.discount_value) / 100
    else:  # fixed
        discount = promo_code.discount_value

    # Apply maximum discount cap
    if promo_code.max_discount_amount and discount > promo_code.max_discount_amount:
        discount = promo_code.max_discount_amount

    # Ensure discount doesn't exceed order amount
    if discount > order_amount:
        discount = order_amount

    return True, "Promo code applied successfully", discount, promo_code


def increment_usage(db: Session, promo_code_id: UUID) -> Optional[PromoCode]:
    """
    Increment usage count for a promo code.

    Args:
        db: Database session
        promo_code_id: Promo code ID

    Returns:
        Updated promo code or None if not found
    """
    promo_code = db.query(PromoCode).filter(PromoCode.id == promo_code_id).first()

    if not promo_code:
        return None

    promo_code.usage_count += 1
    db.commit()
    db.refresh(promo_code)

    return promo_code


def is_expired(promo_code: PromoCode) -> bool:
    """Check if a promo code is expired."""
    if not promo_code.valid_until:
        return False
    return datetime.now(timezone.utc) > promo_code.valid_until


def is_usage_exhausted(promo_code: PromoCode) -> bool:
    """Check if a promo code has exhausted its usage limit."""
    if not promo_code.usage_limit:
        return False
    return promo_code.usage_count >= promo_code.usage_limit
