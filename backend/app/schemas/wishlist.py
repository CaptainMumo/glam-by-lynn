"""Wishlist schemas for API requests and responses."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class WishlistItemCreate(BaseModel):
    """Schema for adding product to wishlist."""

    product_id: UUID = Field(..., alias="productId")

    model_config = {"populate_by_name": True}


class ProductSummary(BaseModel):
    """Product info for wishlist item."""

    id: UUID
    title: str
    slug: str
    base_price: Decimal = Field(..., alias="basePrice")
    inventory_count: int = Field(..., alias="inventoryCount")
    is_active: bool = Field(..., alias="isActive")

    model_config = {"from_attributes": True, "populate_by_name": True}


class WishlistItemResponse(BaseModel):
    """Schema for wishlist item response."""

    id: UUID
    user_id: UUID = Field(..., alias="userId")
    product_id: UUID = Field(..., alias="productId")
    created_at: datetime = Field(..., alias="createdAt")
    product: ProductSummary

    model_config = {"from_attributes": True, "populate_by_name": True}


class WishlistResponse(BaseModel):
    """Schema for wishlist response."""

    items: list[WishlistItemResponse]
    total: int

    model_config = {"populate_by_name": True}
