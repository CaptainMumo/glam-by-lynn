"""Admin activity log routes."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.activity_log import (
    ActivityLogListResponse,
    ActivityLogResponse,
    ActivitySummaryResponse,
)
from app.services import activity_log_service

router = APIRouter(tags=["Admin Activity Logs"])


@router.get(
    "/admin/activity-logs",
    response_model=ActivityLogListResponse,
    summary="Get admin activity logs (admin only)",
)
def get_activity_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    admin_user_id: Optional[UUID] = Query(None, alias="adminUserId", description="Filter by admin user ID"),
    action: Optional[str] = Query(None, description="Filter by action (partial match)"),
    entity_type: Optional[str] = Query(None, alias="entityType", description="Filter by entity type"),
    start_date: Optional[datetime] = Query(None, alias="startDate", description="Filter from date"),
    end_date: Optional[datetime] = Query(None, alias="endDate", description="Filter to date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get admin activity logs with pagination and filters.

    Only accessible by admin users.

    **Query Parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 50, max: 100)
    - adminUserId: Filter by specific admin user
    - action: Filter by action type (partial match, case-insensitive)
    - entityType: Filter by entity type (exact match)
    - startDate: Filter activities from this date (ISO format)
    - endDate: Filter activities up to this date (ISO format)

    **Returns:**
    - List of activity logs with pagination info
    - Each log includes admin user summary, action details, and timestamp
    """
    logs, total = activity_log_service.get_activity_logs(
        db=db,
        skip=skip,
        limit=limit,
        admin_user_id=admin_user_id,
        action=action,
        entity_type=entity_type,
        start_date=start_date,
        end_date=end_date,
    )

    # Enrich logs with admin user details
    enriched_logs = []
    for log in logs:
        log_data = ActivityLogResponse.model_validate(log)
        # Add admin user summary
        if log.admin_user:
            from app.schemas.activity_log import AdminUserSummary

            log_data.admin_user = AdminUserSummary.model_validate(log.admin_user)
        enriched_logs.append(log_data)

    return ActivityLogListResponse(
        logs=enriched_logs,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/admin/activity-logs/{log_id}",
    response_model=ActivityLogResponse,
    summary="Get specific activity log (admin only)",
)
def get_activity_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get a specific activity log by ID.

    Only accessible by admin users.

    **Returns:**
    - Activity log details with admin user summary
    """
    log = activity_log_service.get_activity_log_by_id(db=db, log_id=log_id)

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found",
        )

    log_data = ActivityLogResponse.model_validate(log)
    if log.admin_user:
        from app.schemas.activity_log import AdminUserSummary

        log_data.admin_user = AdminUserSummary.model_validate(log.admin_user)

    return log_data


@router.get(
    "/admin/activity-logs/summary/{admin_user_id}",
    response_model=ActivitySummaryResponse,
    summary="Get activity summary for admin user (admin only)",
)
def get_user_activity_summary(
    admin_user_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get activity summary for a specific admin user.

    Only accessible by admin users.

    **Query Parameters:**
    - days: Number of days to look back (default: 30, max: 365)

    **Returns:**
    - Total action count for the period
    - Breakdown by action type
    - Breakdown by entity type
    """
    summary = activity_log_service.get_user_activity_summary(
        db=db,
        admin_user_id=admin_user_id,
        days=days,
    )

    return summary
