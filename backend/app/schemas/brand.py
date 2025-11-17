"""
Brand schemas for request/response validation
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


class BrandBase(BaseModel):
    """Base brand schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Brand name")
    description: Optional[str] = Field(None, description="Brand description")
    logo_url: Optional[str] = Field(None, max_length=500, description="Brand logo URL")
    is_active: bool = Field(True, description="Whether brand is active")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean brand name"""
        v = v.strip()
        if not v:
            raise ValueError('Brand name cannot be empty')
        return v


class BrandCreate(BrandBase):
    """Schema for creating a new brand"""
    pass


class BrandUpdate(BaseModel):
    """Schema for updating a brand (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean brand name if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Brand name cannot be empty')
        return v


class BrandResponse(BrandBase):
    """Schema for brand response"""
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BrandListResponse(BaseModel):
    """Schema for paginated brand list response"""
    items: list[BrandResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
