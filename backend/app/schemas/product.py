"""
Product schemas for request/response validation
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, computed_field
import re


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


class ProductBase(BaseModel):
    """Base product schema with common fields"""
    title: str = Field(..., min_length=1, max_length=500, description="Product title")
    description: Optional[str] = Field(None, description="Full product description")
    brand_id: Optional[UUID] = Field(None, description="Brand ID")
    category_id: Optional[UUID] = Field(None, description="Category ID")
    base_price: Decimal = Field(..., ge=0, description="Base price before discount")
    discount_type: Optional[str] = Field(None, description="Discount type: 'percentage' or 'fixed'")
    discount_value: Optional[Decimal] = Field(None, ge=0, description="Discount value")
    sku: Optional[str] = Field(None, max_length=100, description="Stock keeping unit (SKU)")
    inventory_count: int = Field(0, ge=0, description="Current inventory count")
    low_stock_threshold: int = Field(10, ge=0, description="Low stock alert threshold")
    is_active: bool = Field(True, description="Whether product is active")
    is_featured: bool = Field(False, description="Whether product is featured")
    tags: Optional[list[str]] = Field(default_factory=list, description="Product tags")
    meta_title: Optional[str] = Field(None, max_length=255, description="SEO meta title")
    meta_description: Optional[str] = Field(None, description="SEO meta description")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean product title"""
        v = v.strip()
        if not v:
            raise ValueError('Product title cannot be empty')
        return v

    @field_validator('discount_type')
    @classmethod
    def validate_discount_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate discount type"""
        if v is not None and v not in ['percentage', 'fixed']:
            raise ValueError("Discount type must be 'percentage' or 'fixed'")
        return v

    @field_validator('discount_value')
    @classmethod
    def validate_discount_value(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validate discount value based on type"""
        if v is not None:
            discount_type = info.data.get('discount_type')
            if discount_type == 'percentage' and v > 100:
                raise ValueError('Percentage discount cannot exceed 100')
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    brand_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    base_price: Optional[Decimal] = Field(None, ge=0)
    discount_type: Optional[str] = None
    discount_value: Optional[Decimal] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=100)
    inventory_count: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    tags: Optional[list[str]] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean product title if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Product title cannot be empty')
        return v

    @field_validator('discount_type')
    @classmethod
    def validate_discount_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate discount type"""
        if v is not None and v not in ['percentage', 'fixed']:
            raise ValueError("Discount type must be 'percentage' or 'fixed'")
        return v

    @field_validator('discount_value')
    @classmethod
    def validate_discount_value(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validate discount value based on type"""
        if v is not None:
            discount_type = info.data.get('discount_type')
            if discount_type == 'percentage' and v > 100:
                raise ValueError('Percentage discount cannot exceed 100')
        return v


class BrandSummary(BaseModel):
    """Minimal brand info for product response"""
    id: UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


class CategorySummary(BaseModel):
    """Minimal category info for product response"""
    id: UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime
    brand: Optional[BrandSummary] = None
    category: Optional[CategorySummary] = None

    @computed_field
    @property
    def final_price(self) -> Decimal:
        """Calculate final price after discount"""
        if self.discount_type and self.discount_value:
            if self.discount_type == 'percentage':
                discount_amount = self.base_price * (self.discount_value / Decimal('100'))
                return self.base_price - discount_amount
            elif self.discount_type == 'fixed':
                return max(Decimal('0'), self.base_price - self.discount_value)
        return self.base_price

    @computed_field
    @property
    def in_stock(self) -> bool:
        """Check if product is in stock"""
        return self.inventory_count > 0

    @computed_field
    @property
    def is_low_stock(self) -> bool:
        """Check if product is low on stock"""
        return 0 < self.inventory_count <= self.low_stock_threshold

    model_config = {"from_attributes": True}


class RatingSummary(BaseModel):
    """Summary of product ratings"""
    average_rating: float = Field(..., description="Average rating (0-5)")
    total_reviews: int = Field(..., description="Total number of reviews")
    rating_distribution: dict[int, int] = Field(..., description="Distribution of ratings (1-5 stars)")


class ProductDetailResponse(ProductResponse):
    """
    Enhanced product response with all relations for detail page.

    Includes:
    - All product info from ProductResponse
    - Images and videos
    - Variants
    - Average rating and review count
    - Related products (same category/brand)
    - Recent approved reviews
    """
    images: List[Any] = Field(default_factory=list, description="Product images")
    videos: List[Any] = Field(default_factory=list, description="Product videos")
    variants: List[Any] = Field(default_factory=list, description="Product variants")
    rating_summary: Optional[RatingSummary] = Field(None, description="Rating summary")
    related_products: List[ProductResponse] = Field(default_factory=list, description="Related products")
    reviews: List[Any] = Field(default_factory=list, description="Recent approved reviews")

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Schema for paginated product list response"""
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
