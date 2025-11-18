"""Gallery post schemas for API requests and responses."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class GalleryPostResponse(BaseModel):
    """Gallery post response schema."""

    id: UUID
    media_type: str = Field(..., alias="mediaType")
    media_url: str = Field(..., alias="mediaUrl")
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
    caption: Optional[str] = None
    tags: Optional[List[str]] = []
    source_type: Optional[str] = Field(None, alias="sourceType")
    is_featured: bool = Field(..., alias="isFeatured")
    display_order: int = Field(..., alias="displayOrder")
    published_at: datetime = Field(..., alias="publishedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class GalleryListResponse(BaseModel):
    """Paginated gallery list response."""

    items: List[GalleryPostResponse]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    total_pages: int = Field(..., alias="totalPages")

    class Config:
        populate_by_name = True


class GalleryPostCreate(BaseModel):
    """Schema for creating a gallery post."""

    media_type: str = Field(..., alias="mediaType", pattern="^(image|video)$")
    media_url: str = Field(..., alias="mediaUrl", max_length=500)
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl", max_length=500)
    caption: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    source_type: Optional[str] = Field(None, alias="sourceType", pattern="^(instagram|tiktok|original)$")
    is_featured: bool = Field(default=False, alias="isFeatured")
    display_order: int = Field(default=0, alias="displayOrder")
    published_at: Optional[datetime] = Field(None, alias="publishedAt")

    class Config:
        populate_by_name = True


class GalleryPostUpdate(BaseModel):
    """Schema for updating a gallery post."""

    media_type: Optional[str] = Field(None, alias="mediaType", pattern="^(image|video)$")
    media_url: Optional[str] = Field(None, alias="mediaUrl", max_length=500)
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl", max_length=500)
    caption: Optional[str] = None
    tags: Optional[List[str]] = None
    source_type: Optional[str] = Field(None, alias="sourceType", pattern="^(instagram|tiktok|original)$")
    is_featured: Optional[bool] = Field(None, alias="isFeatured")
    display_order: Optional[int] = Field(None, alias="displayOrder")
    published_at: Optional[datetime] = Field(None, alias="publishedAt")

    class Config:
        populate_by_name = True
