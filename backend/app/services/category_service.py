"""
Category service
Business logic for category management with hierarchy support
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, slugify, CategoryWithSubcategories


def get_category_by_id(db: Session, category_id: UUID) -> Optional[Category]:
    """Get category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
    """Get category by slug"""
    return db.query(Category).filter(Category.slug == slug).first()


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    """Get category by name"""
    return db.query(Category).filter(Category.name == name).first()


def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    parent_id: Optional[UUID] = None
) -> tuple[list[Category], int]:
    """
    Get list of categories with pagination and filters

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        search: Search in name and description
        parent_id: Filter by parent category (None for root categories)

    Returns:
        Tuple of (categories list, total count)
    """
    query = db.query(Category)

    # Apply filters
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Category.name.ilike(search_term),
                Category.description.ilike(search_term)
            )
        )

    if parent_id is not None:
        query = query.filter(Category.parent_category_id == parent_id)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    categories = query.order_by(
        Category.display_order,
        Category.name
    ).offset(skip).limit(limit).all()

    return categories, total


def get_category_tree(db: Session, is_active: Optional[bool] = None) -> list[CategoryWithSubcategories]:
    """
    Get hierarchical category tree

    Args:
        db: Database session
        is_active: Filter by active status

    Returns:
        List of root categories with nested subcategories
    """
    query = db.query(Category)

    if is_active is not None:
        query = query.filter(Category.is_active == is_active)

    # Get all categories
    all_categories = query.order_by(Category.display_order, Category.name).all()

    # Build a mapping of category_id -> category data
    category_map: dict[UUID, CategoryWithSubcategories] = {}
    for cat in all_categories:
        category_map[cat.id] = CategoryWithSubcategories(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            image_url=cat.image_url,
            parent_category_id=cat.parent_category_id,
            display_order=cat.display_order,
            is_active=cat.is_active,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
            subcategories=[]
        )

    # Build the tree structure
    root_categories: list[CategoryWithSubcategories] = []
    for cat_id, cat_data in category_map.items():
        if cat_data.parent_category_id is None:
            # Root category
            root_categories.append(cat_data)
        else:
            # Subcategory - attach to parent
            parent = category_map.get(cat_data.parent_category_id)
            if parent:
                parent.subcategories.append(cat_data)

    return root_categories


def create_category(db: Session, category_data: CategoryCreate) -> Category:
    """
    Create a new category

    Args:
        db: Database session
        category_data: Category creation data

    Returns:
        Created category

    Raises:
        ValueError: If category with same name already exists or parent doesn't exist
    """
    # Check if category with same name exists
    existing_category = get_category_by_name(db, category_data.name)
    if existing_category:
        raise ValueError(f"Category with name '{category_data.name}' already exists")

    # Validate parent category exists if provided
    if category_data.parent_category_id:
        parent = get_category_by_id(db, category_data.parent_category_id)
        if not parent:
            raise ValueError(f"Parent category with ID {category_data.parent_category_id} not found")

    # Generate slug from name
    slug = slugify(category_data.name)

    # Check if slug already exists (shouldn't happen if name is unique, but just in case)
    slug_counter = 1
    original_slug = slug
    while get_category_by_slug(db, slug):
        slug = f"{original_slug}-{slug_counter}"
        slug_counter += 1

    # Create category
    category = Category(
        name=category_data.name,
        slug=slug,
        description=category_data.description,
        image_url=category_data.image_url,
        parent_category_id=category_data.parent_category_id,
        display_order=category_data.display_order,
        is_active=category_data.is_active
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def update_category(
    db: Session,
    category_id: UUID,
    category_data: CategoryUpdate
) -> Optional[Category]:
    """
    Update a category

    Args:
        db: Database session
        category_id: Category ID to update
        category_data: Category update data

    Returns:
        Updated category or None if not found

    Raises:
        ValueError: If new name conflicts with existing category, parent doesn't exist, or self-referencing
    """
    category = get_category_by_id(db, category_id)
    if not category:
        return None

    # Check if new name conflicts with another category
    if category_data.name and category_data.name != category.name:
        existing_category = get_category_by_name(db, category_data.name)
        if existing_category and existing_category.id != category_id:
            raise ValueError(f"Category with name '{category_data.name}' already exists")

        # Update name and regenerate slug
        category.name = category_data.name
        category.slug = slugify(category_data.name)

    # Validate parent category
    if category_data.parent_category_id is not None:
        # Check for self-referencing
        if category_data.parent_category_id == category_id:
            raise ValueError("Category cannot be its own parent")

        # Check parent exists
        parent = get_category_by_id(db, category_data.parent_category_id)
        if not parent:
            raise ValueError(f"Parent category with ID {category_data.parent_category_id} not found")

        # Check for circular reference (parent cannot be a child of this category)
        if _would_create_circular_reference(db, category_id, category_data.parent_category_id):
            raise ValueError("Cannot create circular category reference")

        category.parent_category_id = category_data.parent_category_id

    # Update other fields if provided
    if category_data.description is not None:
        category.description = category_data.description

    if category_data.image_url is not None:
        category.image_url = category_data.image_url

    if category_data.display_order is not None:
        category.display_order = category_data.display_order

    if category_data.is_active is not None:
        category.is_active = category_data.is_active

    db.commit()
    db.refresh(category)

    return category


def delete_category(db: Session, category_id: UUID) -> bool:
    """
    Delete a category (cascade deletes subcategories)

    Args:
        db: Database session
        category_id: Category ID to delete

    Returns:
        True if deleted, False if not found

    Raises:
        ValueError: If category has associated products
    """
    category = get_category_by_id(db, category_id)
    if not category:
        return False

    # Check if category or any subcategory has products
    if _has_products_recursive(db, category):
        raise ValueError(
            f"Cannot delete category '{category.name}' because it or its subcategories have associated products. "
            "Please delete or reassign products first."
        )

    # Delete will cascade to subcategories due to ondelete="CASCADE"
    db.delete(category)
    db.commit()

    return True


def _would_create_circular_reference(db: Session, category_id: UUID, new_parent_id: UUID) -> bool:
    """
    Check if setting new_parent_id as parent would create circular reference

    Args:
        db: Database session
        category_id: Category being updated
        new_parent_id: Proposed parent category ID

    Returns:
        True if would create circular reference, False otherwise
    """
    # Walk up the parent chain from new_parent_id
    current_id = new_parent_id
    visited = set()

    while current_id:
        if current_id in visited:
            # Already circular in existing structure
            return True

        if current_id == category_id:
            # Found the category we're updating - would create circular reference
            return True

        visited.add(current_id)
        parent = get_category_by_id(db, current_id)
        if not parent:
            break
        current_id = parent.parent_category_id

    return False


def _has_products_recursive(db: Session, category: Category) -> bool:
    """
    Check if category or any subcategory has products

    Args:
        db: Database session
        category: Category to check

    Returns:
        True if category or subcategories have products
    """
    # Check if this category has products
    if category.products.count() > 0:
        return True

    # Check all subcategories recursively
    for subcategory in category.subcategories:
        if _has_products_recursive(db, subcategory):
            return True

    return False
