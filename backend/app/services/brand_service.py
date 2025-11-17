"""
Brand service
Business logic for brand management
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Brand
from app.schemas.brand import BrandCreate, BrandUpdate, slugify


def get_brand_by_id(db: Session, brand_id: UUID) -> Optional[Brand]:
    """Get brand by ID"""
    return db.query(Brand).filter(Brand.id == brand_id).first()


def get_brand_by_slug(db: Session, slug: str) -> Optional[Brand]:
    """Get brand by slug"""
    return db.query(Brand).filter(Brand.slug == slug).first()


def get_brand_by_name(db: Session, name: str) -> Optional[Brand]:
    """Get brand by name"""
    return db.query(Brand).filter(Brand.name == name).first()


def get_brands(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> tuple[list[Brand], int]:
    """
    Get list of brands with pagination and filters

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        search: Search in name and description

    Returns:
        Tuple of (brands list, total count)
    """
    query = db.query(Brand)

    # Apply filters
    if is_active is not None:
        query = query.filter(Brand.is_active == is_active)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Brand.name.ilike(search_term),
                Brand.description.ilike(search_term)
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination
    brands = query.order_by(Brand.name).offset(skip).limit(limit).all()

    return brands, total


def create_brand(db: Session, brand_data: BrandCreate) -> Brand:
    """
    Create a new brand

    Args:
        db: Database session
        brand_data: Brand creation data

    Returns:
        Created brand

    Raises:
        ValueError: If brand with same name already exists
    """
    # Check if brand with same name exists
    existing_brand = get_brand_by_name(db, brand_data.name)
    if existing_brand:
        raise ValueError(f"Brand with name '{brand_data.name}' already exists")

    # Generate slug from name
    slug = slugify(brand_data.name)

    # Check if slug already exists (shouldn't happen if name is unique, but just in case)
    slug_counter = 1
    original_slug = slug
    while get_brand_by_slug(db, slug):
        slug = f"{original_slug}-{slug_counter}"
        slug_counter += 1

    # Create brand
    brand = Brand(
        name=brand_data.name,
        slug=slug,
        description=brand_data.description,
        logo_url=brand_data.logo_url,
        is_active=brand_data.is_active
    )

    db.add(brand)
    db.commit()
    db.refresh(brand)

    return brand


def update_brand(
    db: Session,
    brand_id: UUID,
    brand_data: BrandUpdate
) -> Optional[Brand]:
    """
    Update a brand

    Args:
        db: Database session
        brand_id: Brand ID to update
        brand_data: Brand update data

    Returns:
        Updated brand or None if not found

    Raises:
        ValueError: If new name conflicts with existing brand
    """
    brand = get_brand_by_id(db, brand_id)
    if not brand:
        return None

    # Check if new name conflicts with another brand
    if brand_data.name and brand_data.name != brand.name:
        existing_brand = get_brand_by_name(db, brand_data.name)
        if existing_brand and existing_brand.id != brand_id:
            raise ValueError(f"Brand with name '{brand_data.name}' already exists")

        # Update name and regenerate slug
        brand.name = brand_data.name
        brand.slug = slugify(brand_data.name)

    # Update other fields if provided
    if brand_data.description is not None:
        brand.description = brand_data.description

    if brand_data.logo_url is not None:
        brand.logo_url = brand_data.logo_url

    if brand_data.is_active is not None:
        brand.is_active = brand_data.is_active

    db.commit()
    db.refresh(brand)

    return brand


def delete_brand(db: Session, brand_id: UUID) -> bool:
    """
    Delete a brand

    Args:
        db: Database session
        brand_id: Brand ID to delete

    Returns:
        True if deleted, False if not found

    Raises:
        ValueError: If brand has associated products
    """
    brand = get_brand_by_id(db, brand_id)
    if not brand:
        return False

    # Check if brand has products
    if brand.products.count() > 0:
        raise ValueError(
            f"Cannot delete brand '{brand.name}' because it has associated products. "
            "Please delete or reassign products first."
        )

    db.delete(brand)
    db.commit()

    return True
