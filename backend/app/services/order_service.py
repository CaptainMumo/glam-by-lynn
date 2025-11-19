"""Order service for business logic."""
import secrets
import string
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.order import Cart, CartItem, Order, OrderItem
from app.models.product import Product, ProductVariant
from app.models.user import User
from app.schemas.order import DeliveryInfo, GuestInfo
from app.services import promo_code_service


def generate_order_number(db: Session) -> str:
    """
    Generate a unique order number.

    Format: ORD-YYYYMMDD-XXXXX where X is random alphanumeric
    """
    date_part = datetime.utcnow().strftime("%Y%m%d")

    # Generate random 5-character suffix
    while True:
        random_part = "".join(
            secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5)
        )
        order_number = f"ORD-{date_part}-{random_part}"

        # Check if order number already exists
        existing = db.query(Order).filter(Order.order_number == order_number).first()
        if not existing:
            return order_number


def validate_cart_and_calculate_totals(
    db: Session, cart: Cart
) -> Tuple[bool, str, Decimal, List[dict]]:
    """
    Validate cart items and calculate order totals.

    Args:
        db: Database session
        cart: User's cart

    Returns:
        Tuple of (is_valid, error_message, subtotal, items_data)
    """
    if not cart or cart.cart_items.count() == 0:
        return False, "Cart is empty", Decimal(0), []

    subtotal = Decimal(0)
    items_data = []

    for cart_item in cart.cart_items:
        # Get product
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()

        if not product:
            return False, f"Product not found", Decimal(0), []

        if not product.is_active:
            return False, f"Product '{product.title}' is no longer available", Decimal(0), []

        # Check stock availability
        if product.inventory_count < cart_item.quantity:
            return (
                False,
                f"Insufficient stock for '{product.title}'. Available: {product.inventory_count}",
                Decimal(0),
                [],
            )

        # Get variant if specified
        variant = None
        if cart_item.product_variant_id:
            variant = (
                db.query(ProductVariant)
                .filter(ProductVariant.id == cart_item.product_variant_id)
                .first()
            )

            if not variant:
                return False, f"Product variant not found", Decimal(0), []

            if variant.inventory_count < cart_item.quantity:
                return (
                    False,
                    f"Insufficient stock for '{product.title}' variant. Available: {variant.inventory_count}",
                    Decimal(0),
                    [],
                )

        # Calculate price (base price + variant adjustment)
        unit_price = product.base_price + (variant.price_adjustment if variant else Decimal(0))

        # Calculate item total
        item_total = unit_price * cart_item.quantity
        subtotal += item_total

        # Store item data
        items_data.append({
            "product_id": product.id,
            "product_variant_id": variant.id if variant else None,
            "product_title": product.title,
            "product_sku": variant.sku if variant else product.sku,
            "quantity": cart_item.quantity,
            "unit_price": unit_price,
            "total_price": item_total,
        })

    return True, "", subtotal, items_data


def calculate_delivery_fee(delivery_county: str) -> Decimal:
    """
    Calculate delivery fee based on county.

    For now, returns fixed fee. Can be enhanced later with location-based pricing.
    """
    # TODO: Implement location-based delivery fee calculation
    # For now, return fixed fee (can be 0 for local, higher for distant counties)
    return Decimal("200.00")  # Fixed fee for now


def create_order(
    db: Session,
    user: Optional[User],
    guest_info: Optional[GuestInfo],
    delivery_info: DeliveryInfo,
    promo_code: Optional[str],
    payment_method: Optional[str],
) -> Tuple[bool, str, Optional[Order]]:
    """
    Create a new order from user's cart.

    Args:
        db: Database session
        user: Authenticated user (None for guest checkout)
        guest_info: Guest customer info (required if user is None)
        delivery_info: Delivery address
        promo_code: Optional promo code
        payment_method: Payment method chosen

    Returns:
        Tuple of (success, message, order)
    """
    # Validate user or guest info
    if not user and not guest_info:
        return False, "Either user or guest information required", None

    # Get cart (only for authenticated users)
    cart = None
    if user:
        cart = db.query(Cart).filter(Cart.user_id == user.id).first()
        if not cart or cart.cart_items.count() == 0:
            return False, "Cart is empty", None
    else:
        # For guest checkout, we would need to pass cart items directly
        # For now, require authentication
        return False, "Guest checkout not yet implemented", None

    # Validate cart and calculate subtotal
    is_valid, error_msg, subtotal, items_data = validate_cart_and_calculate_totals(db, cart)
    if not is_valid:
        return False, error_msg, None

    # Calculate delivery fee
    delivery_fee = calculate_delivery_fee(delivery_info.county)

    # Calculate order total
    order_total = subtotal + delivery_fee

    # Apply promo code if provided
    discount_amount = Decimal(0)
    promo_code_id = None

    if promo_code:
        is_valid, message, discount, promo_obj = promo_code_service.validate_promo_code(
            db, promo_code, order_total
        )

        if not is_valid:
            return False, message, None

        discount_amount = discount or Decimal(0)
        promo_code_id = promo_obj.id if promo_obj else None

        # Recalculate total with discount
        order_total -= discount_amount

    # Generate unique order number
    order_number = generate_order_number(db)

    # Create order
    order = Order(
        order_number=order_number,
        user_id=user.id if user else None,
        guest_email=guest_info.email if guest_info else None,
        guest_name=guest_info.name if guest_info else None,
        guest_phone=guest_info.phone if guest_info else None,
        delivery_county=delivery_info.county,
        delivery_town=delivery_info.town,
        delivery_address=delivery_info.address,
        subtotal=subtotal,
        discount_amount=discount_amount,
        promo_code_id=promo_code_id,
        delivery_fee=delivery_fee,
        total_amount=order_total,
        payment_method=payment_method,
        status="pending",
    )

    db.add(order)
    db.flush()  # Get order ID

    # Create order items and update stock
    for item_data in items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product_id"],
            product_variant_id=item_data["product_variant_id"],
            product_title=item_data["product_title"],
            product_sku=item_data["product_sku"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            discount=Decimal(0),
            total_price=item_data["total_price"],
        )
        db.add(order_item)

        # Update stock
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        product.inventory_count -= item_data["quantity"]

        if item_data["product_variant_id"]:
            variant = (
                db.query(ProductVariant)
                .filter(ProductVariant.id == item_data["product_variant_id"])
                .first()
            )
            variant.inventory_count -= item_data["quantity"]

    # Increment promo code usage if used
    if promo_code_id:
        promo_code_service.increment_usage(db, promo_code_id)

    # Clear cart
    if cart:
        for cart_item in cart.cart_items:
            db.delete(cart_item)

    # Commit transaction
    db.commit()
    db.refresh(order)

    # TODO: Send order confirmation email

    return True, "Order created successfully", order


def get_order_by_id(db: Session, order_id: UUID) -> Optional[Order]:
    """Get an order by ID."""
    return db.query(Order).filter(Order.id == order_id).first()


def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
    """Get an order by order number."""
    return db.query(Order).filter(Order.order_number == order_number).first()


def get_user_orders(
    db: Session, user_id: UUID, skip: int = 0, limit: int = 20
) -> Tuple[List[Order], int]:
    """
    Get orders for a user with pagination.

    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (orders list, total count)
    """
    query = db.query(Order).filter(Order.user_id == user_id)

    total = query.count()

    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    return orders, total
