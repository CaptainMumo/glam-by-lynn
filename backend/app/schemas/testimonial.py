"""Testimonial schemas for API requests and responses."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


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
    display_order: int = Field(..., alias="displayOrder")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class TestimonialListResponse(BaseModel):
    """List of testimonials response."""

    items: List[TestimonialResponse]
    total: int

    class Config:
        populate_by_name = True
