"""
Category schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import re


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


class CategoryBase(BaseModel):
    """Base category schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    image_url: Optional[str] = Field(None, max_length=500, description="Category image URL")
    parent_category_id: Optional[UUID] = Field(None, description="Parent category ID for subcategories")
    display_order: int = Field(0, ge=0, description="Display order (lower = earlier)")
    is_active: bool = Field(True, description="Whether category is active")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean category name"""
        v = v.strip()
        if not v:
            raise ValueError('Category name cannot be empty')
        return v


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    parent_category_id: Optional[UUID] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean category name if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Category name cannot be empty')
        return v


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategoryWithSubcategories(CategoryResponse):
    """Schema for category with subcategories (hierarchical view)"""
    subcategories: list['CategoryWithSubcategories'] = Field(default_factory=list)


class CategoryListResponse(BaseModel):
    """Schema for paginated category list response"""
    items: list[CategoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CategoryTreeResponse(BaseModel):
    """Schema for hierarchical category tree response"""
    items: list[CategoryWithSubcategories]
    total: int
