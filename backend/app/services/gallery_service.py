"""Gallery service for business logic."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.content import GalleryPost


def get_published_gallery_posts(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    media_type: Optional[str] = None,
    source_type: Optional[str] = None,
) -> tuple[List[GalleryPost], int]:
    """
    Get published gallery posts with pagination and filters.

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        media_type: Filter by media type ('image' or 'video')
        source_type: Filter by source type ('instagram', 'tiktok', or 'original')

    Returns:
        Tuple of (list of gallery posts, total count)
    """
    # Build base query - only published posts (published_at <= now)
    query = db.query(GalleryPost).filter(
        GalleryPost.published_at <= datetime.utcnow()
    )

    # Apply filters
    if media_type:
        query = query.filter(GalleryPost.media_type == media_type)

    if source_type:
        query = query.filter(GalleryPost.source_type == source_type)

    # Get total count before pagination
    total = query.count()

    # Apply ordering (featured first, then by display_order, then by published_at desc)
    query = query.order_by(
        GalleryPost.is_featured.desc(),
        GalleryPost.display_order.asc(),
        GalleryPost.published_at.desc(),
    )

    # Apply pagination
    offset = (page - 1) * page_size
    posts = query.offset(offset).limit(page_size).all()

    return posts, total


def get_gallery_post_by_id(db: Session, post_id: UUID) -> Optional[GalleryPost]:
    """Get a single published gallery post by ID."""
    return (
        db.query(GalleryPost)
        .filter(
            and_(
                GalleryPost.id == post_id,
                GalleryPost.published_at <= datetime.utcnow(),
            )
        )
        .first()
    )
