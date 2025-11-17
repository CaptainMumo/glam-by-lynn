"""
Product service
Business logic for product management
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from app.models.product import Product, Brand, Category
from app.schemas.product import ProductCreate, ProductUpdate, slugify


def get_product_by_id(db: Session, product_id: UUID, load_relations: bool = True) -> Optional[Product]:
    """
    Get product by ID

    Args:
        db: Database session
        product_id: Product ID
        load_relations: Whether to eagerly load brand and category

    Returns:
        Product or None if not found
    """
    query = db.query(Product)

    if load_relations:
        query = query.options(
            joinedload(Product.brand),
            joinedload(Product.category)
        )

    return query.filter(Product.id == product_id).first()


def get_product_by_slug(db: Session, slug: str, load_relations: bool = True) -> Optional[Product]:
    """Get product by slug"""
    query = db.query(Product)

    if load_relations:
        query = query.options(
            joinedload(Product.brand),
            joinedload(Product.category)
        )

    return query.filter(Product.slug == slug).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    """Get product by SKU"""
    return db.query(Product).filter(Product.sku == sku).first()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    brand_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: bool = False,
    load_relations: bool = True
) -> tuple[list[Product], int]:
    """
    Get list of products with pagination and filters

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        is_featured: Filter by featured status
        brand_id: Filter by brand
        category_id: Filter by category
        search: Search in title, description, and tags
        min_price: Minimum base price
        max_price: Maximum base price
        in_stock_only: Only show products with inventory > 0
        load_relations: Whether to eagerly load brand and category

    Returns:
        Tuple of (products list, total count)
    """
    query = db.query(Product)

    # Eagerly load relations if requested
    if load_relations:
        query = query.options(
            joinedload(Product.brand),
            joinedload(Product.category)
        )

    # Apply filters
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)

    if brand_id is not None:
        query = query.filter(Product.brand_id == brand_id)

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.title.ilike(search_term),
                Product.description.ilike(search_term),
                Product.tags.contains([search])  # PostgreSQL ARRAY contains
            )
        )

    if min_price is not None:
        query = query.filter(Product.base_price >= min_price)

    if max_price is not None:
        query = query.filter(Product.base_price <= max_price)

    if in_stock_only:
        query = query.filter(Product.inventory_count > 0)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    products = query.order_by(
        Product.is_featured.desc(),
        Product.created_at.desc()
    ).offset(skip).limit(limit).all()

    return products, total


def create_product(db: Session, product_data: ProductCreate) -> Product:
    """
    Create a new product

    Args:
        db: Database session
        product_data: Product creation data

    Returns:
        Created product

    Raises:
        ValueError: If SKU already exists, brand/category not found, or validation fails
    """
    # Check if SKU already exists
    if product_data.sku:
        existing_product = get_product_by_sku(db, product_data.sku)
        if existing_product:
            raise ValueError(f"Product with SKU '{product_data.sku}' already exists")

    # Validate brand exists if provided
    if product_data.brand_id:
        brand = db.query(Brand).filter(Brand.id == product_data.brand_id).first()
        if not brand:
            raise ValueError(f"Brand with ID {product_data.brand_id} not found")

    # Validate category exists if provided
    if product_data.category_id:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise ValueError(f"Category with ID {product_data.category_id} not found")

    # Validate discount logic
    if product_data.discount_type and not product_data.discount_value:
        raise ValueError("Discount value is required when discount type is set")
    if product_data.discount_value and not product_data.discount_type:
        raise ValueError("Discount type is required when discount value is set")

    # Generate slug from title
    slug = slugify(product_data.title)

    # Check if slug already exists and make it unique
    slug_counter = 1
    original_slug = slug
    while get_product_by_slug(db, slug, load_relations=False):
        slug = f"{original_slug}-{slug_counter}"
        slug_counter += 1

    # Create product
    product = Product(
        title=product_data.title,
        slug=slug,
        description=product_data.description,
        brand_id=product_data.brand_id,
        category_id=product_data.category_id,
        base_price=product_data.base_price,
        discount_type=product_data.discount_type,
        discount_value=product_data.discount_value,
        sku=product_data.sku,
        inventory_count=product_data.inventory_count,
        low_stock_threshold=product_data.low_stock_threshold,
        is_active=product_data.is_active,
        is_featured=product_data.is_featured,
        tags=product_data.tags or [],
        meta_title=product_data.meta_title,
        meta_description=product_data.meta_description
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    # Load relations
    return get_product_by_id(db, product.id, load_relations=True)


def update_product(
    db: Session,
    product_id: UUID,
    product_data: ProductUpdate
) -> Optional[Product]:
    """
    Update a product

    Args:
        db: Database session
        product_id: Product ID to update
        product_data: Product update data

    Returns:
        Updated product or None if not found

    Raises:
        ValueError: If new SKU conflicts, brand/category not found, or validation fails
    """
    product = get_product_by_id(db, product_id, load_relations=False)
    if not product:
        return None

    # Check if new SKU conflicts with another product
    if product_data.sku is not None and product_data.sku != product.sku:
        existing_product = get_product_by_sku(db, product_data.sku)
        if existing_product and existing_product.id != product_id:
            raise ValueError(f"Product with SKU '{product_data.sku}' already exists")
        product.sku = product_data.sku

    # Validate brand if provided
    if product_data.brand_id is not None:
        if product_data.brand_id:  # Only validate if not explicitly setting to None
            brand = db.query(Brand).filter(Brand.id == product_data.brand_id).first()
            if not brand:
                raise ValueError(f"Brand with ID {product_data.brand_id} not found")
        product.brand_id = product_data.brand_id

    # Validate category if provided
    if product_data.category_id is not None:
        if product_data.category_id:  # Only validate if not explicitly setting to None
            category = db.query(Category).filter(Category.id == product_data.category_id).first()
            if not category:
                raise ValueError(f"Category with ID {product_data.category_id} not found")
        product.category_id = product_data.category_id

    # Update title and regenerate slug if title changed
    if product_data.title and product_data.title != product.title:
        product.title = product_data.title
        product.slug = slugify(product_data.title)

    # Update discount fields with validation
    if product_data.discount_type is not None:
        product.discount_type = product_data.discount_type
    if product_data.discount_value is not None:
        product.discount_value = product_data.discount_value

    # Validate discount logic
    if product.discount_type and not product.discount_value:
        raise ValueError("Discount value is required when discount type is set")
    if product.discount_value and not product.discount_type:
        raise ValueError("Discount type is required when discount value is set")

    # Update other fields if provided
    if product_data.description is not None:
        product.description = product_data.description

    if product_data.base_price is not None:
        product.base_price = product_data.base_price

    if product_data.inventory_count is not None:
        product.inventory_count = product_data.inventory_count

    if product_data.low_stock_threshold is not None:
        product.low_stock_threshold = product_data.low_stock_threshold

    if product_data.is_active is not None:
        product.is_active = product_data.is_active

    if product_data.is_featured is not None:
        product.is_featured = product_data.is_featured

    if product_data.tags is not None:
        product.tags = product_data.tags

    if product_data.meta_title is not None:
        product.meta_title = product_data.meta_title

    if product_data.meta_description is not None:
        product.meta_description = product_data.meta_description

    db.commit()
    db.refresh(product)

    # Load relations
    return get_product_by_id(db, product_id, load_relations=True)


def delete_product(db: Session, product_id: UUID) -> bool:
    """
    Delete a product

    Args:
        db: Database session
        product_id: Product ID to delete

    Returns:
        True if deleted, False if not found

    Raises:
        ValueError: If product has associated orders
    """
    product = get_product_by_id(db, product_id, load_relations=False)
    if not product:
        return False

    # Check if product has orders (we don't want to delete products that have been ordered)
    if product.order_items.count() > 0:
        raise ValueError(
            f"Cannot delete product '{product.title}' because it has associated orders. "
            "Consider marking it as inactive instead."
        )

    # Delete will cascade to images, videos, and variants due to cascade settings
    db.delete(product)
    db.commit()

    return True


def update_inventory(db: Session, product_id: UUID, quantity_delta: int) -> Optional[Product]:
    """
    Update product inventory count

    Args:
        db: Database session
        product_id: Product ID
        quantity_delta: Change in inventory (can be negative)

    Returns:
        Updated product or None if not found

    Raises:
        ValueError: If resulting inventory would be negative
    """
    product = get_product_by_id(db, product_id, load_relations=False)
    if not product:
        return None

    new_inventory = product.inventory_count + quantity_delta
    if new_inventory < 0:
        raise ValueError(f"Insufficient inventory. Current: {product.inventory_count}, Requested: {abs(quantity_delta)}")

    product.inventory_count = new_inventory
    db.commit()
    db.refresh(product)

    return get_product_by_id(db, product_id, load_relations=True)
