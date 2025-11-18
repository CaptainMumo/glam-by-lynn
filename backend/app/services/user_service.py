"""
User service
Business logic for user management, guest users, and data linking
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.models.order import Order, Cart
from app.models.booking import Booking


def create_guest_user(
    db: Session,
    email: str,
    name: Optional[str] = None
) -> User:
    """
    Create a guest user (without Google OAuth)

    Args:
        db: Database session
        email: User email
        name: Optional user name

    Returns:
        Created guest user

    Raises:
        ValueError: If user with email already exists
    """
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise ValueError(f"User with email {email} already exists")

    # Create guest user (google_id = NULL)
    guest_user = User(
        email=email,
        name=name,
        google_id=None,  # Guest users don't have Google ID
        is_active=True,
        is_admin=False
    )

    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)

    return guest_user


def link_guest_data_to_user(
    db: Session,
    user_id: UUID,
    guest_email: str
) -> dict:
    """
    Link guest orders and bookings to registered user

    When a guest user registers with Google OAuth, this function:
    1. Finds all orders placed by guest (by email)
    2. Finds all bookings made by guest (by email)
    3. Links them to the authenticated user account

    Args:
        db: Database session
        user_id: Authenticated user ID to link data to
        guest_email: Email address used for guest orders/bookings

    Returns:
        Dictionary with link statistics
    """
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    # Find all guest orders with this email
    guest_orders = db.query(Order).filter(
        Order.user_id == None,  # Guest orders have NULL user_id
        Order.guest_email == guest_email
    ).all()

    # Find all guest bookings with this email
    guest_bookings = db.query(Booking).filter(
        Booking.user_id == None,  # Guest bookings have NULL user_id
        Booking.guest_email == guest_email
    ).all()

    # Note: Carts are user-only (no guest carts in the system)
    # The Cart model requires user_id and doesn't support guest_email
    guest_carts = []

    # Link orders to user
    orders_linked = 0
    for order in guest_orders:
        order.user_id = user_id
        orders_linked += 1

    # Link bookings to user
    bookings_linked = 0
    for booking in guest_bookings:
        booking.user_id = user_id
        bookings_linked += 1

    # Link carts to user
    carts_linked = 0
    for cart in guest_carts:
        cart.user_id = user_id
        cart.guest_email = None  # Clear guest email
        carts_linked += 1

    db.commit()

    return {
        "user_id": str(user_id),
        "guest_email": guest_email,
        "orders_linked": orders_linked,
        "bookings_linked": bookings_linked,
        "carts_linked": carts_linked,
        "total_items_linked": orders_linked + bookings_linked + carts_linked
    }


def get_or_create_user_from_oauth(
    db: Session,
    email: str,
    google_id: str,
    name: Optional[str] = None,
    image: Optional[str] = None
) -> tuple[User, bool, dict]:
    """
    Get or create user from Google OAuth
    Also handles guest data linking

    Args:
        db: Database session
        email: User email from Google
        google_id: Google ID
        name: User name from Google
        image: Profile image URL from Google

    Returns:
        Tuple of (user, created, link_stats)
        - user: User object
        - created: Whether user was newly created
        - link_stats: Guest data linking statistics (if applicable)
    """
    created = False
    link_stats = {}

    # Check if user exists by Google ID
    user = db.query(User).filter(User.google_id == google_id).first()

    if user:
        # User exists, update profile if needed
        if name and user.full_name != name:
            user.full_name = name
        if image and user.profile_picture_url != image:
            user.profile_picture_url = image
        db.commit()
        db.refresh(user)
        return user, created, link_stats

    # Check if user exists by email (could be guest user)
    user = db.query(User).filter(User.email == email).first()

    if user:
        # Existing user (possibly guest), update with Google ID
        user.google_id = google_id
        if name:
            user.full_name = name
        if image:
            user.profile_picture_url = image
        db.commit()
        db.refresh(user)

        # If this was a guest user, link their data
        if not user.google_id:  # Was guest before
            link_stats = link_guest_data_to_user(db, user.id, email)

        return user, created, link_stats

    # Create new user
    user = User(
        email=email,
        google_id=google_id,
        full_name=name,
        profile_picture_url=image,
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    created = True

    # Check if there are guest orders/bookings with this email
    link_stats = link_guest_data_to_user(db, user.id, email)

    return user, created, link_stats


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Get user by Google ID"""
    return db.query(User).filter(User.google_id == google_id).first()
