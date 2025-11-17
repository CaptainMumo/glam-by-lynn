"""
Service Package API routes
Admin-only endpoints for service package management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import math

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.service_package import (
    ServicePackageCreate,
    ServicePackageUpdate,
    ServicePackageResponse,
    ServicePackageListResponse
)
from app.services import service_package_service

router = APIRouter(prefix="/admin/services", tags=["admin", "services"])


@router.get("/types", response_model=list[str])
async def list_package_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get list of unique package types

    **Admin only**

    Returns list of package types currently in use.
    """
    package_types = service_package_service.get_package_types(db)
    return package_types


@router.get("", response_model=ServicePackageListResponse)
async def list_packages(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    package_type: Optional[str] = Query(None, description="Filter by package type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get paginated list of service packages

    **Admin only**

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **package_type**: Filter by package type (bridal_large, bridal_small, bride_only, regular, classes)
    - **is_active**: Filter by active status
    - **search**: Search in name and description
    """
    skip = (page - 1) * page_size

    packages, total = service_package_service.get_packages(
        db=db,
        skip=skip,
        limit=page_size,
        package_type=package_type,
        is_active=is_active,
        search=search
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
async def get_package(
    package_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific service package by ID

    **Admin only**
    """
    package = service_package_service.get_package_by_id(db, package_id)

    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service package with ID {package_id} not found"
        )

    return package


@router.post("", response_model=ServicePackageResponse, status_code=status.HTTP_201_CREATED)
async def create_package(
    package_data: ServicePackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new service package

    **Admin only**

    Package types:
    - **bridal_large**: Large bridal party
    - **bridal_small**: Small bridal party
    - **bride_only**: Bride only
    - **regular**: Regular makeup
    - **classes**: Makeup classes

    Validation:
    - max_maids must be >= min_maids
    - All prices must be non-negative
    - duration_minutes must be positive
    """
    try:
        package = service_package_service.create_package(db, package_data)
        return package
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{package_id}", response_model=ServicePackageResponse)
async def update_package(
    package_id: UUID,
    package_data: ServicePackageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a service package

    **Admin only**

    Validates that max_maids >= min_maids after update.
    """
    try:
        package = service_package_service.update_package(db, package_id, package_data)

        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service package with ID {package_id} not found"
            )

        return package
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_package(
    package_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a service package

    **Admin only**

    Cannot delete a package that has associated bookings.
    Consider marking packages as inactive instead of deleting them.
    """
    try:
        deleted = service_package_service.delete_package(db, package_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service package with ID {package_id} not found"
            )

        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
