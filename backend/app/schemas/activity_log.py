"""Activity log schemas for API requests and responses."""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AdminUserSummary(BaseModel):
    """Summary of admin user for activity logs."""

    id: UUID
    email: str
    full_name: Optional[str] = Field(None, alias="fullName")
    admin_role: Optional[str] = Field(None, alias="adminRole")

    model_config = {"from_attributes": True, "populate_by_name": True}


class ActivityLogResponse(BaseModel):
    """Schema for activity log response."""

    id: UUID
    admin_user_id: UUID = Field(..., alias="adminUserId")
    admin_user: Optional[AdminUserSummary] = Field(None, alias="adminUser")
    action: str
    entity_type: Optional[str] = Field(None, alias="entityType")
    entity_id: Optional[UUID] = Field(None, alias="entityId")
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, alias="ipAddress")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"from_attributes": True, "populate_by_name": True}


class ActivityLogListResponse(BaseModel):
    """Response for paginated activity log list."""

    logs: list[ActivityLogResponse]
    total: int
    skip: int
    limit: int

    model_config = {"populate_by_name": True}


class ActivitySummaryResponse(BaseModel):
    """Activity summary statistics for an admin user."""

    total_actions: int = Field(..., alias="totalActions")
    period_days: int = Field(..., alias="periodDays")
    action_breakdown: Dict[str, int] = Field(..., alias="actionBreakdown")
    entity_breakdown: Dict[str, int] = Field(..., alias="entityBreakdown")

    model_config = {"populate_by_name": True}
