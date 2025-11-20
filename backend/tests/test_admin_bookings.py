"""Tests for admin booking management API."""
from datetime import date, time, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi import status

from app.models.booking import Booking
from app.models.service import ServicePackage, TransportLocation
from app.models.user import User


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    user = User(
        email="admin@example.com",
        google_id="admin123",
        full_name="Admin User",
        is_admin=True,
        admin_role="super_admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session):
    """Create a regular (non-admin) user for testing."""
    user = User(
        email="user@example.com",
        google_id="user123",
        full_name="Regular User",
        is_admin=False,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    """Create JWT token for admin user."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email})


@pytest.fixture
def regular_token(regular_user):
    """Create JWT token for regular user."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(regular_user.id), "email": regular_user.email})


@pytest.fixture
def service_package(db_session):
    """Create a service package for testing."""
    package = ServicePackage(
        package_type="bridal_small",
        name="Small Bridal Package",
        description="Test package",
        base_bride_price=Decimal("15000.00"),
        base_maid_price=Decimal("3000.00"),
        base_mother_price=Decimal("4000.00"),
        base_other_price=Decimal("2000.00"),
        max_maids=6,
        min_maids=0,
        includes_facial=False,
        duration_minutes=180,
        is_active=True,
        display_order=1
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)
    return package


@pytest.fixture
def transport_location(db_session):
    """Create a transport location for testing."""
    location = TransportLocation(
        location_name="Nairobi CBD",
        county="Nairobi",
        transport_cost=Decimal("2000.00"),
        is_free=False,
        is_active=True
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def sample_bookings(db_session, regular_user, service_package, transport_location):
    """Create sample bookings for testing."""
    today = date.today()

    bookings = [
        Booking(
            booking_number="BK202501010001",
            user_id=regular_user.id,
            package_id=service_package.id,
            booking_date=today + timedelta(days=5),
            booking_time=time(10, 0),
            location_id=transport_location.id,
            num_brides=1,
            num_maids=2,
            num_mothers=1,
            num_others=0,
            subtotal=Decimal("22000.00"),
            transport_cost=Decimal("2000.00"),
            total_amount=Decimal("24000.00"),
            deposit_amount=Decimal("12000.00"),
            deposit_paid=False,
            status="pending"
        ),
        Booking(
            booking_number="BK202501010002",
            user_id=regular_user.id,
            package_id=service_package.id,
            booking_date=today + timedelta(days=10),
            booking_time=time(14, 0),
            location_id=transport_location.id,
            num_brides=1,
            num_maids=3,
            num_mothers=0,
            num_others=0,
            subtotal=Decimal("24000.00"),
            transport_cost=Decimal("2000.00"),
            total_amount=Decimal("26000.00"),
            deposit_amount=Decimal("13000.00"),
            deposit_paid=True,
            deposit_paid_at=datetime.utcnow(),
            status="deposit_paid"
        ),
        Booking(
            booking_number="BK202501010003",
            guest_email="guest@example.com",
            guest_name="Guest User",
            guest_phone="+254712345678",
            package_id=service_package.id,
            booking_date=today + timedelta(days=15),
            booking_time=time(11, 0),
            location_id=transport_location.id,
            num_brides=1,
            num_maids=1,
            num_mothers=0,
            num_others=0,
            subtotal=Decimal("18000.00"),
            transport_cost=Decimal("2000.00"),
            total_amount=Decimal("20000.00"),
            deposit_amount=Decimal("10000.00"),
            deposit_paid=False,
            status="confirmed"
        ),
    ]

    for booking in bookings:
        db_session.add(booking)
    db_session.commit()

    for booking in bookings:
        db_session.refresh(booking)

    return bookings


def test_list_all_bookings(client, admin_token, sample_bookings):
    """Test getting list of all bookings."""
    response = client.get(
        "/api/admin/bookings",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_list_bookings_with_status_filter(client, admin_token, sample_bookings):
    """Test filtering bookings by status."""
    response = client.get(
        "/api/admin/bookings?status=pending",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total"] == 1
    assert all(item["status"] == "pending" for item in data["items"])


def test_list_bookings_with_date_filter(client, admin_token, sample_bookings):
    """Test filtering bookings by date range."""
    start_date = date.today() + timedelta(days=8)
    end_date = date.today() + timedelta(days=12)

    response = client.get(
        f"/api/admin/bookings?startDate={start_date}&endDate={end_date}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["booking_number"] == "BK202501010002"


def test_list_bookings_with_location_filter(client, admin_token, sample_bookings, transport_location):
    """Test filtering bookings by location."""
    response = client.get(
        f"/api/admin/bookings?locationId={transport_location.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total"] == 3  # All sample bookings use the same location


def test_list_bookings_pagination(client, admin_token, sample_bookings):
    """Test booking list pagination."""
    response = client.get(
        "/api/admin/bookings?page=1&page_size=2",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 2


def test_list_bookings_invalid_date_range(client, admin_token):
    """Test that end_date before start_date is rejected."""
    start_date = date.today()
    end_date = start_date - timedelta(days=1)

    response = client.get(
        f"/api/admin/bookings?startDate={start_date}&endDate={end_date}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 422


def test_list_bookings_without_auth(client, sample_bookings):
    """Test that listing bookings requires authentication."""
    response = client.get("/api/admin/bookings")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_bookings_as_regular_user(client, regular_token, sample_bookings):
    """Test that listing bookings requires admin role."""
    response = client.get(
        "/api/admin/bookings",
        headers={"Authorization": f"Bearer {regular_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_booking_by_id(client, admin_token, sample_bookings):
    """Test getting a specific booking by ID."""
    booking = sample_bookings[0]

    response = client.get(
        f"/api/admin/bookings/{booking.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == str(booking.id)
    assert data["booking_number"] == booking.booking_number
    assert data["status"] == "pending"


def test_get_nonexistent_booking(client, admin_token):
    """Test getting a booking that doesn't exist."""
    from uuid import uuid4

    response = client.get(
        f"/api/admin/bookings/{uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_booking(client, admin_token, sample_bookings):
    """Test updating a booking."""
    booking = sample_bookings[0]

    update_data = {
        "num_maids": 3,
        "wedding_theme": "Vintage Garden",
        "admin_notes": "Updated maid count"
    }

    response = client.put(
        f"/api/admin/bookings/{booking.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["num_maids"] == 3
    assert data["wedding_theme"] == "Vintage Garden"
    assert "Updated maid count" in data["admin_notes"]
    # Pricing should be recalculated
    assert float(data["subtotal"]) == 28000.0  # 15000 + 3*3000 + 4000 = 28000


def test_update_booking_date_and_time(client, admin_token, sample_bookings):
    """Test updating booking date and time."""
    booking = sample_bookings[0]
    new_date = date.today() + timedelta(days=20)
    new_time = "15:00:00"

    update_data = {
        "booking_date": str(new_date),
        "booking_time": new_time
    }

    response = client.put(
        f"/api/admin/bookings/{booking.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["booking_date"] == str(new_date)
    assert data["booking_time"] == new_time


def test_update_booking_to_unavailable_slot(client, admin_token, sample_bookings):
    """Test that updating to an unavailable slot fails."""
    booking1, booking2 = sample_bookings[0], sample_bookings[1]

    # Try to change booking1 to booking2's slot
    update_data = {
        "booking_date": str(booking2.booking_date),
        "booking_time": str(booking2.booking_time)
    }

    response = client.put(
        f"/api/admin/bookings/{booking1.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not available" in response.json()["detail"].lower()


def test_mark_deposit_paid(client, admin_token, sample_bookings):
    """Test marking deposit as paid."""
    booking = sample_bookings[0]  # pending booking without deposit

    deposit_data = {
        "deposit_paid": True,
        "admin_notes": "M-Pesa payment received"
    }

    response = client.put(
        f"/api/admin/bookings/{booking.id}/deposit",
        json=deposit_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["deposit_paid"] is True
    assert data["deposit_paid_at"] is not None
    assert data["status"] == "deposit_paid"  # Auto-updated from pending
    assert "M-Pesa payment received" in data["admin_notes"]


def test_mark_deposit_unpaid(client, admin_token, sample_bookings):
    """Test marking deposit as unpaid."""
    booking = sample_bookings[1]  # deposit_paid booking

    deposit_data = {
        "deposit_paid": False,
        "admin_notes": "Payment reversed"
    }

    response = client.put(
        f"/api/admin/bookings/{booking.id}/deposit",
        json=deposit_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["deposit_paid"] is False
    assert data["deposit_paid_at"] is None


def test_update_booking_status(client, admin_token, sample_bookings):
    """Test updating booking status."""
    booking = sample_bookings[0]

    status_data = {
        "status": "confirmed",
        "admin_notes": "Confirmed via phone call"
    }

    response = client.put(
        f"/api/admin/bookings/{booking.id}/status",
        json=status_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "confirmed"
    assert "Status changed from 'pending' to 'confirmed'" in data["admin_notes"]
    assert "Confirmed via phone call" in data["admin_notes"]


def test_update_booking_status_invalid(client, admin_token, sample_bookings):
    """Test that invalid status is rejected."""
    booking = sample_bookings[0]

    status_data = {
        "status": "invalid_status"
    }

    response = client.put(
        f"/api/admin/bookings/{booking.id}/status",
        json=status_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 422  # Pydantic validation error


def test_cancel_booking(client, admin_token, sample_bookings):
    """Test cancelling a booking."""
    booking = sample_bookings[0]

    response = client.delete(
        f"/api/admin/bookings/{booking.id}?admin_notes=Customer request",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify booking is cancelled
    get_response = client.get(
        f"/api/admin/bookings/{booking.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert get_response.status_code == status.HTTP_200_OK
    data = get_response.json()
    assert data["status"] == "cancelled"
    assert "Admin cancelled: Customer request" in data["admin_notes"]


def test_cancel_already_cancelled_booking(client, admin_token, db_session, sample_bookings):
    """Test that cancelling an already cancelled booking fails."""
    booking = sample_bookings[0]
    booking.status = "cancelled"
    db_session.commit()

    response = client.delete(
        f"/api/admin/bookings/{booking.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already cancelled" in response.json()["detail"].lower()


def test_export_bookings_csv(client, admin_token, sample_bookings):
    """Test exporting bookings to CSV."""
    response = client.get(
        "/api/admin/bookings/export/csv",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]

    # Check CSV content
    csv_content = response.text
    lines = csv_content.strip().split("\n")

    # Header + 3 bookings
    assert len(lines) == 4
    assert "Booking Number" in lines[0]
    assert "BK202501010001" in csv_content
    assert "BK202501010002" in csv_content
    assert "BK202501010003" in csv_content


def test_export_bookings_csv_with_filters(client, admin_token, sample_bookings):
    """Test exporting filtered bookings to CSV."""
    response = client.get(
        "/api/admin/bookings/export/csv?status=pending",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    csv_content = response.text
    lines = csv_content.strip().split("\n")

    # Header + 1 pending booking
    assert len(lines) == 2
    assert "BK202501010001" in csv_content
    assert "BK202501010002" not in csv_content


def test_admin_notes_tracking(client, admin_token, sample_bookings):
    """Test that admin notes track changes with timestamps."""
    booking = sample_bookings[0]

    # Make multiple updates
    client.put(
        f"/api/admin/bookings/{booking.id}/status",
        json={"status": "confirmed", "admin_notes": "First update"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    client.put(
        f"/api/admin/bookings/{booking.id}/deposit",
        json={"deposit_paid": True, "admin_notes": "Second update"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Get booking and check notes
    response = client.get(
        f"/api/admin/bookings/{booking.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    data = response.json()
    notes = data["admin_notes"]

    # Should contain both updates with timestamps
    assert "First update" in notes
    assert "Second update" in notes
    assert "Status changed from" in notes
    assert "Deposit paid" in notes


def test_pricing_recalculation_on_update(client, admin_token, sample_bookings, transport_location, db_session):
    """Test that pricing is recalculated when participant counts change."""
    booking = sample_bookings[0]
    original_total = float(booking.total_amount)

    # Create a new location with different transport cost
    new_location = TransportLocation(
        location_name="Kitui Town",
        county="Kitui",
        transport_cost=Decimal("5000.00"),
        is_free=False,
        is_active=True
    )
    db_session.add(new_location)
    db_session.commit()
    db_session.refresh(new_location)

    # Update location and participant counts
    update_data = {
        "location_id": str(new_location.id),
        "num_maids": 4
    }

    response = client.put(
        f"/api/admin/bookings/{booking.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Verify pricing changed
    assert float(data["total_amount"]) != original_total
    # New total: 15000 (bride) + 12000 (4 maids) + 4000 (1 mother) + 5000 (transport) = 36000
    assert float(data["total_amount"]) == 36000.0
    assert float(data["transport_cost"]) == 5000.0
    assert float(data["deposit_amount"]) == 18000.0  # 50% of 36000
