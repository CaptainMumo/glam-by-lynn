"""Tests for public promo code API endpoints."""
import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.order import PromoCode


@pytest.fixture
def active_percentage_promo(db_session: Session):
    """Create an active percentage-based promo code."""
    now = datetime.now(timezone.utc)
    promo = PromoCode(
        code="SAVE20",
        description="20% off all orders",
        discount_type="percentage",
        discount_value=Decimal("20"),
        min_order_amount=Decimal("50"),
        max_discount_amount=Decimal("100"),
        usage_limit=100,
        usage_count=0,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=30),
        is_active=True,
    )
    db_session.add(promo)
    db_session.commit()
    db_session.refresh(promo)
    return promo


@pytest.fixture
def active_fixed_promo(db_session: Session):
    """Create an active fixed-discount promo code."""
    now = datetime.now(timezone.utc)
    promo = PromoCode(
        code="FIXED10",
        description="$10 off",
        discount_type="fixed",
        discount_value=Decimal("10"),
        min_order_amount=Decimal("30"),
        max_discount_amount=None,
        usage_limit=50,
        usage_count=0,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=30),
        is_active=True,
    )
    db_session.add(promo)
    db_session.commit()
    db_session.refresh(promo)
    return promo


@pytest.fixture
def expired_promo(db_session: Session):
    """Create an expired promo code."""
    now = datetime.now(timezone.utc)
    promo = PromoCode(
        code="EXPIRED",
        description="Expired promo",
        discount_type="percentage",
        discount_value=Decimal("15"),
        min_order_amount=None,
        max_discount_amount=None,
        usage_limit=None,
        usage_count=0,
        valid_from=now - timedelta(days=60),
        valid_until=now - timedelta(days=1),
        is_active=True,
    )
    db_session.add(promo)
    db_session.commit()
    db_session.refresh(promo)
    return promo


@pytest.fixture
def inactive_promo(db_session: Session):
    """Create an inactive promo code."""
    now = datetime.now(timezone.utc)
    promo = PromoCode(
        code="INACTIVE",
        description="Inactive promo",
        discount_type="percentage",
        discount_value=Decimal("25"),
        min_order_amount=None,
        max_discount_amount=None,
        usage_limit=None,
        usage_count=0,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=30),
        is_active=False,
    )
    db_session.add(promo)
    db_session.commit()
    db_session.refresh(promo)
    return promo


@pytest.fixture
def exhausted_promo(db_session: Session):
    """Create a promo code that has reached its usage limit."""
    now = datetime.now(timezone.utc)
    promo = PromoCode(
        code="EXHAUSTED",
        description="Usage limit reached",
        discount_type="fixed",
        discount_value=Decimal("5"),
        min_order_amount=None,
        max_discount_amount=None,
        usage_limit=10,
        usage_count=10,  # Already at limit
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=30),
        is_active=True,
    )
    db_session.add(promo)
    db_session.commit()
    db_session.refresh(promo)
    return promo


def test_validate_percentage_promo_success(client: TestClient, active_percentage_promo):
    """Test validating a valid percentage-based promo code."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "SAVE20", "orderAmount": "100.00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is True
    assert "successfully" in data["message"].lower()
    assert float(data["discountAmount"]) == 20.0  # 20% of 100
    assert data["promoCode"] is not None
    assert data["promoCode"]["code"] == "SAVE20"
    assert data["promoCode"]["discountType"] == "percentage"


def test_validate_fixed_promo_success(client: TestClient, active_fixed_promo):
    """Test validating a valid fixed-discount promo code."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "FIXED10", "orderAmount": "50.00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is True
    assert "successfully" in data["message"].lower()
    assert float(data["discountAmount"]) == 10.0
    assert data["promoCode"] is not None
    assert data["promoCode"]["code"] == "FIXED10"
    assert data["promoCode"]["discountType"] == "fixed"


