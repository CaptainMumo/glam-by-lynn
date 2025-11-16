"""Order-related models including orders, order items, carts, cart items, promo codes, and wishlists."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PromoCode(Base):
    """Discount promo codes."""

    __tablename__ = "promo_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    discount_type = Column(String(20), nullable=False)
    discount_value = Column(Numeric(10, 2), nullable=False)
    min_order_amount = Column(Numeric(10, 2))
    max_discount_amount = Column(Numeric(10, 2))
    usage_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    orders = relationship("Order", back_populates="promo_code", lazy="dynamic")

    __table_args__ = (
        CheckConstraint(
            "discount_type IN ('percentage', 'fixed')", name="promo_codes_discount_type_check"
        ),
        CheckConstraint("discount_value > 0", name="promo_codes_discount_value_check"),
        CheckConstraint("min_order_amount >= 0", name="promo_codes_min_order_check"),
        CheckConstraint("max_discount_amount >= 0", name="promo_codes_max_discount_check"),
        CheckConstraint("usage_limit > 0", name="promo_codes_usage_limit_check"),
        CheckConstraint("usage_count >= 0", name="promo_codes_usage_count_check"),
        CheckConstraint(
            "valid_until IS NULL OR valid_from IS NULL OR valid_until > valid_from",
            name="promo_codes_date_range_check",
        ),
        CheckConstraint(
            "usage_limit IS NULL OR usage_count <= usage_limit",
            name="promo_codes_usage_check",
        ),
        Index("idx_promo_codes_valid_dates", "valid_from", "valid_until"),
    )

    def __repr__(self) -> str:
        return f"<PromoCode(id={self.id}, code={self.code})>"


class Order(Base):
    """Customer orders."""

    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    guest_email = Column(String(255), index=True)
    guest_name = Column(String(255))
    guest_phone = Column(String(20))
    delivery_county = Column(String(100))
    delivery_town = Column(String(100))
    delivery_address = Column(Text)
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    promo_code_id = Column(
        UUID(as_uuid=True), ForeignKey("promo_codes.id", ondelete="SET NULL")
    )
    delivery_fee = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50))
    payment_confirmed = Column(Boolean, default=False, index=True)
    payment_confirmed_at = Column(DateTime(timezone=True))
    status = Column(String(30), nullable=False, default="pending", index=True)
    tracking_number = Column(String(100))
    admin_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="orders")
    promo_code = relationship("PromoCode", back_populates="orders")
    order_items = relationship(
        "OrderItem", back_populates="order", lazy="dynamic", cascade="all, delete-orphan"
    )
    reviews = relationship("Review", back_populates="order", lazy="dynamic")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'payment_confirmed', 'processing', 'shipped', 'delivered', 'cancelled')",
            name="orders_status_check",
        ),
        CheckConstraint("subtotal >= 0", name="orders_subtotal_check"),
        CheckConstraint("discount_amount >= 0", name="orders_discount_amount_check"),
        CheckConstraint("delivery_fee >= 0", name="orders_delivery_fee_check"),
        CheckConstraint("total_amount >= 0", name="orders_total_amount_check"),
        CheckConstraint(
            """
            user_id IS NOT NULL OR
            (guest_email IS NOT NULL AND guest_name IS NOT NULL AND guest_phone IS NOT NULL)
            """,
            name="orders_user_or_guest_check",
        ),
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"


class OrderItem(Base):
    """Items in each order (snapshot at time of purchase)."""

    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), index=True
    )
    product_variant_id = Column(
        UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="SET NULL")
    )
    product_title = Column(String(500), nullable=False)
    product_sku = Column(String(100))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    product_variant = relationship("ProductVariant", back_populates="order_items")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="order_items_quantity_check"),
        CheckConstraint("unit_price >= 0", name="order_items_unit_price_check"),
        CheckConstraint("discount >= 0", name="order_items_discount_check"),
        CheckConstraint("total_price >= 0", name="order_items_total_price_check"),
    )

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, product_title={self.product_title}, quantity={self.quantity})>"


class Cart(Base):
    """User shopping carts."""

    __tablename__ = "carts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="cart")
    cart_items = relationship(
        "CartItem", back_populates="cart", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Cart(id={self.id}, user_id={self.user_id})>"


class CartItem(Base):
    """Items in shopping carts."""

    __tablename__ = "cart_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    cart_id = Column(
        UUID(as_uuid=True),
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_variant_id = Column(
        UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE")
    )
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    product_variant = relationship("ProductVariant", back_populates="cart_items")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="cart_items_quantity_check"),
        UniqueConstraint("cart_id", "product_id", "product_variant_id", name="cart_items_unique"),
    )

    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"


class Wishlist(Base):
    """User wishlists."""

    __tablename__ = "wishlists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="wishlists")
    product = relationship("Product", back_populates="wishlists")

    __table_args__ = (UniqueConstraint("user_id", "product_id", name="wishlists_unique"),)

    def __repr__(self) -> str:
        return f"<Wishlist(id={self.id}, user_id={self.user_id}, product_id={self.product_id})>"
