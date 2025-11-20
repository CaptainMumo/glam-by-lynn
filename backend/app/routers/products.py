"""Public product API routes."""
import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import ProductListResponse, ProductResponse, ProductDetailResponse
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    brand_id: Optional[UUID] = Query(None, alias="brandId", description="Filter by brand ID"),
    category_id: Optional[UUID] = Query(None, alias="categoryId", description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search in title, description, and tags"),
    min_price: Optional[float] = Query(None, ge=0, alias="minPrice", description="Minimum base price"),
    max_price: Optional[float] = Query(None, ge=0, alias="maxPrice", description="Maximum base price"),
    sort_by: str = Query("created_at", alias="sortBy", description="Sort field"),
    sort_order: str = Query("desc", alias="sortOrder", pattern="^(asc|desc)$", description="Sort order"),
    in_stock_only: bool = Query(True, alias="inStockOnly", description="Only show in-stock products"),
    db: Session = Depends(get_db),
):
    """
    Get paginated list of active products (public).

    Returns only active products that are available for purchase.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **brandId**: Filter by brand
    - **categoryId**: Filter by category
    - **search**: Search in title, description, and tags
    - **minPrice**: Minimum base price
    - **maxPrice**: Maximum base price
    - **sortBy**: Sort field (created_at, price, title, etc.)
    - **sortOrder**: Sort order (asc/desc)
    - **inStockOnly**: Only show products with inventory > 0 (default: true)
    """
    skip = (page - 1) * page_size

    products, total = product_service.get_products(
        db=db,
        skip=skip,
        limit=page_size,
        is_active=True,  # Only active products for public
        brand_id=brand_id,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        load_relations=True,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ProductListResponse(
        items=products, total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/featured", response_model=ProductListResponse)
async def list_featured_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get featured products (public).

    Returns only active, in-stock featured products.
    """
    skip = (page - 1) * page_size

    products, total = product_service.get_products(
        db=db,
        skip=skip,
        limit=page_size,
        is_active=True,
        is_featured=True,
        in_stock_only=True,
        load_relations=True,
        sort_by="created_at",
        sort_order="desc",
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ProductListResponse(
        items=products, total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/slug/{slug}", response_model=ProductDetailResponse)
async def get_product_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Get comprehensive product details by slug (public).

    Returns only active products with:
    - All product information
    - Images and videos
    - Product variants
    - Average rating and review count
    - Related products (same category/brand)
    - Recent approved reviews (10 most recent)

    This endpoint is optimized for product detail pages.
    """
    detail = product_service.get_product_detail_by_slug(db, slug)

    if not detail or not detail["product"].is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with slug '{slug}' not found",
        )

    # Build response
    product = detail["product"]
    response_data = {
        **product.__dict__,
        "images": detail["images"],
        "videos": detail["videos"],
        "variants": detail["variants"],
        "rating_summary": detail["rating_summary"],
        "related_products": detail["related_products"],
        "reviews": detail["reviews"],
    }

    return response_data


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a specific product by ID (public).

    Returns only active products. Includes brand, category, images, and variants.
    """
    product = product_service.get_product_by_id(db, product_id, load_relations=True)

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    return product
