"""
Product Image service
Business logic for product image management
"""
from typing import Optional, BinaryIO
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.product import ProductImage, Product
from app.schemas.product_image import ProductImageCreate, ProductImageUpdate
from app.services.file_storage_service import file_storage


def get_product_image_by_id(db: Session, image_id: UUID) -> Optional[ProductImage]:
    """Get product image by ID"""
    return db.query(ProductImage).filter(ProductImage.id == image_id).first()


def get_product_images(
    db: Session,
    product_id: UUID,
    is_primary: Optional[bool] = None
) -> list[ProductImage]:
    """
    Get all images for a product

    Args:
        db: Database session
        product_id: Product ID
        is_primary: Filter by primary status

    Returns:
        List of product images ordered by display_order
    """
    query = db.query(ProductImage).filter(ProductImage.product_id == product_id)

    if is_primary is not None:
        query = query.filter(ProductImage.is_primary == is_primary)

    return query.order_by(ProductImage.display_order, ProductImage.created_at).all()


def get_primary_image(db: Session, product_id: UUID) -> Optional[ProductImage]:
    """Get primary image for a product"""
    return db.query(ProductImage).filter(
        and_(
            ProductImage.product_id == product_id,
            ProductImage.is_primary == True
        )
    ).first()


def create_product_image(
    db: Session,
    product_id: UUID,
    image_data: ProductImageCreate
) -> ProductImage:
    """
    Create a new product image

    Args:
        db: Database session
        product_id: Product ID
        image_data: Image creation data

    Returns:
        Created product image

    Raises:
        ValueError: If product not found or primary image conflict
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError(f"Product with ID {product_id} not found")

    # If setting as primary, remove primary from existing images
    if image_data.is_primary:
        _unset_primary_images(db, product_id)

    # If this is the first image, make it primary by default
    existing_images = get_product_images(db, product_id)
    if len(existing_images) == 0 and not image_data.is_primary:
        image_data.is_primary = True

    # Create image
    product_image = ProductImage(
        product_id=product_id,
        image_url=image_data.image_url,
        alt_text=image_data.alt_text,
        is_primary=image_data.is_primary,
        display_order=image_data.display_order
    )

    db.add(product_image)
    db.commit()
    db.refresh(product_image)

    return product_image


def upload_product_image(
    db: Session,
    product_id: UUID,
    file: BinaryIO,
    filename: str,
    alt_text: Optional[str] = None,
    is_primary: bool = False,
    display_order: int = 0
) -> ProductImage:
    """
    Upload a product image file

    Args:
        db: Database session
        product_id: Product ID
        file: File-like object
        filename: Original filename
        alt_text: Alt text for image
        is_primary: Whether to set as primary image
        display_order: Display order

    Returns:
        Created product image

    Raises:
        ValueError: If product not found or upload fails
        Exception: If file upload fails
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError(f"Product with ID {product_id} not found")

    # Upload file to storage
    try:
        image_url = file_storage.upload_file(
            file=file,
            filename=filename,
            folder=f"products/{product_id}"
        )
    except Exception as e:
        raise Exception(f"Failed to upload image: {str(e)}")

    # Create image record
    image_data = ProductImageCreate(
        image_url=image_url,
        alt_text=alt_text,
        is_primary=is_primary,
        display_order=display_order
    )

    return create_product_image(db, product_id, image_data)


def update_product_image(
    db: Session,
    image_id: UUID,
    image_data: ProductImageUpdate
) -> Optional[ProductImage]:
    """
    Update a product image

    Args:
        db: Database session
        image_id: Image ID to update
        image_data: Image update data

    Returns:
        Updated product image or None if not found
    """
    product_image = get_product_image_by_id(db, image_id)
    if not product_image:
        return None

    # Update fields if provided
    if image_data.alt_text is not None:
        product_image.alt_text = image_data.alt_text

    if image_data.display_order is not None:
        product_image.display_order = image_data.display_order

    db.commit()
    db.refresh(product_image)

    return product_image


def set_primary_image(db: Session, image_id: UUID) -> Optional[ProductImage]:
    """
    Set an image as the primary image for its product

    Args:
        db: Database session
        image_id: Image ID to set as primary

    Returns:
        Updated product image or None if not found
    """
    product_image = get_product_image_by_id(db, image_id)
    if not product_image:
        return None

    # Unset primary on other images for this product
    _unset_primary_images(db, product_image.product_id)

    # Set this image as primary
    product_image.is_primary = True
    db.commit()
    db.refresh(product_image)

    return product_image


def delete_product_image(db: Session, image_id: UUID, delete_from_storage: bool = True) -> bool:
    """
    Delete a product image

    Args:
        db: Database session
        image_id: Image ID to delete
        delete_from_storage: Whether to delete file from storage

    Returns:
        True if deleted, False if not found

    Raises:
        ValueError: If trying to delete the only primary image
    """
    product_image = get_product_image_by_id(db, image_id)
    if not product_image:
        return False

    # If deleting the primary image and there are other images, set another as primary
    if product_image.is_primary:
        other_images = db.query(ProductImage).filter(
            and_(
                ProductImage.product_id == product_image.product_id,
                ProductImage.id != image_id
            )
        ).order_by(ProductImage.display_order).all()

        if other_images:
            # Set the first other image as primary
            other_images[0].is_primary = True

    # Delete from storage if requested
    if delete_from_storage:
        file_storage.delete_file(product_image.image_url)

    # Delete from database
    db.delete(product_image)
    db.commit()

    return True


def reorder_product_images(
    db: Session,
    product_id: UUID,
    image_orders: dict[UUID, int]
) -> list[ProductImage]:
    """
    Reorder multiple product images at once

    Args:
        db: Database session
        product_id: Product ID
        image_orders: Dict mapping image_id to new display_order

    Returns:
        Updated list of product images

    Raises:
        ValueError: If any image doesn't belong to the product
    """
    for image_id, display_order in image_orders.items():
        product_image = get_product_image_by_id(db, image_id)

        if not product_image:
            raise ValueError(f"Image with ID {image_id} not found")

        if product_image.product_id != product_id:
            raise ValueError(f"Image {image_id} does not belong to product {product_id}")

        product_image.display_order = display_order

    db.commit()

    return get_product_images(db, product_id)


def _unset_primary_images(db: Session, product_id: UUID) -> None:
    """
    Unset primary flag on all images for a product

    Args:
        db: Database session
        product_id: Product ID
    """
    db.query(ProductImage).filter(
        and_(
            ProductImage.product_id == product_id,
            ProductImage.is_primary == True
        )
    ).update({"is_primary": False})
    db.flush()
