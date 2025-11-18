"""Admin gallery management routes."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.gallery import (
    GalleryListResponse,
    GalleryPostCreate,
    GalleryPostResponse,
    GalleryPostUpdate,
)
from app.services import gallery_service

router = APIRouter(tags=["Admin Gallery"])


@router.get(
    "/admin/gallery",
    response_model=GalleryListResponse,
    summary="List all gallery posts (admin only)",
)
def list_all_gallery_posts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    media_type: Optional[str] = Query(
        None, alias="mediaType", pattern="^(image|video)$", description="Filter by media type"
    ),
    source_type: Optional[str] = Query(
        None,
        alias="sourceType",
        pattern="^(instagram|tiktok|original)$",
        description="Filter by source type",
    ),
    is_featured: Optional[bool] = Query(None, alias="isFeatured", description="Filter by featured status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get all gallery posts (includes unpublished).

    Admin only. Supports pagination and filtering by media type, source type, and featured status.
    """
    posts, total = gallery_service.get_all_gallery_posts(
        db=db,
        skip=skip,
        limit=limit,
        media_type=media_type,
        source_type=source_type,
        is_featured=is_featured,
    )

    # Calculate pagination info
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1

    return GalleryListResponse(
        items=[GalleryPostResponse.model_validate(post) for post in posts],
        total=total,
        page=current_page,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get(
    "/admin/gallery/{post_id}",
    response_model=GalleryPostResponse,
    summary="Get gallery post by ID (admin only)",
)
def get_gallery_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get a single gallery post by ID (includes unpublished).

    Admin only.
    """
    post = gallery_service.admin_get_gallery_post(db=db, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Gallery post with ID {post_id} not found",
        )

    return GalleryPostResponse.model_validate(post)


@router.post(
    "/admin/gallery",
    response_model=GalleryPostResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Create gallery post (admin only)",
)
def create_gallery_post(
    post_data: GalleryPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Create a new gallery post.

    Admin only. Requires media_type and media_url. Other fields are optional.
    If published_at is not provided, defaults to current timestamp.
    """
    post = gallery_service.create_gallery_post(
        db=db,
        media_type=post_data.media_type,
        media_url=post_data.media_url,
        thumbnail_url=post_data.thumbnail_url,
        caption=post_data.caption,
        tags=post_data.tags,
        source_type=post_data.source_type,
        is_featured=post_data.is_featured,
        display_order=post_data.display_order,
        published_at=post_data.published_at,
    )

    return GalleryPostResponse.model_validate(post)


@router.put(
    "/admin/gallery/{post_id}",
    response_model=GalleryPostResponse,
    summary="Update gallery post (admin only)",
)
def update_gallery_post(
    post_id: UUID,
    post_data: GalleryPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Update a gallery post.

    Admin only. All fields are optional for partial updates.
    """
    post = gallery_service.update_gallery_post(
        db=db,
        post_id=post_id,
        media_type=post_data.media_type,
        media_url=post_data.media_url,
        thumbnail_url=post_data.thumbnail_url,
        caption=post_data.caption,
        tags=post_data.tags,
        source_type=post_data.source_type,
        is_featured=post_data.is_featured,
        display_order=post_data.display_order,
        published_at=post_data.published_at,
    )

    if not post:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Gallery post with ID {post_id} not found",
        )

    return GalleryPostResponse.model_validate(post)


@router.delete(
    "/admin/gallery/{post_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Delete gallery post (admin only)",
)
def delete_gallery_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Delete a gallery post.

    Admin only.
    """
    success = gallery_service.delete_gallery_post(db=db, post_id=post_id)
    if not success:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Gallery post with ID {post_id} not found",
        )

    return None
