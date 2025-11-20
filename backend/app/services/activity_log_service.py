"""Admin activity logging service for audit trail."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.content import AdminActivityLog


def log_admin_activity(
    db: Session,
    admin_user_id: UUID,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AdminActivityLog:
    """
    Log an admin action to the audit trail.

    Args:
        db: Database session
        admin_user_id: ID of the admin user performing the action
        action: Description of the action (e.g., "create_product", "update_order")
        entity_type: Type of entity affected (e.g., "product", "order", "user")
        entity_id: ID of the affected entity
        details: Additional details in JSONB format
        ip_address: IP address of the request

    Returns:
        Created activity log entry
    """
    log = AdminActivityLog(
        admin_user_id=admin_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def get_activity_logs(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    admin_user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Tuple[List[AdminActivityLog], int]:
    """
    Get admin activity logs with pagination and filters.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        admin_user_id: Filter by admin user
        action: Filter by action type
        entity_type: Filter by entity type
        start_date: Filter by start date
        end_date: Filter by end date

    Returns:
        Tuple of (logs list, total count)
    """
    query = db.query(AdminActivityLog)

    # Apply filters
    if admin_user_id:
        query = query.filter(AdminActivityLog.admin_user_id == admin_user_id)

    if action:
        query = query.filter(AdminActivityLog.action.ilike(f"%{action}%"))

    if entity_type:
        query = query.filter(AdminActivityLog.entity_type == entity_type)

    if start_date:
        query = query.filter(AdminActivityLog.created_at >= start_date)

    if end_date:
        query = query.filter(AdminActivityLog.created_at <= end_date)

    total = query.count()

    # Order by created_at descending (most recent first)
    logs = query.order_by(AdminActivityLog.created_at.desc()).offset(skip).limit(limit).all()

    return logs, total


def get_activity_log_by_id(db: Session, log_id: UUID) -> Optional[AdminActivityLog]:
    """
    Get a specific activity log by ID.

    Args:
        db: Database session
        log_id: Activity log ID

    Returns:
        Activity log or None if not found
    """
    return db.query(AdminActivityLog).filter(AdminActivityLog.id == log_id).first()


def get_user_activity_summary(db: Session, admin_user_id: UUID, days: int = 30) -> Dict[str, Any]:
    """
    Get activity summary for a specific admin user.

    Args:
        db: Database session
        admin_user_id: Admin user ID
        days: Number of days to look back (default: 30)

    Returns:
        Dictionary with activity summary stats
    """
    from datetime import datetime, timedelta, timezone

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    query = db.query(AdminActivityLog).filter(
        and_(
            AdminActivityLog.admin_user_id == admin_user_id,
            AdminActivityLog.created_at >= cutoff_date,
        )
    )

    total_actions = query.count()

    # Get action breakdown
    action_counts = {}
    for log in query.all():
        action_counts[log.action] = action_counts.get(log.action, 0) + 1

    # Get entity type breakdown
    entity_counts = {}
    for log in query.all():
        if log.entity_type:
            entity_counts[log.entity_type] = entity_counts.get(log.entity_type, 0) + 1

    return {
        "total_actions": total_actions,
        "period_days": days,
        "action_breakdown": action_counts,
        "entity_breakdown": entity_counts,
    }
