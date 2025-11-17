"""
Service Package service
Business logic for service package management
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.service import ServicePackage
from app.schemas.service_package import ServicePackageCreate, ServicePackageUpdate


def get_package_by_id(db: Session, package_id: UUID) -> Optional[ServicePackage]:
    """Get service package by ID"""
    return db.query(ServicePackage).filter(ServicePackage.id == package_id).first()


def get_package_by_name(db: Session, name: str) -> Optional[ServicePackage]:
    """Get service package by name"""
    return db.query(ServicePackage).filter(ServicePackage.name == name).first()


def get_packages(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    package_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> tuple[list[ServicePackage], int]:
    """
    Get list of service packages with pagination and filters

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        package_type: Filter by package type
        is_active: Filter by active status
        search: Search in name and description

    Returns:
        Tuple of (packages list, total count)
    """
    query = db.query(ServicePackage)

    # Apply filters
    if package_type:
        query = query.filter(ServicePackage.package_type == package_type.lower())

    if is_active is not None:
        query = query.filter(ServicePackage.is_active == is_active)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                ServicePackage.name.ilike(search_term),
                ServicePackage.description.ilike(search_term)
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    packages = query.order_by(
        ServicePackage.display_order,
        ServicePackage.name
    ).offset(skip).limit(limit).all()

    return packages, total


def get_package_types(db: Session) -> list[str]:
    """
    Get list of unique package types

    Args:
        db: Database session

    Returns:
        List of package types
    """
    result = db.query(ServicePackage.package_type).distinct().all()
    return [row[0] for row in result]


def create_package(db: Session, package_data: ServicePackageCreate) -> ServicePackage:
    """
    Create a new service package

    Args:
        db: Database session
        package_data: Package creation data

    Returns:
        Created service package

    Raises:
        ValueError: If package with same name already exists or validation fails
    """
    # Check if package with same name exists
    existing_package = get_package_by_name(db, package_data.name)
    if existing_package:
        raise ValueError(f"Service package with name '{package_data.name}' already exists")

    # Additional validation for maid range
    if package_data.max_maids is not None and package_data.min_maids is not None:
        if package_data.max_maids < package_data.min_maids:
            raise ValueError("max_maids must be greater than or equal to min_maids")

    # Create package
    package = ServicePackage(
        package_type=package_data.package_type.lower(),
        name=package_data.name,
        description=package_data.description,
        base_bride_price=package_data.base_bride_price,
        base_maid_price=package_data.base_maid_price,
        base_mother_price=package_data.base_mother_price,
        base_other_price=package_data.base_other_price,
        max_maids=package_data.max_maids,
        min_maids=package_data.min_maids,
        includes_facial=package_data.includes_facial,
        duration_minutes=package_data.duration_minutes,
        is_active=package_data.is_active,
        display_order=package_data.display_order
    )

    db.add(package)
    db.commit()
    db.refresh(package)

    return package


def update_package(
    db: Session,
    package_id: UUID,
    package_data: ServicePackageUpdate
) -> Optional[ServicePackage]:
    """
    Update a service package

    Args:
        db: Database session
        package_id: Package ID to update
        package_data: Package update data

    Returns:
        Updated service package or None if not found

    Raises:
        ValueError: If new name conflicts with existing package or validation fails
    """
    package = get_package_by_id(db, package_id)
    if not package:
        return None

    # Check if new name conflicts with another package
    if package_data.name and package_data.name != package.name:
        existing_package = get_package_by_name(db, package_data.name)
        if existing_package and existing_package.id != package_id:
            raise ValueError(f"Service package with name '{package_data.name}' already exists")
        package.name = package_data.name

    # Update fields if provided
    if package_data.package_type is not None:
        package.package_type = package_data.package_type.lower()

    if package_data.description is not None:
        package.description = package_data.description

    if package_data.base_bride_price is not None:
        package.base_bride_price = package_data.base_bride_price

    if package_data.base_maid_price is not None:
        package.base_maid_price = package_data.base_maid_price

    if package_data.base_mother_price is not None:
        package.base_mother_price = package_data.base_mother_price

    if package_data.base_other_price is not None:
        package.base_other_price = package_data.base_other_price

    if package_data.max_maids is not None:
        package.max_maids = package_data.max_maids

    if package_data.min_maids is not None:
        package.min_maids = package_data.min_maids

    # Validate maid range after updates
    if package.max_maids is not None and package.min_maids is not None:
        if package.max_maids < package.min_maids:
            raise ValueError("max_maids must be greater than or equal to min_maids")

    if package_data.includes_facial is not None:
        package.includes_facial = package_data.includes_facial

    if package_data.duration_minutes is not None:
        package.duration_minutes = package_data.duration_minutes

    if package_data.is_active is not None:
        package.is_active = package_data.is_active

    if package_data.display_order is not None:
        package.display_order = package_data.display_order

    db.commit()
    db.refresh(package)

    return package


def delete_package(db: Session, package_id: UUID) -> bool:
    """
    Delete a service package

    Args:
        db: Database session
        package_id: Package ID to delete

    Returns:
        True if deleted, False if not found

    Raises:
        ValueError: If package has associated bookings
    """
    package = get_package_by_id(db, package_id)
    if not package:
        return False

    # Check if package has bookings
    if package.bookings.count() > 0:
        raise ValueError(
            f"Cannot delete service package '{package.name}' because it has associated bookings. "
            "Consider marking it as inactive instead."
        )

    db.delete(package)
    db.commit()

    return True
