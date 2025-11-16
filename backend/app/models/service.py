"""Service-related models for makeup services and bookings."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ServicePackage(Base):
    """Makeup service packages with dynamic pricing."""

    __tablename__ = "service_packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    package_type = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    base_bride_price = Column(Numeric(10, 2))
    base_maid_price = Column(Numeric(10, 2))
    base_mother_price = Column(Numeric(10, 2))
    base_other_price = Column(Numeric(10, 2))
    max_maids = Column(Integer)
    min_maids = Column(Integer, default=0)
    includes_facial = Column(Boolean, default=False)
    duration_minutes = Column(Integer)
    is_active = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    bookings = relationship("Booking", back_populates="package", lazy="dynamic")
    testimonials = relationship("Testimonial", back_populates="related_service", lazy="dynamic")

    __table_args__ = (
        CheckConstraint(
            "package_type IN ('bridal_large', 'bridal_small', 'bride_only', 'regular', 'classes')",
            name="service_packages_type_check",
        ),
        CheckConstraint("base_bride_price >= 0", name="service_packages_bride_price_check"),
        CheckConstraint("base_maid_price >= 0", name="service_packages_maid_price_check"),
        CheckConstraint("base_mother_price >= 0", name="service_packages_mother_price_check"),
        CheckConstraint("base_other_price >= 0", name="service_packages_other_price_check"),
        CheckConstraint("max_maids > 0", name="service_packages_max_maids_check"),
        CheckConstraint("min_maids >= 0", name="service_packages_min_maids_check"),
        CheckConstraint("duration_minutes > 0", name="service_packages_duration_check"),
        CheckConstraint(
            "max_maids IS NULL OR min_maids IS NULL OR max_maids >= min_maids",
            name="service_packages_maid_range_check",
        ),
    )

    def __repr__(self) -> str:
        return f"<ServicePackage(id={self.id}, name={self.name}, type={self.package_type})>"


class TransportLocation(Base):
    """Locations with transport pricing."""

    __tablename__ = "transport_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    location_name = Column(String(255), unique=True, nullable=False)
    county = Column(String(100))
    transport_cost = Column(Numeric(10, 2), default=0)
    is_free = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    bookings = relationship("Booking", back_populates="location", lazy="dynamic")

    __table_args__ = (
        CheckConstraint("transport_cost >= 0", name="transport_locations_cost_check"),
    )

    def __repr__(self) -> str:
        return f"<TransportLocation(id={self.id}, name={self.location_name})>"


class CalendarAvailability(Base):
    """Calendar availability for bookings."""

    __tablename__ = "calendar_availability"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date = Column(Date, nullable=False, index=True)
    time_slot = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    reason = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("date", "time_slot", name="calendar_availability_unique_datetime"),
        Index("idx_calendar_availability_date_time", "date", "time_slot"),
        Index(
            "idx_calendar_availability_is_available",
            "is_available",
            postgresql_where="is_available = FALSE",
        ),
    )

    def __repr__(self) -> str:
        return f"<CalendarAvailability(id={self.id}, date={self.date}, time={self.time_slot})>"
