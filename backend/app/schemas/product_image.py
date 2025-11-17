"""
Product Image schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ProductImageBase(BaseModel):
    """Base product image schema"""
    alt_text: Optional[str] = Field(None, max_length=255, description="Alternative text for image")
    is_primary: bool = Field(False, description="Whether this is the primary product image")
    display_order: int = Field(0, ge=0, description="Display order (lower = earlier)")


class ProductImageCreate(ProductImageBase):
    """Schema for creating a product image"""
    image_url: str = Field(..., max_length=500, description="Image URL")


class ProductImageUpdate(BaseModel):
    """Schema for updating a product image"""
    alt_text: Optional[str] = Field(None, max_length=255)
    display_order: Optional[int] = Field(None, ge=0)


class ProductImageResponse(ProductImageBase):
    """Schema for product image response"""
    id: UUID
    product_id: UUID
    image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductImageUploadResponse(BaseModel):
    """Schema for image upload response"""
    image: ProductImageResponse
    message: str = "Image uploaded successfully"