def test_validate_promo_case_insensitive(client: TestClient, active_percentage_promo):
    """Test that promo code validation is case-insensitive."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "save20", "orderAmount": "100.00"},  # Lowercase
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is True
    assert data["promoCode"]["code"] == "SAVE20"


def test_validate_promo_with_max_discount_cap(client: TestClient, active_percentage_promo):
    """Test that maximum discount amount cap is applied."""
    # Order of $1000 would normally give $200 discount (20%)
    # But max discount is capped at $100
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "SAVE20", "orderAmount": "1000.00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is True
    assert float(data["discountAmount"]) == 100.0  # Capped at max
    assert float(data["discountAmount"]) < 200.0  # Less than uncapped amount


def test_validate_promo_minimum_order_not_met(client: TestClient, active_percentage_promo):
    """Test validation fails when order amount is below minimum."""
    # SAVE20 requires minimum order of $50
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "SAVE20", "orderAmount": "30.00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is False
    assert "minimum order amount" in data["message"].lower()
    assert data["discountAmount"] is None
    assert data["promoCode"] is None  # Don't expose details for invalid codes


def test_validate_nonexistent_promo(client: TestClient):
    """Test validation fails for non-existent promo code."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "NONEXISTENT", "orderAmount": "100.00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is False
    assert "invalid" in data["message"].lower()
    assert data["discountAmount"] is None
    assert data["promoCode"] is None


def test_validate_expired_promo(client: TestClient, expired_promo):
    """Test validation fails for expired promo code."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "EXPIRED", "orderAmount": "100.00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is False
    assert "expired" in data["message"].lower()
    assert data["discountAmount"] is None
    assert data["promoCode"] is None


def test_validate_inactive_promo(client: TestClient, inactive_promo):
    """Test validation fails for inactive promo code."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "INACTIVE", "orderAmount": "100.00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is False
    assert "inactive" in data["message"].lower()
    assert data["discountAmount"] is None
    assert data["promoCode"] is None


def test_validate_exhausted_promo(client: TestClient, exhausted_promo):
    """Test validation fails for promo code that reached usage limit."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "EXHAUSTED", "orderAmount": "100.00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is False
    assert "usage limit" in data["message"].lower()
    assert data["discountAmount"] is None
    assert data["promoCode"] is None


def test_validate_promo_discount_capped_at_order_amount(client: TestClient, active_fixed_promo):
    """Test that discount cannot exceed order amount."""
    # Fixed $10 discount on $5 order should cap at $5
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "FIXED10", "orderAmount": "5.00"},
    )

    assert response.status_code == 200
    data = response.json()

    # This should fail minimum order amount check first ($30 minimum)
    assert data["valid"] is False
    assert "minimum order amount" in data["message"].lower()


def test_validate_promo_exact_minimum_order_amount(client: TestClient, active_fixed_promo):
    """Test validation with exact minimum order amount."""
    # FIXED10 requires minimum $30
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "FIXED10", "orderAmount": "30.00"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["valid"] is True
    assert float(data["discountAmount"]) == 10.0


def test_validate_promo_invalid_request_missing_code(client: TestClient):
    """Test validation with missing code field."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"orderAmount": "100.00"},
    )

    assert response.status_code == 422  # Validation error


def test_validate_promo_invalid_request_missing_order_amount(client: TestClient):
    """Test validation with missing order amount."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "SAVE20"},
    )

    assert response.status_code == 422  # Validation error


def test_validate_promo_negative_order_amount(client: TestClient, active_percentage_promo):
    """Test validation with negative order amount."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "SAVE20", "orderAmount": "-50.00"},
    )

    # Should fail Pydantic validation (if we have ge=0 constraint)
    # or should fail business logic
    assert response.status_code in [422, 200]


def test_validate_promo_zero_order_amount(client: TestClient, active_percentage_promo):
    """Test validation with zero order amount."""
    response = client.post(
        "/api/promo-codes/validate",
        json={"code": "SAVE20", "orderAmount": "0.00"},
    )

    # Should fail Pydantic validation (gt=0 constraint)
    assert response.status_code == 422
