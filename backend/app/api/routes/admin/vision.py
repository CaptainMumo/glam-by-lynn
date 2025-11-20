"""Admin vision registration routes."""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.vision import VisionAnalyticsResponse, VisionRegistrationListResponse
from app.services import vision_service

router = APIRouter(tags=["Admin Vision"])


@router.get(
    "/admin/vision/registrations",
    response_model=VisionRegistrationListResponse,
    summary="Get all vision registrations (admin only)",
)
def get_vision_registrations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    service: Optional[str] = Query(
        None,
        description="Filter by service interest (salon, barbershop, spa, mobile_van)",
    ),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get all vision registrations with pagination and filters.

    Only accessible by admin users.

    **Query Parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 20, max: 100)
    - service: Filter by service interest (salon, barbershop, spa, mobile_van)
    - location: Filter by location (partial match, case-insensitive)

    **Returns:**
    - List of vision registrations with pagination info
    """
    registrations, total = vision_service.get_all_vision_registrations(
        db=db,
        skip=skip,
        limit=limit,
        service_filter=service,
        location_filter=location,
    )

    return VisionRegistrationListResponse(
        registrations=registrations,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/admin/vision/analytics",
    response_model=VisionAnalyticsResponse,
    summary="Get vision registration analytics (admin only)",
)
def get_vision_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get vision registration analytics and statistics.

    Only accessible by admin users.

    **Returns:**
    - Total registration count
    - Service interest breakdown with percentages
    - Geographic distribution
    - Monthly registration timeline
    """
    analytics = vision_service.get_vision_analytics(db=db)
    return analytics


@router.get(
    "/admin/vision/export",
    summary="Export vision registrations to CSV (admin only)",
)
def export_vision_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Export all vision registrations to CSV format.

    Only accessible by admin users.

    **Returns:**
    - CSV file download with all vision registration data
    """
    csv_content = vision_service.export_vision_registrations_csv(db=db)

    # Return as downloadable CSV file
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=vision_registrations.csv"
        },
    )
