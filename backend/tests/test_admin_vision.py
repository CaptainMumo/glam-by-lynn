"""Tests for admin vision registration analytics API."""
from datetime import datetime, timezone

import pytest
from fastapi import status

from app.models.content import VisionRegistration
from app.models.user import User


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    user = User(
        email="admin@glambylynn.com",
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
    """Create a regular non-admin user for testing."""
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
def sample_registrations(db_session):
    """Create sample vision registrations."""
    registrations = [
        VisionRegistration(
            full_name="Jane Doe",
            email="jane@example.com",
            phone_number="+254712345678",
            location="Nairobi",
            interested_in_salon=True,
            interested_in_spa=True,
            interested_in_barbershop=False,
            interested_in_mobile_van=False,
            created_at=datetime(2025, 1, 15, tzinfo=timezone.utc),
        ),
        VisionRegistration(
            full_name="John Smith",
            email="john@example.com",
            phone_number="+254722334455",
            location="Kitui",
            interested_in_salon=False,
            interested_in_spa=False,
            interested_in_barbershop=True,
            interested_in_mobile_van=True,
            created_at=datetime(2025, 1, 20, tzinfo=timezone.utc),
        ),
        VisionRegistration(
            full_name="Mary Johnson",
            email="mary@example.com",
            phone_number="+254733445566",
            location="Nairobi",
            interested_in_salon=True,
            interested_in_spa=False,
            interested_in_barbershop=False,
            interested_in_mobile_van=True,
            created_at=datetime(2025, 2, 10, tzinfo=timezone.utc),
        ),
        VisionRegistration(
            full_name="Peter Brown",
            email="peter@example.com",
            phone_number="+254744556677",
            location="Mombasa",
            interested_in_salon=True,
            interested_in_spa=True,
            interested_in_barbershop=True,
            interested_in_mobile_van=True,
            additional_comments="Very interested!",
            created_at=datetime(2025, 2, 15, tzinfo=timezone.utc),
        ),
    ]

    for registration in registrations:
        db_session.add(registration)
    db_session.commit()

    return registrations


def test_get_vision_registrations_unauthorized(client):
    """Test that unauthenticated requests are rejected."""
    response = client.get("/api/admin/vision/registrations")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_vision_registrations_non_admin(client, regular_token):
    """Test that non-admin users cannot access vision registrations."""
    response = client.get(
        "/api/admin/vision/registrations",
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_vision_registrations_success(client, admin_token, sample_registrations):
    """Test getting all vision registrations as admin."""
    response = client.get(
        "/api/admin/vision/registrations",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "registrations" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data

    assert data["total"] == 4
    assert len(data["registrations"]) == 4


def test_get_vision_registrations_pagination(client, admin_token, sample_registrations):
    """Test pagination parameters."""
    response = client.get(
        "/api/admin/vision/registrations?skip=1&limit=2",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total"] == 4
    assert data["skip"] == 1
    assert data["limit"] == 2
    assert len(data["registrations"]) == 2


def test_get_vision_registrations_filter_by_service(client, admin_token, sample_registrations):
    """Test filtering by service interest."""
    # Filter by salon interest
    response = client.get(
        "/api/admin/vision/registrations?service=salon",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should get 3 registrations interested in salon
    assert data["total"] == 3
    for reg in data["registrations"]:
        assert reg["interestedInSalon"] is True


def test_get_vision_registrations_filter_by_location(client, admin_token, sample_registrations):
    """Test filtering by location."""
    response = client.get(
        "/api/admin/vision/registrations?location=Nairobi",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should get 2 registrations from Nairobi
    assert data["total"] == 2
    for reg in data["registrations"]:
        assert "Nairobi" in reg["location"]


def test_get_vision_analytics_unauthorized(client):
    """Test that unauthenticated requests are rejected."""
    response = client.get("/api/admin/vision/analytics")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_vision_analytics_non_admin(client, regular_token):
    """Test that non-admin users cannot access analytics."""
    response = client.get(
        "/api/admin/vision/analytics",
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_vision_analytics_success(client, admin_token, sample_registrations):
    """Test getting vision analytics as admin."""
    response = client.get(
        "/api/admin/vision/analytics",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "totalRegistrations" in data
    assert "serviceInterests" in data
    assert "locationDistribution" in data
    assert "registrationsByMonth" in data

    # Verify total
    assert data["totalRegistrations"] == 4

    # Verify service interests
    service_interests = data["serviceInterests"]
    assert len(service_interests) == 4

    # Find salon interest
    salon_interest = next(s for s in service_interests if s["serviceName"] == "Full-service Salon")
    assert salon_interest["count"] == 3
    assert salon_interest["percentage"] == 75.0

    # Verify location distribution
    location_dist = data["locationDistribution"]
    assert len(location_dist) == 3  # Nairobi, Kitui, Mombasa

    # Verify monthly registrations
    monthly = data["registrationsByMonth"]
    assert "2025-01" in monthly
    assert "2025-02" in monthly
    assert monthly["2025-01"] == 2  # 2 registrations in January
    assert monthly["2025-02"] == 2  # 2 registrations in February


def test_get_vision_analytics_empty(client, admin_token):
    """Test analytics with no registrations."""
    response = client.get(
        "/api/admin/vision/analytics",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["totalRegistrations"] == 0
    assert data["serviceInterests"] == []
    assert data["locationDistribution"] == []
    assert data["registrationsByMonth"] == {}


def test_export_vision_registrations_unauthorized(client):
    """Test that unauthenticated requests are rejected."""
    response = client.get("/api/admin/vision/export")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_export_vision_registrations_non_admin(client, regular_token):
    """Test that non-admin users cannot export registrations."""
    response = client.get(
        "/api/admin/vision/export",
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_export_vision_registrations_success(client, admin_token, sample_registrations):
    """Test exporting vision registrations to CSV."""
    response = client.get(
        "/api/admin/vision/export",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]
    assert "vision_registrations.csv" in response.headers["content-disposition"]

    # Verify CSV content
    csv_content = response.text
    lines = csv_content.strip().split("\n")

    # Should have header + 4 data rows
    assert len(lines) == 5

    # Verify header
    header = lines[0]
    assert "Full Name" in header
    assert "Email" in header
    assert "Phone Number" in header
    assert "Location" in header
    assert "Interested in Salon" in header

    # Verify data rows contain expected info
    assert "Jane Doe" in csv_content
    assert "john@example.com" in csv_content
    assert "Nairobi" in csv_content
    assert "Mombasa" in csv_content


def test_export_vision_registrations_empty(client, admin_token):
    """Test exporting when there are no registrations."""
    response = client.get(
        "/api/admin/vision/export",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

    # Should only have header row
    csv_content = response.text
    lines = csv_content.strip().split("\n")
    assert len(lines) == 1  # Only header
