"""Wishlist service for business logic."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.order import Wishlist
from app.models.product import Product


def get_user_wishlist(db: Session, user_id: UUID) -> List[Wishlist]:
    """
    Get user's wishlist with product details.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of wishlist items with products
    """
    wishlist_items = (
        db.query(Wishlist)
        .options(joinedload(Wishlist.product))
        .filter(Wishlist.user_id == user_id)
        .order_by(Wishlist.created_at.desc())
        .all()
    )

    return wishlist_items


def add_to_wishlist(db: Session, user_id: UUID, product_id: UUID) -> Wishlist:
    """
    Add product to user's wishlist.

    Args:
        db: Database session
        user_id: User ID
        product_id: Product ID

    Returns:
        Wishlist item

    Raises:
        ValueError: If product doesn't exist, not active, or already in wishlist
    """
    # Check if product exists and is active
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError("Product not found")

    if not product.is_active:
        raise ValueError("Product is not available")

    # Check if already in wishlist
    existing = (
        db.query(Wishlist)
        .filter(and_(Wishlist.user_id == user_id, Wishlist.product_id == product_id))
        .first()
    )

    if existing:
        raise ValueError("Product is already in your wishlist")

    # Add to wishlist
    wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)

    # Reload with product details
    wishlist_item = (
        db.query(Wishlist)
        .options(joinedload(Wishlist.product))
        .filter(Wishlist.id == wishlist_item.id)
        .first()
    )

    return wishlist_item


def remove_from_wishlist(db: Session, user_id: UUID, product_id: UUID) -> bool:
    """
    Remove product from user's wishlist.

    Args:
        db: Database session
        user_id: User ID
        product_id: Product ID

    Returns:
        True if removed, False if not found
    """
    wishlist_item = (
        db.query(Wishlist)
        .filter(and_(Wishlist.user_id == user_id, Wishlist.product_id == product_id))
        .first()
    )

    if not wishlist_item:
        return False

    db.delete(wishlist_item)
    db.commit()
    return True


def is_in_wishlist(db: Session, user_id: UUID, product_id: UUID) -> bool:
    """
    Check if product is in user's wishlist.

    Args:
        db: Database session
        user_id: User ID
        product_id: Product ID

    Returns:
        True if in wishlist, False otherwise
    """
    exists = (
        db.query(Wishlist)
        .filter(and_(Wishlist.user_id == user_id, Wishlist.product_id == product_id))
        .first()
    )

    return exists is not None
