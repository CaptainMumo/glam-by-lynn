"""
Category API routes
Admin-only endpoints for category management with hierarchy support
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import math

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryTreeResponse
)
from app.services import category_service

router = APIRouter(prefix="/admin/categories", tags=["admin", "categories"])


@router.get("/tree", response_model=CategoryTreeResponse)
async def get_category_tree(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get hierarchical category tree

    **Admin only**

    Returns all categories organized in a hierarchical structure with
    parent categories containing their subcategories.

    Query parameters:
    - **is_active**: Filter by active status
    """
    tree = category_service.get_category_tree(db=db, is_active=is_active)

    return CategoryTreeResponse(
        items=tree,
        total=len(tree)
    )


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category ID (null for root)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get paginated list of categories

    **Admin only**

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **is_active**: Filter by active status
    - **search**: Search in name and description
    - **parent_id**: Filter by parent category (omit for root categories)
    """
    skip = (page - 1) * page_size

    categories, total = category_service.get_categories(
        db=db,
        skip=skip,
        limit=page_size,
        is_active=is_active,
        search=search,
        parent_id=parent_id
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return CategoryListResponse(
        items=categories,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific category by ID

    **Admin only**
    """
    category = category_service.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )

    return category


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new category

    **Admin only**

    The slug will be automatically generated from the category name.
    Provide `parent_category_id` to create a subcategory.
    """
    try:
        category = category_service.create_category(db, category_data)
        return category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a category

    **Admin only**

    If the name is updated, the slug will be automatically regenerated.
    Cannot create self-referencing or circular category hierarchies.
    """
    try:
        category = category_service.update_category(db, category_id, category_data)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )

        return category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a category

    **Admin only**

    Cannot delete a category (or any subcategory) that has associated products.
    Deleting a category will CASCADE delete all its subcategories.
    """
    try:
        deleted = category_service.delete_category(db, category_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )

        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
