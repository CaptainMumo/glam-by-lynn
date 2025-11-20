"""Cart service for business logic."""
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.order import Cart, CartItem
from app.models.product import Product, ProductVariant


def get_or_create_cart(db: Session, user_id: UUID) -> Cart:
    """
    Get user's cart or create if doesn't exist.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User's cart
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


def get_cart_with_items(db: Session, user_id: UUID) -> Optional[Cart]:
    """
    Get user's cart with all items and product details.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Cart with items or None if cart doesn't exist
    """
    # Get cart (cart_items is lazy="dynamic" so it returns a query)
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if cart:
        # Manually load items with product and variant details
        # Since cart_items is dynamic, we need to query it separately
        cart._items_list = (
            cart.cart_items.options(
                joinedload(CartItem.product),
                joinedload(CartItem.product_variant),
            ).all()
        )

    return cart


def validate_stock(
    db: Session, product_id: UUID, quantity: int, product_variant_id: Optional[UUID] = None
) -> Tuple[bool, str]:
    """
    Validate stock availability for a product/variant.

    Args:
        db: Database session
        product_id: Product ID
        quantity: Requested quantity
        product_variant_id: Optional variant ID

    Returns:
        Tuple of (is_available, error_message)
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return False, "Product not found"

    if not product.is_active:
        return False, "Product is not available"

    # Check variant stock if variant specified
    if product_variant_id:
        variant = db.query(ProductVariant).filter(ProductVariant.id == product_variant_id).first()
        if not variant:
            return False, "Product variant not found"

        if variant.inventory_count < quantity:
            return False, f"Insufficient stock. Only {variant.inventory_count} available"
    else:
        # Check product stock
        if product.inventory_count < quantity:
            return False, f"Insufficient stock. Only {product.inventory_count} available"

    return True, ""


def add_item_to_cart(
    db: Session,
    user_id: UUID,
    product_id: UUID,
    quantity: int,
    product_variant_id: Optional[UUID] = None,
) -> CartItem:
    """
    Add item to cart or update quantity if already exists.

    Args:
        db: Database session
        user_id: User ID
        product_id: Product ID
        quantity: Quantity to add
        product_variant_id: Optional variant ID

    Returns:
        Cart item

    Raises:
        ValueError: If stock validation fails
    """
    # Validate stock
    is_available, error_msg = validate_stock(db, product_id, quantity, product_variant_id)
    if not is_available:
        raise ValueError(error_msg)

    # Get or create cart
    cart = get_or_create_cart(db, user_id)

    # Check if item already exists in cart
    existing_item = (
        db.query(CartItem)
        .filter(
            and_(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id,
                CartItem.product_variant_id == product_variant_id,
            )
        )
        .first()
    )

    if existing_item:
        # Update quantity
        new_quantity = existing_item.quantity + quantity

        # Validate new quantity against stock
        is_available, error_msg = validate_stock(db, product_id, new_quantity, product_variant_id)
        if not is_available:
            raise ValueError(error_msg)

        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Create new cart item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            product_variant_id=product_variant_id,
            quantity=quantity,
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item


def update_cart_item_quantity(
    db: Session, user_id: UUID, cart_item_id: UUID, quantity: int
) -> Optional[CartItem]:
    """
    Update cart item quantity.

    Args:
        db: Database session
        user_id: User ID (for authorization)
        cart_item_id: Cart item ID
        quantity: New quantity

    Returns:
        Updated cart item or None if not found

    Raises:
        ValueError: If stock validation fails or item doesn't belong to user
    """
    # Get cart item and verify it belongs to user's cart
    cart_item = (
        db.query(CartItem)
        .join(Cart)
        .filter(and_(CartItem.id == cart_item_id, Cart.user_id == user_id))
        .first()
    )

    if not cart_item:
        return None

    # Validate new quantity against stock
    is_available, error_msg = validate_stock(
        db, cart_item.product_id, quantity, cart_item.product_variant_id
    )
    if not is_available:
        raise ValueError(error_msg)

    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_cart_item(db: Session, user_id: UUID, cart_item_id: UUID) -> bool:
    """
    Remove item from cart.

    Args:
        db: Database session
        user_id: User ID (for authorization)
        cart_item_id: Cart item ID

    Returns:
        True if removed, False if not found
    """
    # Get cart item and verify it belongs to user's cart
    cart_item = (
        db.query(CartItem)
        .join(Cart)
        .filter(and_(CartItem.id == cart_item_id, Cart.user_id == user_id))
        .first()
    )

    if not cart_item:
        return False

    db.delete(cart_item)
    db.commit()
    return True


def clear_cart(db: Session, user_id: UUID) -> bool:
    """
    Clear all items from user's cart.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if cart was cleared, False if cart doesn't exist
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        return False

    # Delete all cart items
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return True
