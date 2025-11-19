"""Order schemas for API requests and responses."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class OrderItemCreate(BaseModel):
    """Schema for creating an order item from cart."""

    product_id: UUID = Field(..., alias="productId")
    product_variant_id: Optional[UUID] = Field(None, alias="productVariantId")
    quantity: int

    class Config:
        populate_by_name = True

    @validator("quantity")
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class GuestInfo(BaseModel):
    """Guest customer information."""

    email: str
    name: str
    phone: str

    @validator("email")
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v.lower()

    @validator("phone")
    def validate_phone(cls, v):
        # Basic phone validation
        if not v or len(v) < 10:
            raise ValueError("Phone number must be at least 10 characters")
        return v


class DeliveryInfo(BaseModel):
    """Delivery address information."""

    county: str
    town: str
    address: str

    class Config:
        populate_by_name = True


class OrderCreate(BaseModel):
    """Schema for creating a new order."""

    guest_info: Optional[GuestInfo] = Field(None, alias="guestInfo")
    delivery_info: DeliveryInfo = Field(..., alias="deliveryInfo")
    promo_code: Optional[str] = Field(None, alias="promoCode")
    payment_method: Optional[str] = Field(None, alias="paymentMethod")

    class Config:
        populate_by_name = True

    @validator("promo_code")
    def validate_promo_code(cls, v):
        if v:
            return v.upper()
        return v


class OrderItemResponse(BaseModel):
    """Schema for order item in response."""

    id: UUID
    product_id: Optional[UUID] = Field(None, alias="productId")
    product_variant_id: Optional[UUID] = Field(None, alias="productVariantId")
    product_title: str = Field(..., alias="productTitle")
    product_sku: Optional[str] = Field(None, alias="productSku")
    quantity: int
    unit_price: Decimal = Field(..., alias="unitPrice")
    discount: Decimal
    total_price: Decimal = Field(..., alias="totalPrice")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class OrderResponse(BaseModel):
    """Schema for order in response."""

    id: UUID
    order_number: str = Field(..., alias="orderNumber")
    user_id: Optional[UUID] = Field(None, alias="userId")
    guest_email: Optional[str] = Field(None, alias="guestEmail")
    guest_name: Optional[str] = Field(None, alias="guestName")
    guest_phone: Optional[str] = Field(None, alias="guestPhone")
    delivery_county: str = Field(..., alias="deliveryCounty")
    delivery_town: str = Field(..., alias="deliveryTown")
    delivery_address: str = Field(..., alias="deliveryAddress")
    subtotal: Decimal
    discount_amount: Decimal = Field(..., alias="discountAmount")
    delivery_fee: Decimal = Field(..., alias="deliveryFee")
    total_amount: Decimal = Field(..., alias="totalAmount")
    payment_method: Optional[str] = Field(None, alias="paymentMethod")
    payment_confirmed: bool = Field(..., alias="paymentConfirmed")
    status: str
    promo_code_id: Optional[UUID] = Field(None, alias="promoCodeId")
    order_items: List[OrderItemResponse] = Field(..., alias="orderItems")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class OrderSummary(BaseModel):
    """Summary of order for list views."""

    id: UUID
    order_number: str = Field(..., alias="orderNumber")
    total_amount: Decimal = Field(..., alias="totalAmount")
    status: str
    payment_confirmed: bool = Field(..., alias="paymentConfirmed")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True
