"""User model for authentication and user management."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User model supporting both customers and admins with Google OAuth."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    phone_number = Column(String(20))
    profile_picture_url = Column(String(500))
    google_id = Column(String(255), unique=True, index=True)
    is_admin = Column(Boolean, default=False, index=True)
    admin_role = Column(
        String(50),
        CheckConstraint(
            "admin_role IN ('super_admin', 'product_manager', 'booking_manager', 'content_editor', 'artist')",
            name="users_admin_role_values",
        ),
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    orders = relationship("Order", back_populates="user", lazy="dynamic")
    bookings = relationship("Booking", back_populates="user", lazy="dynamic")
    reviews = relationship("Review", back_populates="user", lazy="dynamic")
    cart = relationship("Cart", back_populates="user", uselist=False)
    wishlists = relationship("Wishlist", back_populates="user", lazy="dynamic")
    admin_activity_logs = relationship(
        "AdminActivityLog", back_populates="admin_user", lazy="dynamic"
    )

    __table_args__ = (
        CheckConstraint(
            "(is_admin = FALSE AND admin_role IS NULL) OR (is_admin = TRUE AND admin_role IS NOT NULL)",
            name="users_admin_role_check",
        ),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, is_admin={self.is_admin})>"
