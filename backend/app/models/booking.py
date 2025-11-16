"""Booking model for makeup service reservations."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Booking(Base):
    """Makeup service bookings."""

    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    booking_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    guest_email = Column(String(255), index=True)
    guest_name = Column(String(255))
    guest_phone = Column(String(20))
    package_id = Column(
        UUID(as_uuid=True),
        ForeignKey("service_packages.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    booking_date = Column(Date, nullable=False, index=True)
    booking_time = Column(Time, nullable=False)
    location_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transport_locations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    num_brides = Column(Integer, default=1)
    num_maids = Column(Integer, default=0)
    num_mothers = Column(Integer, default=0)
    num_others = Column(Integer, default=0)
    wedding_theme = Column(String(255))
    special_requests = Column(Text)
    subtotal = Column(Numeric(10, 2), nullable=False)
    transport_cost = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2))
    deposit_paid = Column(Boolean, default=False)
    deposit_paid_at = Column(DateTime(timezone=True))
    status = Column(String(30), nullable=False, default="pending", index=True)
    admin_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="bookings")
    package = relationship("ServicePackage", back_populates="bookings")
    location = relationship("TransportLocation", back_populates="bookings")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'deposit_paid', 'completed', 'cancelled')",
            name="bookings_status_check",
        ),
        CheckConstraint("num_brides >= 0", name="bookings_num_brides_check"),
        CheckConstraint("num_maids >= 0", name="bookings_num_maids_check"),
        CheckConstraint("num_mothers >= 0", name="bookings_num_mothers_check"),
        CheckConstraint("num_others >= 0", name="bookings_num_others_check"),
        CheckConstraint("subtotal >= 0", name="bookings_subtotal_check"),
        CheckConstraint("transport_cost >= 0", name="bookings_transport_cost_check"),
        CheckConstraint("total_amount >= 0", name="bookings_total_amount_check"),
        CheckConstraint("deposit_amount >= 0", name="bookings_deposit_amount_check"),
        CheckConstraint(
            """
            user_id IS NOT NULL OR
            (guest_email IS NOT NULL AND guest_name IS NOT NULL AND guest_phone IS NOT NULL)
            """,
            name="bookings_user_or_guest_check",
        ),
        CheckConstraint(
            "deposit_amount IS NULL OR deposit_amount = ROUND(total_amount * 0.5, 2)",
            name="bookings_deposit_amount_check_50_percent",
        ),
        Index("idx_bookings_date_time", "booking_date", "booking_time"),
    )

    def __repr__(self) -> str:
        return f"<Booking(id={self.id}, booking_number={self.booking_number}, status={self.status})>"
