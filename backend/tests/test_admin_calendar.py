"""Tests for admin calendar availability API."""
from datetime import date, time, timedelta

import pytest
from fastapi import status

from app.models.service import CalendarAvailability
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
def sample_blocked_slots(db_session):
    """Create sample blocked calendar slots."""
    today = date.today()

    slots = [
        CalendarAvailability(
            date=today,
            time_slot=time(9, 0),
            is_available=False,
            reason="Fully booked"
        ),
        CalendarAvailability(
            date=today,
            time_slot=time(14, 0),
            is_available=False,
            reason="Personal appointment"
        ),
        CalendarAvailability(
            date=today + timedelta(days=1),
            time_slot=time(10, 0),
            is_available=False,
            reason="Holiday"
        ),
    ]

    for slot in slots:
        db_session.add(slot)
    db_session.commit()

    for slot in slots:
        db_session.refresh(slot)

    return slots


def test_get_calendar_availability(client, admin_token, sample_blocked_slots):
    """Test getting calendar availability for a date range."""
    today = date.today()
    end_date = today + timedelta(days=7)

    response = client.get(
        f"/api/admin/calendar?startDate={today}&endDate={end_date}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_get_calendar_availability_empty_range(client, admin_token):
    """Test getting availability for a date range with no blocked slots."""
    start_date = date.today() + timedelta(days=30)
    end_date = start_date + timedelta(days=7)

    response = client.get(
        f"/api/admin/calendar?startDate={start_date}&endDate={end_date}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_get_calendar_invalid_date_range(client, admin_token):
    """Test that end_date before start_date is rejected."""
    start_date = date.today()
    end_date = start_date - timedelta(days=1)

    response = client.get(
        f"/api/admin/calendar?startDate={start_date}&endDate={end_date}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_calendar_without_auth(client, sample_blocked_slots):
    """Test that getting calendar requires authentication."""
    today = date.today()
    end_date = today + timedelta(days=7)

    response = client.get(f"/api/admin/calendar?startDate={today}&endDate={end_date}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_calendar_as_regular_user(client, regular_token, sample_blocked_slots):
    """Test that getting calendar requires admin role."""
    today = date.today()
    end_date = today + timedelta(days=7)

    response = client.get(
        f"/api/admin/calendar?startDate={today}&endDate={end_date}",
        headers={"Authorization": f"Bearer {regular_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_block_time_slot(client, admin_token):
    """Test blocking a time slot."""
    slot_data = {
        "date": str(date.today()),
        "timeSlot": "15:00:00",
        "reason": "Maintenance"
    }

    response = client.post(
        "/api/admin/calendar/block",
        json=slot_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["date"] == slot_data["date"]
    assert data["timeSlot"] == slot_data["timeSlot"]
    assert data["isAvailable"] is False
    assert data["reason"] == "Maintenance"
    assert "id" in data


def test_block_already_blocked_slot(client, admin_token, sample_blocked_slots):
    """Test that blocking an already blocked slot fails."""
    slot = sample_blocked_slots[0]

    slot_data = {
        "date": str(slot.date),
        "timeSlot": str(slot.time_slot),
        "reason": "Trying to block again"
    }

    response = client.post(
        "/api/admin/calendar/block",
        json=slot_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already blocked" in response.json()["detail"].lower()


def test_block_slot_without_reason(client, admin_token):
    """Test blocking a slot without providing a reason."""
    slot_data = {
        "date": str(date.today() + timedelta(days=5)),
        "timeSlot": "16:00:00"
    }

    response = client.post(
        "/api/admin/calendar/block",
        json=slot_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["reason"] is None


def test_unblock_time_slot(client, admin_token, sample_blocked_slots):
    """Test unblocking a time slot."""
    slot = sample_blocked_slots[0]

    response = client.delete(
        f"/api/admin/calendar/block/{slot.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify slot is deleted
    get_response = client.get(
        f"/api/admin/calendar/{slot.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_unblock_nonexistent_slot(client, admin_token):
    """Test unblocking a slot that doesn't exist."""
    from uuid import uuid4

    response = client.delete(
        f"/api/admin/calendar/block/{uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_slot_by_id(client, admin_token, sample_blocked_slots):
    """Test getting a specific slot by ID."""
    slot = sample_blocked_slots[0]

    response = client.get(
        f"/api/admin/calendar/{slot.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == str(slot.id)
    assert data["date"] == str(slot.date)
    assert data["isAvailable"] is False


def test_calendar_slots_ordered_correctly(client, admin_token, db_session):
    """Test that calendar slots are returned in correct order (date, time)."""
    today = date.today()

    # Create slots in random order
    slots_data = [
        (today + timedelta(days=2), time(10, 0)),
        (today, time(14, 0)),
        (today, time(9, 0)),
        (today + timedelta(days=1), time(11, 0)),
    ]

    for date_val, time_val in slots_data:
        slot = CalendarAvailability(
            date=date_val,
            time_slot=time_val,
            is_available=False,
            reason="Test"
        )
        db_session.add(slot)
    db_session.commit()

    end_date = today + timedelta(days=7)

    response = client.get(
        f"/api/admin/calendar?startDate={today}&endDate={end_date}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    items = data["items"]
    assert len(items) == 4

    # Verify order: date ascending, then time ascending
    assert items[0]["date"] == str(today)
    assert items[0]["timeSlot"] == "09:00:00"

    assert items[1]["date"] == str(today)
    assert items[1]["timeSlot"] == "14:00:00"

    assert items[2]["date"] == str(today + timedelta(days=1))
    assert items[3]["date"] == str(today + timedelta(days=2))


def test_block_invalid_date_format(client, admin_token):
    """Test that invalid date format is rejected."""
    slot_data = {
        "date": "invalid-date",
        "timeSlot": "15:00:00",
        "reason": "Test"
    }

    response = client.post(
        "/api/admin/calendar/block",
        json=slot_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_block_invalid_time_format(client, admin_token):
    """Test that invalid time format is rejected."""
    slot_data = {
        "date": str(date.today()),
        "timeSlot": "invalid-time",
        "reason": "Test"
    }

    response = client.post(
        "/api/admin/calendar/block",
        json=slot_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_calendar_response_schema(client, admin_token, sample_blocked_slots):
    """Test that calendar response has all required fields."""
    today = date.today()
    end_date = today + timedelta(days=7)

    response = client.get(
        f"/api/admin/calendar?startDate={today}&endDate={end_date}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data["items"]) > 0
    slot = data["items"][0]

    # Check all required fields
    assert "id" in slot
    assert "date" in slot
    assert "timeSlot" in slot
    assert "isAvailable" in slot
    assert "reason" in slot
    assert "createdAt" in slot

    # Verify data types
    assert isinstance(slot["date"], str)
    assert isinstance(slot["timeSlot"], str)
    assert isinstance(slot["isAvailable"], bool)
    assert slot["isAvailable"] is False  # All our test slots are blocked


def test_unique_constraint_prevents_duplicates(client, admin_token, db_session):
    """Test that database unique constraint prevents duplicate date/time slots."""
    from app.models.service import CalendarAvailability

    today = date.today()
    time_slot = time(10, 0)

    # Create first slot
    slot1 = CalendarAvailability(
        date=today,
        time_slot=time_slot,
        is_available=False,
        reason="First slot"
    )
    db_session.add(slot1)
    db_session.commit()

    # Try to create duplicate via API (should update existing)
    slot_data = {
        "date": str(today),
        "timeSlot": str(time_slot),
        "reason": "Trying to create duplicate"
    }

    response = client.post(
        "/api/admin/calendar/block",
        json=slot_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Should fail because slot is already blocked
    assert response.status_code == status.HTTP_409_CONFLICT
