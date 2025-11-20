"""
FastAPI dependencies for authentication and authorization
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User


class HTTPBearerUnauthorized(HTTPBearer):
    """Custom HTTPBearer that raises 401 instead of 403 for missing credentials."""

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            if e.status_code == 403:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            raise


# Security scheme for Bearer token
security = HTTPBearerUnauthorized()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        Current user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Verify token
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user ID from token
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    try:
        user = db.query(User).filter(User.id == UUID(user_id)).first()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get the current authenticated user from JWT token

    Returns None if no token is provided or token is invalid.
    Does not raise HTTPException for missing/invalid tokens.

    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session

    Returns:
        Current user object or None
    """
    if not credentials:
        return None

    token = credentials.credentials

    # Verify token
    payload = verify_token(token, token_type="access")
    if not payload:
        return None

    # Get user ID from token
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        return None

    # Get user from database
    try:
        user = db.query(User).filter(User.id == UUID(user_id)).first()
    except ValueError:
        return None

    if not user or not user.is_active:
        return None

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure user is active

    Args:
        current_user: Current authenticated user

    Returns:
        Active user object

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure user is an admin

    Args:
        current_user: Current authenticated user

    Returns:
        Admin user object

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_super_admin(
    current_user: User = Depends(get_current_admin_user)
) -> User:
    """
    Dependency to ensure user is a super admin

    Args:
        current_user: Current admin user

    Returns:
        Super admin user object

    Raises:
        HTTPException: If user is not a super admin
    """
    if current_user.admin_role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


def require_role(allowed_roles: List[str]):
    """
    Factory function to create role-based dependency

    Args:
        allowed_roles: List of allowed admin roles

    Returns:
        Dependency function that checks for required roles

    Example:
        @router.get("/products", dependencies=[Depends(require_role(["product_manager", "super_admin"]))])
    """
    async def role_checker(current_user: User = Depends(get_current_admin_user)) -> User:
        if current_user.admin_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {' or '.join(allowed_roles)}"
            )
        return current_user

    return role_checker


async def get_product_manager(
    current_user: User = Depends(get_current_admin_user)
) -> User:
    """
    Dependency to ensure user has product management permissions

    Args:
        current_user: Current admin user

    Returns:
        Product manager or super admin user

    Raises:
        HTTPException: If user doesn't have product management permissions
    """
    if current_user.admin_role not in ["product_manager", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product management permissions required"
        )
    return current_user


async def get_booking_manager(
    current_user: User = Depends(get_current_admin_user)
) -> User:
    """
    Dependency to ensure user has booking management permissions

    Args:
        current_user: Current admin user

    Returns:
        Booking manager or super admin user

    Raises:
        HTTPException: If user doesn't have booking management permissions
    """
    if current_user.admin_role not in ["booking_manager", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Booking management permissions required"
        )
    return current_user


async def get_content_editor(
    current_user: User = Depends(get_current_admin_user)
) -> User:
    """
    Dependency to ensure user has content editing permissions

    Args:
        current_user: Current admin user

    Returns:
        Content editor or super admin user

    Raises:
        HTTPException: If user doesn't have content editing permissions
    """
    if current_user.admin_role not in ["content_editor", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Content editing permissions required"
        )
    return current_user


async def get_artist(
    current_user: User = Depends(get_current_admin_user)
) -> User:
    """
    Dependency to ensure user is an artist

    Args:
        current_user: Current admin user

    Returns:
        Artist or super admin user

    Raises:
        HTTPException: If user is not an artist
    """
    if current_user.admin_role not in ["artist", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Artist permissions required"
        )
    return current_user
