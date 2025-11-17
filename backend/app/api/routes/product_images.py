"""
Product Image API routes
Admin-only endpoints for product image management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.product_image import (
    ProductImageResponse,
    ProductImageUpdate,
    ProductImageUploadResponse
)
from app.services import product_image_service

router = APIRouter(prefix="/admin/products", tags=["admin", "product-images"])


@router.get("/{product_id}/images", response_model=list[ProductImageResponse])
async def list_product_images(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get all images for a product

    **Admin only**

    Returns images ordered by display_order.
    """
    images = product_image_service.get_product_images(db, product_id)
    return images


@router.post("/{product_id}/images", response_model=ProductImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    product_id: UUID,
    file: UploadFile = File(..., description="Image file to upload"),
    alt_text: Optional[str] = Form(None, max_length=255, description="Alternative text for image"),
    is_primary: bool = Form(False, description="Set as primary image"),
    display_order: int = Form(0, ge=0, description="Display order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Upload a new product image

    **Admin only**

    Accepts multipart/form-data with image file and metadata.
    The image will be uploaded to S3 (or local storage if S3 not configured).
    The first image uploaded is automatically set as primary.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Expected image, got {file.content_type}"
        )

    # Validate file size (max 10MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed size of 10MB"
        )

    try:
        image = product_image_service.upload_product_image(
            db=db,
            product_id=product_id,
            file=file.file,
            filename=file.filename or "image.jpg",
            alt_text=alt_text,
            is_primary=is_primary,
            display_order=display_order
        )

        return ProductImageUploadResponse(image=image)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.get("/images/{image_id}", response_model=ProductImageResponse)
async def get_product_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific product image by ID

    **Admin only**
    """
    image = product_image_service.get_product_image_by_id(db, image_id)

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product image with ID {image_id} not found"
        )

    return image


@router.put("/images/{image_id}", response_model=ProductImageResponse)
async def update_product_image(
    image_id: UUID,
    image_data: ProductImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update product image metadata

    **Admin only**

    Can update alt_text and display_order.
    Use separate endpoint to set as primary.
    """
    image = product_image_service.update_product_image(db, image_id, image_data)

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product image with ID {image_id} not found"
        )

    return image


@router.put("/images/{image_id}/primary", response_model=ProductImageResponse)
async def set_primary_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Set an image as the primary product image

    **Admin only**

    Automatically unsets the previous primary image.
    Only one image can be primary per product.
    """
    image = product_image_service.set_primary_image(db, image_id)

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product image with ID {image_id} not found"
        )

    return image


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a product image

    **Admin only**

    Deletes both the database record and the file from storage.
    If deleting the primary image, another image will be automatically set as primary.
    """
    deleted = product_image_service.delete_product_image(
        db, image_id, delete_from_storage=True
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product image with ID {image_id} not found"
        )

    return None


@router.put("/{product_id}/images/reorder", response_model=list[ProductImageResponse])
async def reorder_product_images(
    product_id: UUID,
    image_orders: dict[UUID, int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Reorder product images

    **Admin only**

    Pass a dictionary mapping image_id to new display_order.
    Example: {"uuid1": 0, "uuid2": 1, "uuid3": 2}
    """
    try:
        images = product_image_service.reorder_product_images(
            db, product_id, image_orders
        )
        return images

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
