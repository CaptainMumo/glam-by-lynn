"""Review schemas for API requests and responses."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ReviewCreate(BaseModel):
    """Schema for creating a review."""

    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=5000, description="Review text (optional)", alias="reviewText")

    @field_validator("review_text")
    @classmethod
    def validate_review_text(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean review text."""
        if v is not None:
            v = v.strip()
            if len(v) < 10 and len(v) > 0:
                raise ValueError("Review text must be at least 10 characters if provided")
        return v if v else None

    model_config = {"populate_by_name": True}


class ReviewUpdate(BaseModel):
    """Schema for updating a review by the user."""

    rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=5000, alias="reviewText")

    @field_validator("review_text")
    @classmethod
    def validate_review_text(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean review text."""
        if v is not None:
            v = v.strip()
            if len(v) < 10 and len(v) > 0:
                raise ValueError("Review text must be at least 10 characters if provided")
        return v if v else None

    model_config = {"populate_by_name": True}


class ReviewAdminUpdate(BaseModel):
    """Schema for updating a review (admin only)."""

    is_approved: Optional[bool] = Field(None, description="Approval status", alias="isApproved")
    admin_reply: Optional[str] = Field(None, max_length=2000, description="Admin reply to review", alias="adminReply")

    @field_validator("admin_reply")
    @classmethod
    def validate_admin_reply(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean admin reply."""
        if v is not None:
            v = v.strip()
        return v if v else None

    model_config = {"populate_by_name": True}


class UserSummary(BaseModel):
    """Minimal user info for review response."""

    id: UUID
    full_name: Optional[str] = Field(None, alias="fullName")

    model_config = {"from_attributes": True, "populate_by_name": True}


class ReviewResponse(BaseModel):
    """Schema for review response."""

    id: UUID
    product_id: UUID = Field(..., alias="productId")
    user_id: UUID = Field(..., alias="userId")
    order_id: Optional[UUID] = Field(None, alias="orderId")
    rating: int
    review_text: Optional[str] = Field(None, alias="reviewText")
    is_verified_purchase: bool = Field(..., alias="isVerifiedPurchase")
    is_approved: bool = Field(..., alias="isApproved")
    helpful_count: int = Field(..., alias="helpfulCount")
    admin_reply: Optional[str] = Field(None, alias="adminReply")
    admin_reply_at: Optional[datetime] = Field(None, alias="adminReplyAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    user: Optional[UserSummary] = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class ReviewListResponse(BaseModel):
    """Schema for paginated review list response."""

    reviews: list[ReviewResponse]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    total_pages: int = Field(..., alias="totalPages")
    average_rating: Optional[float] = Field(None, alias="averageRating")

    model_config = {"populate_by_name": True}


class ProductRatingSummary(BaseModel):
    """Summary of product ratings."""

    total_reviews: int = Field(..., alias="totalReviews")
    average_rating: float = Field(..., alias="averageRating")
    rating_distribution: dict[int, int] = Field(..., alias="ratingDistribution")

    model_config = {"populate_by_name": True}
