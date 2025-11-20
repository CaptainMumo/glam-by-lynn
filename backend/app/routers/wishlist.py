"""Wishlist API routes."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.wishlist import WishlistItemCreate, WishlistItemResponse, WishlistResponse
from app.services import wishlist_service

router = APIRouter(tags=["Wishlist"])


@router.get("/wishlist", response_model=WishlistResponse)
async def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's wishlist (authenticated).

    Returns the user's wishlist with all saved products, including:
    - Product details (title, price, inventory)
    - Date added
    - Product availability status

    **Returns:**
    - List of wishlist items (newest first)
    - Total count
    """
    items = wishlist_service.get_user_wishlist(db, current_user.id)

    return WishlistResponse(items=items, total=len(items))


@router.post("/wishlist", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    item_data: WishlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add product to wishlist (authenticated).

    **Request:**
    - productId: Product UUID

    **Validation:**
    - Checks product exists and is active
    - Prevents duplicate entries (one product per wishlist)

    **Returns:**
    - Created wishlist item with product details

    **Errors:**
    - 400: Product not found, not available, or already in wishlist
    - 401: Authentication required
    """
    try:
        wishlist_item = wishlist_service.add_to_wishlist(
            db=db,
            user_id=current_user.id,
            product_id=item_data.product_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return wishlist_item


@router.delete("/wishlist/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove product from wishlist (authenticated).

    **Parameters:**
    - product_id: Product UUID to remove

    **Returns:**
    - 204 No Content on success

    **Errors:**
    - 404: Product not in wishlist
    """
    success = wishlist_service.remove_from_wishlist(db, current_user.id, product_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found in wishlist",
        )

    return None


@router.get("/wishlist/check/{product_id}")
async def check_in_wishlist(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check if product is in user's wishlist (authenticated).

    Useful for UI to show wishlist button state.

    **Returns:**
    - inWishlist: Boolean indicating if product is saved
    """
    in_wishlist = wishlist_service.is_in_wishlist(db, current_user.id, product_id)

    return {"inWishlist": in_wishlist}
