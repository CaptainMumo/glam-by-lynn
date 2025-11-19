"""Promo code schemas for API requests and responses."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class PromoCodeCreate(BaseModel):
    """Schema for creating a promo code."""

    code: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None)
    discount_type: str = Field(..., pattern="^(percentage|fixed)$")
    discount_value: Decimal = Field(..., gt=0, decimal_places=2)
    min_order_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, alias="minOrderAmount")
    max_discount_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, alias="maxDiscountAmount")
    usage_limit: Optional[int] = Field(None, gt=0, alias="usageLimit")
    valid_from: Optional[datetime] = Field(None, alias="validFrom")
    valid_until: Optional[datetime] = Field(None, alias="validUntil")
    is_active: bool = Field(default=True, alias="isActive")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate and clean promo code."""
        v = v.strip().upper()
        if not v:
            raise ValueError("Promo code cannot be empty")
        # Only allow alphanumeric and underscores/hyphens
        if not all(c.isalnum() or c in ("_", "-") for c in v):
            raise ValueError("Promo code can only contain letters, numbers, underscores, and hyphens")
        return v

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, v: str) -> str:
        """Validate discount type."""
        if v not in ("percentage", "fixed"):
            raise ValueError("Discount type must be 'percentage' or 'fixed'")
        return v

    @field_validator("discount_value")
    @classmethod
    def validate_discount_value(cls, v: Decimal, info) -> Decimal:
        """Validate discount value based on type."""
        # If percentage, must be between 0 and 100
        if info.data.get("discount_type") == "percentage" and v > 100:
            raise ValueError("Percentage discount cannot exceed 100")
        return v

    @field_validator("valid_until")
    @classmethod
    def validate_dates(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate that valid_until is after valid_from."""
        if v and info.data.get("valid_from") and v <= info.data["valid_from"]:
            raise ValueError("valid_until must be after valid_from")
        return v

    class Config:
        populate_by_name = True


class PromoCodeUpdate(BaseModel):
    """Schema for updating a promo code."""

    code: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
    discount_type: Optional[str] = Field(None, pattern="^(percentage|fixed)$", alias="discountType")
    discount_value: Optional[Decimal] = Field(None, gt=0, decimal_places=2, alias="discountValue")
    min_order_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, alias="minOrderAmount")
    max_discount_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, alias="maxDiscountAmount")
    usage_limit: Optional[int] = Field(None, gt=0, alias="usageLimit")
    valid_from: Optional[datetime] = Field(None, alias="validFrom")
    valid_until: Optional[datetime] = Field(None, alias="validUntil")
    is_active: Optional[bool] = Field(None, alias="isActive")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean promo code."""
        if v is not None:
            v = v.strip().upper()
            if not v:
                raise ValueError("Promo code cannot be empty")
            # Only allow alphanumeric and underscores/hyphens
            if not all(c.isalnum() or c in ("_", "-") for c in v):
                raise ValueError("Promo code can only contain letters, numbers, underscores, and hyphens")
        return v

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate discount type."""
        if v is not None and v not in ("percentage", "fixed"):
            raise ValueError("Discount type must be 'percentage' or 'fixed'")
        return v

    class Config:
        populate_by_name = True


class PromoCodeResponse(BaseModel):
    """Promo code response schema."""

    id: UUID
    code: str
    description: Optional[str] = None
    discount_type: str = Field(..., alias="discountType")
    discount_value: Decimal = Field(..., alias="discountValue")
    min_order_amount: Optional[Decimal] = Field(None, alias="minOrderAmount")
    max_discount_amount: Optional[Decimal] = Field(None, alias="maxDiscountAmount")
    usage_limit: Optional[int] = Field(None, alias="usageLimit")
    usage_count: int = Field(..., alias="usageCount")
    valid_from: Optional[datetime] = Field(None, alias="validFrom")
    valid_until: Optional[datetime] = Field(None, alias="validUntil")
    is_active: bool = Field(..., alias="isActive")
    is_expired: bool = Field(..., alias="isExpired")
    is_usage_exhausted: bool = Field(..., alias="isUsageExhausted")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class PromoCodeListResponse(BaseModel):
    """List of promo codes response."""

    items: List[PromoCodeResponse]
    total: int

    class Config:
        populate_by_name = True


class PromoCodeValidationRequest(BaseModel):
    """Schema for validating a promo code."""

    code: str = Field(..., min_length=3, max_length=50)
    order_amount: Decimal = Field(..., gt=0, decimal_places=2, alias="orderAmount")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate and clean promo code."""
        v = v.strip().upper()
        if not v:
            raise ValueError("Promo code cannot be empty")
        return v

    class Config:
        populate_by_name = True


class PromoCodeValidationResponse(BaseModel):
    """Response for promo code validation."""

    valid: bool
    message: str
    discount_amount: Optional[Decimal] = Field(None, alias="discountAmount")
    promo_code: Optional[PromoCodeResponse] = Field(None, alias="promoCode")

    class Config:
        populate_by_name = True
