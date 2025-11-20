"""Tests for admin transport locations API."""
from decimal import Decimal

import pytest
from fastapi import status

from app.models.service import TransportLocation
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
def sample_locations(db_session):
    """Create sample transport locations."""
    locations = [
        TransportLocation(
            location_name="Nairobi CBD",
            county="Nairobi",
            transport_cost=Decimal("0.00"),
            is_free=True,
            is_active=True,
        ),
        TransportLocation(
            location_name="Kitui Town",
            county="Kitui",
            transport_cost=Decimal("2000.00"),
            is_free=False,
            is_active=True,
        ),
        TransportLocation(
            location_name="Mombasa",
            county="Mombasa",
            transport_cost=Decimal("5000.00"),
            is_free=False,
            is_active=False,  # Inactive
        ),
    ]

    for location in locations:
        db_session.add(location)
    db_session.commit()

    for location in locations:
        db_session.refresh(location)

    return locations


def test_list_locations_as_admin(client, admin_token, sample_locations):
    """Test listing locations as admin user."""
    response = client.get(
        "/api/admin/locations",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should return only active locations by default
    assert len(data) == 2
    assert data[0]["locationName"] == "Kitui Town"
    assert data[1]["locationName"] == "Nairobi CBD"


def test_list_locations_include_inactive(client, admin_token, sample_locations):
    """Test listing locations including inactive ones."""
    response = client.get(
        "/api/admin/locations?include_inactive=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should return all locations including inactive
    assert len(data) == 3


def test_list_locations_without_auth(client, sample_locations):
    """Test that listing locations requires authentication."""
    response = client.get("/api/admin/locations")

    # FastAPI HTTPBearer returns 403 when no credentials provided
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_locations_as_regular_user(client, regular_token, sample_locations):
    """Test that listing locations requires admin role."""
    response = client.get(
        "/api/admin/locations",
        headers={"Authorization": f"Bearer {regular_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_location_by_id(client, admin_token, sample_locations):
    """Test getting a specific location by ID."""
    location = sample_locations[0]

    response = client.get(
        f"/api/admin/locations/{location.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == str(location.id)
    assert data["locationName"] == location.location_name
    assert data["county"] == location.county
    assert data["isFree"] == location.is_free


def test_get_nonexistent_location(client, admin_token):
    """Test getting a location that doesn't exist."""
    from uuid import uuid4

    response = client.get(
        f"/api/admin/locations/{uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_location(client, admin_token):
    """Test creating a new location."""
    location_data = {
        "locationName": "Nakuru",
        "county": "Nakuru",
        "transportCost": "3000.00",
        "isFree": False,
        "isActive": True,
    }

    response = client.post(
        "/api/admin/locations",
        json=location_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["locationName"] == "Nakuru"
    assert data["county"] == "Nakuru"
    assert data["transportCost"] == "3000.00"
    assert data["isFree"] is False
    assert data["isActive"] is True
    assert "id" in data


def test_create_location_with_free_transport(client, admin_token):
    """Test creating a location marked as free transport."""
    location_data = {
        "locationName": "Westlands",
        "county": "Nairobi",
        "transportCost": "0.00",
        "isFree": True,
        "isActive": True,
    }

    response = client.post(
        "/api/admin/locations",
        json=location_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["isFree"] is True
    assert data["transportCost"] == "0.00"


def test_create_duplicate_location(client, admin_token, sample_locations):
    """Test that creating a duplicate location name fails."""
    location_data = {
        "locationName": "Nairobi CBD",  # Already exists
        "county": "Nairobi",
        "transportCost": "0.00",
        "isFree": True,
        "isActive": True,
    }

    response = client.post(
        "/api/admin/locations",
        json=location_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["detail"].lower()


def test_create_location_invalid_data(client, admin_token):
    """Test that invalid data is rejected."""
    location_data = {
        "locationName": "",  # Empty name
        "transportCost": "-100.00",  # Negative cost
    }

    response = client.post(
        "/api/admin/locations",
        json=location_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_location(client, admin_token, sample_locations):
    """Test updating a location."""
    location = sample_locations[1]  # Kitui Town

    update_data = {
        "locationName": "Kitui Updated",
        "transportCost": "2500.00",
    }

    response = client.put(
        f"/api/admin/locations/{location.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["locationName"] == "Kitui Updated"
    assert data["transportCost"] == "2500.00"
    # Other fields should remain unchanged
    assert data["county"] == "Kitui"


def test_update_location_mark_inactive(client, admin_token, sample_locations):
    """Test marking a location as inactive."""
    location = sample_locations[0]

    update_data = {
        "isActive": False,
    }

    response = client.put(
        f"/api/admin/locations/{location.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["isActive"] is False


def test_update_location_to_duplicate_name(client, admin_token, sample_locations):
    """Test that updating to a duplicate name fails."""
    location = sample_locations[1]  # Kitui Town

    update_data = {
        "locationName": "Nairobi CBD",  # Already exists
    }

    response = client.put(
        f"/api/admin/locations/{location.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_nonexistent_location(client, admin_token):
    """Test updating a location that doesn't exist."""
    from uuid import uuid4

    update_data = {
        "locationName": "Updated Name",
    }

    response = client.put(
        f"/api/admin/locations/{uuid4()}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_location(client, admin_token, sample_locations):
    """Test deleting a location."""
    location = sample_locations[2]  # Inactive location

    response = client.delete(
        f"/api/admin/locations/{location.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify location is deleted
    get_response = client.get(
        f"/api/admin/locations/{location.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_location(client, admin_token):
    """Test deleting a location that doesn't exist."""
    from uuid import uuid4

    response = client.delete(
        f"/api/admin/locations/{uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_location_response_schema(client, admin_token, sample_locations):
    """Test that location response has all required fields."""
    response = client.get(
        "/api/admin/locations",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) > 0
    location = data[0]

    # Check all required fields exist
    assert "id" in location
    assert "locationName" in location
    assert "county" in location
    assert "transportCost" in location
    assert "isFree" in location
    assert "isActive" in location
    assert "createdAt" in location
    assert "updatedAt" in location

    # Verify data types
    assert isinstance(location["locationName"], str)
    assert isinstance(location["transportCost"], str)  # Decimal as string
    assert isinstance(location["isFree"], bool)
    assert isinstance(location["isActive"], bool)
