"""
Product API routes
Admin-only endpoints for product management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import math

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse
)
from app.services import product_service

router = APIRouter(prefix="/admin/products", tags=["admin", "products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    brand_id: Optional[UUID] = Query(None, description="Filter by brand ID"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search in title, description, and tags"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum base price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum base price"),
    in_stock_only: bool = Query(False, description="Only show in-stock products"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get paginated list of products

    **Admin only**

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **is_active**: Filter by active status
    - **is_featured**: Filter by featured status
    - **brand_id**: Filter by brand
    - **category_id**: Filter by category
    - **search**: Search in title, description, and tags
    - **min_price**: Minimum base price
    - **max_price**: Maximum base price
    - **in_stock_only**: Only show products with inventory > 0
    """
    skip = (page - 1) * page_size

    products, total = product_service.get_products(
        db=db,
        skip=skip,
        limit=page_size,
        is_active=is_active,
        is_featured=is_featured,
        brand_id=brand_id,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        load_relations=True
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ProductListResponse(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific product by ID

    **Admin only**

    Includes brand and category information.
    """
    product = product_service.get_product_by_id(db, product_id, load_relations=True)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new product

    **Admin only**

    The slug will be automatically generated from the product title.
    Validates that brand and category exist if provided.
    Ensures discount logic is valid.
    """
    try:
        product = product_service.create_product(db, product_data)
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a product

    **Admin only**

    If the title is updated, the slug will be automatically regenerated.
    Validates brand and category exist if provided.
    Ensures discount logic remains valid.
    """
    try:
        product = product_service.update_product(db, product_id, product_data)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )

        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a product

    **Admin only**

    Cannot delete a product that has associated orders.
    Deleting a product will CASCADE delete all images, videos, and variants.
    Consider marking products as inactive instead of deleting them.
    """
    try:
        deleted = product_service.delete_product(db, product_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )

        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{product_id}/inventory", response_model=ProductResponse)
async def update_product_inventory(
    product_id: UUID,
    quantity_delta: int = Query(..., description="Change in inventory (positive or negative)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update product inventory count

    **Admin only**

    Use positive values to add inventory, negative values to reduce.
    Cannot reduce inventory below zero.
    """
    try:
        product = product_service.update_inventory(db, product_id, quantity_delta)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )

        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
