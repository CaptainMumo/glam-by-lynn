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


# Admin-specific functions


def get_all_gallery_posts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    media_type: Optional[str] = None,
    source_type: Optional[str] = None,
    is_featured: Optional[bool] = None,
) -> tuple[List[GalleryPost], int]:
    """
    Get all gallery posts (admin only, includes unpublished).

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        media_type: Filter by media type
        source_type: Filter by source type
        is_featured: Filter by featured status

    Returns:
        Tuple of (list of gallery posts, total count)
    """
    query = db.query(GalleryPost)

    # Apply filters
    if media_type:
        query = query.filter(GalleryPost.media_type == media_type)

    if source_type:
        query = query.filter(GalleryPost.source_type == source_type)

    if is_featured is not None:
        query = query.filter(GalleryPost.is_featured == is_featured)

    # Get total count
    total = query.count()

    # Apply ordering
    query = query.order_by(
        GalleryPost.is_featured.desc(),
        GalleryPost.display_order.asc(),
        GalleryPost.created_at.desc(),
    )

    # Apply pagination
    posts = query.offset(skip).limit(limit).all()

    return posts, total


def admin_get_gallery_post(db: Session, post_id: UUID) -> Optional[GalleryPost]:
    """Get any gallery post by ID (admin only, includes unpublished)."""
    return db.query(GalleryPost).filter(GalleryPost.id == post_id).first()


def create_gallery_post(
    db: Session,
    media_type: str,
    media_url: str,
    thumbnail_url: Optional[str] = None,
    caption: Optional[str] = None,
    tags: Optional[List[str]] = None,
    source_type: Optional[str] = None,
    is_featured: bool = False,
    display_order: int = 0,
    published_at: Optional[datetime] = None,
) -> GalleryPost:
    """
    Create a new gallery post (admin only).

    Args:
        db: Database session
        media_type: Type of media ('image' or 'video')
        media_url: URL to the media file
        thumbnail_url: URL to thumbnail (optional)
        caption: Caption for the post (optional)
        tags: List of tags (optional)
        source_type: Source type ('instagram', 'tiktok', or 'original') (optional)
        is_featured: Whether post is featured
        display_order: Display order (lower = higher priority)
        published_at: Publication timestamp (defaults to now)

    Returns:
        Created gallery post
    """
    post = GalleryPost(
        media_type=media_type,
        media_url=media_url,
        thumbnail_url=thumbnail_url,
        caption=caption,
        tags=tags or [],
        source_type=source_type,
        is_featured=is_featured,
        display_order=display_order,
        published_at=published_at or datetime.utcnow(),
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


def update_gallery_post(
    db: Session,
    post_id: UUID,
    media_type: Optional[str] = None,
    media_url: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
    caption: Optional[str] = None,
    tags: Optional[List[str]] = None,
    source_type: Optional[str] = None,
    is_featured: Optional[bool] = None,
    display_order: Optional[int] = None,
    published_at: Optional[datetime] = None,
) -> Optional[GalleryPost]:
    """
    Update a gallery post (admin only).

    Args:
        db: Database session
        post_id: Post ID
        media_type: New media type (optional)
        media_url: New media URL (optional)
        thumbnail_url: New thumbnail URL (optional)
        caption: New caption (optional)
        tags: New tags (optional)
        source_type: New source type (optional)
        is_featured: New featured status (optional)
        display_order: New display order (optional)
        published_at: New publication timestamp (optional)

    Returns:
        Updated gallery post or None if not found
    """
    post = db.query(GalleryPost).filter(GalleryPost.id == post_id).first()
    if not post:
        return None

    # Update fields if provided
    if media_type is not None:
        post.media_type = media_type

    if media_url is not None:
        post.media_url = media_url

    if thumbnail_url is not None:
        post.thumbnail_url = thumbnail_url

    if caption is not None:
        post.caption = caption

    if tags is not None:
        post.tags = tags

    if source_type is not None:
        post.source_type = source_type

    if is_featured is not None:
        post.is_featured = is_featured

    if display_order is not None:
        post.display_order = display_order

    if published_at is not None:
        post.published_at = published_at

    db.commit()
    db.refresh(post)

    return post


def delete_gallery_post(db: Session, post_id: UUID) -> bool:
    """
    Delete a gallery post (admin only).

    Args:
        db: Database session
        post_id: Post ID to delete

    Returns:
        True if deleted, False if not found
    """
    post = db.query(GalleryPost).filter(GalleryPost.id == post_id).first()
    if not post:
        return False

    db.delete(post)
    db.commit()

    return True
