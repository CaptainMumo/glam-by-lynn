"""Product-related models including brands, categories, products, variants, images, and videos."""
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
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Brand(Base):
    """Product brands (e.g., Fenty Beauty, The Ordinary)."""

    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    logo_url = Column(String(500))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    products = relationship("Product", back_populates="brand", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Brand(id={self.id}, name={self.name})>"


class Category(Base):
    """Product categories with hierarchical structure."""

    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    parent_category_id = Column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    description = Column(Text)
    image_url = Column(String(500))
    display_order = Column(Integer, default=0, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Self-referencing relationship
    parent_category = relationship("Category", remote_side=[id], backref="subcategories")

    # Relationships
    products = relationship("Product", back_populates="category", lazy="dynamic")

    __table_args__ = (
        CheckConstraint("id != parent_category_id", name="categories_no_self_reference"),
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"


class Product(Base):
    """Core product table with pricing and inventory."""

    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    description = Column(Text)
    brand_id = Column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="SET NULL"), index=True
    )
    category_id = Column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), index=True
    )
    base_price = Column(Numeric(10, 2), nullable=False, index=True)
    discount_type = Column(
        String(20), CheckConstraint("discount_type IN ('percentage', 'fixed')")
    )
    discount_value = Column(Numeric(10, 2))
    sku = Column(String(100), unique=True)
    inventory_count = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    tags = Column(ARRAY(Text))
    meta_title = Column(String(255))
    meta_description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    images = relationship(
        "ProductImage", back_populates="product", lazy="dynamic", cascade="all, delete-orphan"
    )
    videos = relationship(
        "ProductVideo", back_populates="product", lazy="dynamic", cascade="all, delete-orphan"
    )
    variants = relationship(
        "ProductVariant", back_populates="product", lazy="dynamic", cascade="all, delete-orphan"
    )
    reviews = relationship("Review", back_populates="product", lazy="dynamic")
    order_items = relationship("OrderItem", back_populates="product", lazy="dynamic")
    cart_items = relationship("CartItem", back_populates="product", lazy="dynamic")
    wishlists = relationship("Wishlist", back_populates="product", lazy="dynamic")
    testimonials = relationship("Testimonial", back_populates="related_product", lazy="dynamic")

    __table_args__ = (
        CheckConstraint("base_price >= 0", name="products_base_price_check"),
        CheckConstraint("discount_value >= 0", name="products_discount_value_check"),
        CheckConstraint("inventory_count >= 0", name="products_inventory_count_check"),
        CheckConstraint(
            "low_stock_threshold >= 0", name="products_low_stock_threshold_check"
        ),
        CheckConstraint(
            """
            (discount_type IS NULL AND discount_value IS NULL) OR
            (discount_type IS NOT NULL AND discount_value IS NOT NULL AND discount_value > 0) OR
            (discount_type = 'percentage' AND discount_value <= 100)
            """,
            name="products_discount_check",
        ),
        Index("idx_products_inventory", "inventory_count"),
        Index("idx_products_tags", "tags", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, title={self.title})>"


class ProductImage(Base):
    """Product images with ordering."""

    __tablename__ = "product_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255))
    is_primary = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="images")

    __table_args__ = (
        Index("idx_product_images_is_primary", "product_id", "is_primary"),
        Index("idx_product_images_display_order", "product_id", "display_order"),
        Index(
            "idx_product_images_one_primary",
            "product_id",
            unique=True,
            postgresql_where="is_primary = TRUE",
        ),
    )

    def __repr__(self) -> str:
        return f"<ProductImage(id={self.id}, product_id={self.product_id})>"


class ProductVideo(Base):
    """Product videos."""

    __tablename__ = "product_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="videos")

    __table_args__ = (Index("idx_product_videos_display_order", "product_id", "display_order"),)

    def __repr__(self) -> str:
        return f"<ProductVideo(id={self.id}, product_id={self.product_id})>"


class ProductVariant(Base):
    """Product variants (size, color, etc.)."""

    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    variant_type = Column(String(50), nullable=False, index=True)
    variant_value = Column(String(100), nullable=False)
    price_adjustment = Column(Numeric(10, 2), default=0)
    inventory_count = Column(Integer, default=0)
    sku = Column(String(100), unique=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    product = relationship("Product", back_populates="variants")
    order_items = relationship("OrderItem", back_populates="product_variant", lazy="dynamic")
    cart_items = relationship("CartItem", back_populates="product_variant", lazy="dynamic")

    __table_args__ = (
        CheckConstraint("inventory_count >= 0", name="product_variants_inventory_check"),
        UniqueConstraint(
            "product_id", "variant_type", "variant_value", name="product_variants_unique"
        ),
    )

    def __repr__(self) -> str:
        return f"<ProductVariant(id={self.id}, type={self.variant_type}, value={self.variant_value})>"
