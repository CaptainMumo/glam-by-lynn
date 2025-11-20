"""Shopping cart API routes."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse
from app.services import cart_service

router = APIRouter(tags=["Shopping Cart"])


@router.get("/cart", response_model=CartResponse)
async def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's shopping cart (authenticated).

    Returns the user's cart with all items, including:
    - Product details
    - Variant details (if applicable)
    - Calculated prices (unit price, subtotal)
    - Stock availability status
    - Total amount and item count

    If user doesn't have a cart yet, creates an empty one.
    """
    cart = cart_service.get_cart_with_items(db, current_user.id)

    if not cart:
        # Create empty cart if doesn't exist
        cart = cart_service.get_or_create_cart(db, current_user.id)
        # Reload with items relationship
        cart = cart_service.get_cart_with_items(db, current_user.id)

    # Convert cart_items to list for Pydantic
    # cart_items is lazy="dynamic", but service loads items into _items_list
    cart_dict = {
        "id": cart.id,
        "user_id": cart.user_id,
        "created_at": cart.created_at,
        "updated_at": cart.updated_at,
        "items": getattr(cart, '_items_list', []),
    }

    return CartResponse(**cart_dict)


@router.post("/cart/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add item to cart (authenticated).

    **Request:**
    - productId: Product UUID
    - productVariantId: Optional variant UUID
    - quantity: Quantity to add (must be > 0)

    **Validation:**
    - Checks product exists and is active
    - Validates stock availability
    - If item already in cart, increases quantity
    - If new item, adds to cart

    **Returns:**
    - Cart item with product details
    - Calculated prices
    - Stock availability status

    **Errors:**
    - 400: Insufficient stock or product not available
    - 401: Authentication required
    """
    try:
        cart_item = cart_service.add_item_to_cart(
            db=db,
            user_id=current_user.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            product_variant_id=item_data.product_variant_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Reload with product and variant details
    from sqlalchemy.orm import joinedload
    from app.models.order import CartItem

    cart_item = (
        db.query(CartItem)
        .options(
            joinedload(CartItem.product),
            joinedload(CartItem.product_variant),
        )
        .filter(CartItem.id == cart_item.id)
        .first()
    )

    return cart_item


@router.put("/cart/items/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: UUID,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update cart item quantity (authenticated).

    **Request:**
    - quantity: New quantity (must be > 0)

    **Validation:**
    - Verifies item belongs to user's cart
    - Validates stock availability for new quantity

    **Returns:**
    - Updated cart item

    **Errors:**
    - 400: Insufficient stock
    - 404: Cart item not found or doesn't belong to user
    """
    try:
        cart_item = cart_service.update_cart_item_quantity(
            db=db,
            user_id=current_user.id,
            cart_item_id=cart_item_id,
            quantity=item_data.quantity,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with ID {cart_item_id} not found",
        )

    # Reload with product and variant details
    from sqlalchemy.orm import joinedload
    from app.models.order import CartItem

    cart_item = (
        db.query(CartItem)
        .options(
            joinedload(CartItem.product),
            joinedload(CartItem.product_variant),
        )
        .filter(CartItem.id == cart_item.id)
        .first()
    )

    return cart_item


@router.delete("/cart/items/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart_item(
    cart_item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove item from cart (authenticated).

    **Validation:**
    - Verifies item belongs to user's cart

    **Returns:**
    - 204 No Content on success

    **Errors:**
    - 404: Cart item not found or doesn't belong to user
    """
    success = cart_service.remove_cart_item(db, current_user.id, cart_item_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with ID {cart_item_id} not found",
        )

    return None


@router.delete("/cart", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Clear all items from cart (authenticated).

    Removes all items from the user's cart.
    The cart itself remains (empty).

    **Returns:**
    - 204 No Content on success
    """
    cart_service.clear_cart(db, current_user.id)
    return None
