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
