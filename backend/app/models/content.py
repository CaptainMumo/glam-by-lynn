"""Content-related models including reviews, gallery posts, testimonials, and vision registrations."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Review(Base):
    """Product reviews and ratings."""

    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"))
    rating = Column(Integer, nullable=False, index=True)
    review_text = Column(Text)
    is_verified_purchase = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False, index=True)
    helpful_count = Column(Integer, default=0)
    admin_reply = Column(Text)
    admin_reply_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    order = relationship("Order", back_populates="reviews")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="reviews_rating_check"),
        CheckConstraint("helpful_count >= 0", name="reviews_helpful_count_check"),
        UniqueConstraint("product_id", "user_id", name="reviews_unique_product_user"),
    )

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating})>"


class GalleryPost(Base):
    """Gallery/social media posts."""

    __tablename__ = "gallery_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    media_type = Column(String(20), nullable=False, index=True)
    media_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    caption = Column(Text)
    tags = Column(ARRAY(Text))
    source_type = Column(String(20), index=True)
    is_featured = Column(Boolean, default=False, index=True)
    display_order = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint("media_type IN ('image', 'video')", name="gallery_posts_media_type_check"),
        CheckConstraint(
            "source_type IN ('instagram', 'tiktok', 'original')",
            name="gallery_posts_source_type_check",
        ),
        Index("idx_gallery_posts_tags", "tags", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<GalleryPost(id={self.id}, media_type={self.media_type})>"


class Testimonial(Base):
    """Customer testimonials."""

    __tablename__ = "testimonials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_name = Column(String(255), nullable=False)
    customer_photo_url = Column(String(500))
    location = Column(String(100))
    rating = Column(Integer, nullable=False, index=True)
    testimonial_text = Column(Text, nullable=False)
    related_service_id = Column(
        UUID(as_uuid=True), ForeignKey("service_packages.id", ondelete="SET NULL")
    )
    related_product_id = Column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL")
    )
    is_featured = Column(Boolean, default=False, index=True)
    is_approved = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    related_service = relationship("ServicePackage", back_populates="testimonials")
    related_product = relationship("Product", back_populates="testimonials")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="testimonials_rating_check"),
    )

    def __repr__(self) -> str:
        return f"<Testimonial(id={self.id}, customer_name={self.customer_name}, rating={self.rating})>"


class VisionRegistration(Base):
    """2026 vision interest registrations."""

    __tablename__ = "vision_registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    location = Column(String(100), index=True)
    interested_in_salon = Column(Boolean, default=False)
    interested_in_barbershop = Column(Boolean, default=False)
    interested_in_spa = Column(Boolean, default=False)
    interested_in_mobile_van = Column(Boolean, default=False)
    additional_comments = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        Index(
            "idx_vision_registrations_salon",
            "interested_in_salon",
            postgresql_where="interested_in_salon = TRUE",
        ),
        Index(
            "idx_vision_registrations_barbershop",
            "interested_in_barbershop",
            postgresql_where="interested_in_barbershop = TRUE",
        ),
        Index(
            "idx_vision_registrations_spa",
            "interested_in_spa",
            postgresql_where="interested_in_spa = TRUE",
        ),
        Index(
            "idx_vision_registrations_van",
            "interested_in_mobile_van",
            postgresql_where="interested_in_mobile_van = TRUE",
        ),
    )

    def __repr__(self) -> str:
        return f"<VisionRegistration(id={self.id}, name={self.full_name}, email={self.email})>"


class AdminActivityLog(Base):
    """Audit trail for admin actions."""

    __tablename__ = "admin_activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    admin_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    details = Column(JSONB)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    admin_user = relationship("User", back_populates="admin_activity_logs")

    __table_args__ = (
        Index("idx_admin_activity_logs_entity", "entity_type", "entity_id"),
        Index("idx_admin_activity_logs_details", "details", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<AdminActivityLog(id={self.id}, action={self.action}, admin_user_id={self.admin_user_id})>"
