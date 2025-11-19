"""Testimonial schemas for API requests and responses."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TestimonialCreate(BaseModel):
    """Schema for creating a testimonial."""

    customer_name: str = Field(..., min_length=1, max_length=255, alias="customerName")
    customer_photo_url: Optional[str] = Field(None, max_length=500, alias="customerPhotoUrl")
    location: Optional[str] = Field(None, max_length=100)
    rating: int = Field(..., ge=1, le=5)
    testimonial_text: str = Field(..., min_length=1, alias="testimonialText")
    related_service_id: Optional[UUID] = Field(None, alias="relatedServiceId")
    related_product_id: Optional[UUID] = Field(None, alias="relatedProductId")
    is_featured: bool = Field(default=False, alias="isFeatured")
    is_approved: bool = Field(default=True, alias="isApproved")
    display_order: int = Field(default=0, ge=0, alias="displayOrder")

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, v: str) -> str:
        """Validate and clean customer name."""
        v = v.strip()
        if not v:
            raise ValueError("Customer name cannot be empty")
        return v

    @field_validator("testimonial_text")
    @classmethod
    def validate_testimonial_text(cls, v: str) -> str:
        """Validate and clean testimonial text."""
        v = v.strip()
        if not v:
            raise ValueError("Testimonial text cannot be empty")
        return v

    class Config:
        populate_by_name = True


class TestimonialUpdate(BaseModel):
    """Schema for updating a testimonial."""

    customer_name: Optional[str] = Field(None, min_length=1, max_length=255, alias="customerName")
    customer_photo_url: Optional[str] = Field(None, max_length=500, alias="customerPhotoUrl")
    location: Optional[str] = Field(None, max_length=100)
    rating: Optional[int] = Field(None, ge=1, le=5)
    testimonial_text: Optional[str] = Field(None, min_length=1, alias="testimonialText")
    related_service_id: Optional[UUID] = Field(None, alias="relatedServiceId")
    related_product_id: Optional[UUID] = Field(None, alias="relatedProductId")
    is_featured: Optional[bool] = Field(None, alias="isFeatured")
    is_approved: Optional[bool] = Field(None, alias="isApproved")
    display_order: Optional[int] = Field(None, ge=0, alias="displayOrder")

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean customer name."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Customer name cannot be empty")
        return v

    @field_validator("testimonial_text")
    @classmethod
    def validate_testimonial_text(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean testimonial text."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Testimonial text cannot be empty")
        return v

    class Config:
        populate_by_name = True


class TestimonialResponse(BaseModel):
    """Testimonial response schema."""

    id: UUID
    customer_name: str = Field(..., alias="customerName")
    customer_photo_url: Optional[str] = Field(None, alias="customerPhotoUrl")
    location: Optional[str] = None
    rating: int
    testimonial_text: str = Field(..., alias="testimonialText")
    related_service_id: Optional[UUID] = Field(None, alias="relatedServiceId")
    related_product_id: Optional[UUID] = Field(None, alias="relatedProductId")
    is_featured: bool = Field(..., alias="isFeatured")
    is_approved: bool = Field(..., alias="isApproved")
    display_order: int = Field(..., alias="displayOrder")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class TestimonialListResponse(BaseModel):
    """List of testimonials response."""

    items: List[TestimonialResponse]
    total: int

    class Config:
        populate_by_name = True


class ApprovalUpdate(BaseModel):
    """Schema for approving/rejecting a testimonial."""

    is_approved: bool = Field(..., alias="isApproved")

    class Config:
        populate_by_name = True
