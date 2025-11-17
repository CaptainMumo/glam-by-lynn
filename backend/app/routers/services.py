"""
Public Service Package API routes
Publicly accessible endpoints for customers to view service packages
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import math

from app.core.database import get_db
from app.schemas.service_package import (
    ServicePackageResponse,
    ServicePackageListResponse
)
from app.services import service_package_service

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=ServicePackageListResponse)
async def list_active_packages(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    package_type: Optional[str] = Query(None, description="Filter by package type"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of active service packages (public endpoint)

    **Publicly accessible - No authentication required**

    Only returns active packages ordered by display_order.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **package_type**: Filter by package type (bridal_large, bridal_small, bride_only, regular, classes)

    Returns:
    - Service packages with pricing breakdown
    - Pagination metadata
    """
    skip = (page - 1) * page_size

    # Only show active packages to public
    packages, total = service_package_service.get_packages(
        db=db,
        skip=skip,
        limit=page_size,
        package_type=package_type,
        is_active=True  # Force only active packages
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ServicePackageListResponse(
        items=packages,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{package_id}", response_model=ServicePackageResponse)
async def get_package_details(
    package_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific service package by ID (public endpoint)

    **Publicly accessible - No authentication required**

    Returns:
    - Full package details including pricing breakdown
    - Package description and features
    - Duration and other metadata

    Raises:
    - 404: If package not found or is inactive
    """
    package = service_package_service.get_package_by_id(db, package_id)

    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service package with ID {package_id} not found"
        )

    # Only return active packages to public
    if not package.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service package with ID {package_id} not found"
        )

    return package
