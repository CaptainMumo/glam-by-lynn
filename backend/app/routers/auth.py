"""
Authentication router
Handles user authentication, token management, and Google OAuth
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.dependencies import get_current_user, get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    GoogleAuthRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google-login", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def google_auth(
    auth_data: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Google OAuth authentication endpoint
    Creates or retrieves user based on Google account info
    Also links any guest orders/bookings if user previously placed orders as guest

    Args:
        auth_data: Google authentication data (email, googleId, name, image)
        db: Database session

    Returns:
        User information (guest data automatically linked if applicable)

    Raises:
        HTTPException: If authentication fails
    """
    # Use user service to handle OAuth login with guest data linking
    user, created, link_stats = user_service.get_or_create_user_from_oauth(
        db=db,
        email=auth_data.email,
        google_id=auth_data.google_id,
        name=auth_data.name,
        image=auth_data.image
    )

    # Ensure user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    Args:
        current_user: Current authenticated user from token

    Returns:
        User information
    """
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    Args:
        token_data: Refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    from uuid import UUID
    try:
        user = db.query(User).filter(User.id == UUID(user_id)).first()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user
    Note: With JWT, logout is handled client-side by removing tokens
    This endpoint can be used for logging/analytics

    Args:
        current_user: Current authenticated user

    Returns:
        Success message
    """
    # In a JWT-based system, logout is primarily client-side
    # However, this endpoint can be used for:
    # 1. Logging logout events
    # 2. Invalidating refresh tokens (if stored in DB)
    # 3. Analytics

    return {
        "message": "Successfully logged out",
        "user_id": str(current_user.id)
    }


@router.post("/token", response_model=TokenResponse)
async def create_tokens_for_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Create access and refresh tokens for a user (internal use)
    This endpoint is typically called after successful Google OAuth

    Args:
        user_id: User ID to create tokens for
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If user not found
    """
    from uuid import UUID
    try:
        user = db.query(User).filter(User.id == UUID(user_id)).first()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/guest", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_guest_user(
    email: str,
    name: str = None,
    db: Session = Depends(get_db)
):
    """
    Create a guest user account (without Google OAuth)
    Used for checkout and booking without registration

    Args:
        email: Guest email address
        name: Optional guest name
        db: Database session

    Returns:
        Created guest user

    Raises:
        HTTPException: If user with email already exists
    """
    try:
        guest_user = user_service.create_guest_user(
            db=db,
            email=email,
            name=name
        )
        return guest_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/link-guest-data")
async def link_guest_data(
    guest_email: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Manually link guest orders and bookings to authenticated user account
    Useful for cases where email doesn't match exactly

    Args:
        guest_email: Email address used for guest orders/bookings
        current_user: Current authenticated user
        db: Database session

    Returns:
        Link statistics

    Raises:
        HTTPException: If linking fails
    """
    try:
        link_stats = user_service.link_guest_data_to_user(
            db=db,
            user_id=current_user.id,
            guest_email=guest_email
        )
        return {
            "message": "Guest data successfully linked",
            **link_stats
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
