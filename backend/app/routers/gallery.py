"""Gallery API endpoints."""
from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.gallery import GalleryListResponse, GalleryPostResponse
from app.services.gallery_service import get_published_gallery_posts

router = APIRouter(prefix="/gallery", tags=["gallery"])


@router.get("", response_model=GalleryListResponse, status_code=status.HTTP_200_OK)
def list_gallery_posts(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    media_type: Optional[str] = Query(
        None,
        description="Filter by media type",
        pattern="^(image|video)$",
    ),
    source_type: Optional[str] = Query(
        None,
        description="Filter by source type",
        pattern="^(instagram|tiktok|original)$",
    ),
    db: Session = Depends(get_db),
):
    """
    Get paginated list of published gallery posts.

    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **media_type**: Filter by 'image' or 'video'
    - **source_type**: Filter by 'instagram', 'tiktok', or 'original'

    Returns posts ordered by featured status, display order, and publication date.
    Only returns posts with published_at <= current time.
    """
    posts, total = get_published_gallery_posts(
        db=db,
        page=page,
        page_size=page_size,
        media_type=media_type,
        source_type=source_type,
    )

    total_pages = ceil(total / page_size) if total > 0 else 0

    return GalleryListResponse(
        items=[GalleryPostResponse.model_validate(post) for post in posts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
