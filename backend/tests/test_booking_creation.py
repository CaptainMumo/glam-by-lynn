"""
Tests for booking creation API endpoints
"""
import pytest
from datetime import date, time, timedelta


class TestBookingCreationAPI:
    """Test suite for booking creation endpoints"""

    def test_create_guest_booking(self, client, db_session):
        """Test creating a booking as a guest (no authentication)"""
        from app.models.service import ServicePackage, TransportLocation

        # Create test package and location
        package = ServicePackage(
            package_type="regular",
            name="Regular Makeup",
            base_other_price=3000,
            duration_minutes=60,
            is_active=True
        )
        location = TransportLocation(
            location_name="Nairobi CBD",
            transport_cost=500,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        # Create booking data
        booking_date = (date.today() + timedelta(days=3)).isoformat()
        booking_data = {
            "package_id": str(package.id),
            "booking_date": booking_date,
            "booking_time": "10:00:00",
            "location_id": str(location.id),
            "num_brides": 0,
            "num_maids": 0,
            "num_mothers": 0,
            "num_others": 1,
            "guest_email": "guest@example.com",
            "guest_name": "Jane Doe",
            "guest_phone": "+254712345678"
        }

        response = client.post("/api/bookings", json=booking_data)
        assert response.status_code == 201

        data = response.json()
        assert data["status"] == "pending"
        assert data["guest_email"] == "guest@example.com"
        assert data["guest_name"] == "Jane Doe"
        assert float(data["subtotal"]) == 3000
        assert float(data["transport_cost"]) == 500
        assert float(data["total_amount"]) == 3500
        assert float(data["deposit_amount"]) == 1750  # 50%
        assert "booking_number" in data
        assert data["booking_number"].startswith("BK")

    def test_create_authenticated_booking(self, client, db_session, admin_headers):
        """Test creating a booking as an authenticated user"""
        from app.models.service import ServicePackage, TransportLocation

        # Create test package and location
        package = ServicePackage(
            package_type="bride_only",
            name="Bride Only Package",
            base_bride_price=10000,
            duration_minutes=180,
            is_active=True
        )
        location = TransportLocation(
            location_name="Kitui Town",
            transport_cost=1000,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        # Create booking data (no guest info required for authenticated users)
        booking_date = (date.today() + timedelta(days=5)).isoformat()
        booking_data = {
            "package_id": str(package.id),
            "booking_date": booking_date,
            "booking_time": "14:00:00",
            "location_id": str(location.id),
            "num_brides": 1,
            "num_maids": 0,
            "num_mothers": 0,
            "num_others": 0
        }

        response = client.post("/api/bookings", json=booking_data, headers=admin_headers)
        assert response.status_code == 201

        data = response.json()
        assert data["status"] == "pending"
        assert data["user_id"] is not None  # Should have user_id
        assert float(data["subtotal"]) == 10000
        assert float(data["transport_cost"]) == 1000
        assert float(data["total_amount"]) == 11000
        assert float(data["deposit_amount"]) == 5500

    def test_create_booking_missing_guest_info(self, client, db_session):
        """Test that guest bookings without contact info fail"""
        from app.models.service import ServicePackage, TransportLocation

        package = ServicePackage(
            package_type="regular",
            name="Regular Makeup",
            base_other_price=3000,
            duration_minutes=60,
            is_active=True
        )
        location = TransportLocation(
            location_name="Nairobi CBD",
            transport_cost=500,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        # Missing guest info
        booking_date = (date.today() + timedelta(days=3)).isoformat()
        booking_data = {
            "package_id": str(package.id),
            "booking_date": booking_date,
            "booking_time": "10:00:00",
            "location_id": str(location.id),
            "num_others": 1
        }

        response = client.post("/api/bookings", json=booking_data)
        assert response.status_code == 400
        assert "require email, name, and phone" in response.json()["detail"]

    def test_create_booking_unavailable_slot(self, client, db_session):
        """Test that booking unavailable slot fails"""
        from app.models.service import ServicePackage, TransportLocation
        from app.models.booking import Booking

        package = ServicePackage(
            package_type="regular",
            name="Regular Makeup",
            base_other_price=3000,
            duration_minutes=60,
            is_active=True
        )
        location = TransportLocation(
            location_name="Nairobi CBD",
            transport_cost=500,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        # Create existing booking
        booking_date = date.today() + timedelta(days=3)
        booking_time = time(10, 0)
        existing_booking = Booking(
            booking_number="BK0001",
            package_id=package.id,
            location_id=location.id,
            booking_date=booking_date,
            booking_time=booking_time,
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="confirmed",
            guest_email="existing@example.com",
            guest_name="Existing User",
            guest_phone="1234567890"
        )
        db_session.add(existing_booking)
        db_session.commit()

        # Try to book same slot
        booking_data = {
            "package_id": str(package.id),
            "booking_date": booking_date.isoformat(),
            "booking_time": "10:00:00",
            "location_id": str(location.id),
            "num_others": 1,
            "guest_email": "new@example.com",
            "guest_name": "New User",
            "guest_phone": "0987654321"
        }

        response = client.post("/api/bookings", json=booking_data)
        assert response.status_code == 400
        assert "not available" in response.json()["detail"]

    def test_create_booking_inactive_package(self, client, db_session):
        """Test that booking inactive package fails"""
        from app.models.service import ServicePackage, TransportLocation

        package = ServicePackage(
            package_type="regular",
            name="Inactive Package",
            base_other_price=3000,
            duration_minutes=60,
            is_active=False  # Inactive
        )
        location = TransportLocation(
            location_name="Nairobi CBD",
            transport_cost=500,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        booking_date = (date.today() + timedelta(days=3)).isoformat()
        booking_data = {
            "package_id": str(package.id),
            "booking_date": booking_date,
            "booking_time": "10:00:00",
            "location_id": str(location.id),
            "num_others": 1,
            "guest_email": "guest@example.com",
            "guest_name": "Jane Doe",
            "guest_phone": "+254712345678"
        }

        response = client.post("/api/bookings", json=booking_data)
        assert response.status_code == 400
        assert "not currently available" in response.json()["detail"]

    def test_create_booking_exceeds_max_maids(self, client, db_session):
        """Test that exceeding max maids fails"""
        from app.models.service import ServicePackage, TransportLocation

        package = ServicePackage(
            package_type="bridal_small",
            name="Small Bridal Package",
            base_bride_price=12000,
            base_maid_price=4500,
            max_maids=3,
            min_maids=1,
            duration_minutes=240,
            is_active=True
        )
        location = TransportLocation(
            location_name="Nairobi CBD",
            transport_cost=500,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        booking_date = (date.today() + timedelta(days=3)).isoformat()
        booking_data = {
            "package_id": str(package.id),
            "booking_date": booking_date,
            "booking_time": "10:00:00",
            "location_id": str(location.id),
            "num_brides": 1,
            "num_maids": 5,  # Exceeds max of 3
            "guest_email": "guest@example.com",
            "guest_name": "Jane Doe",
            "guest_phone": "+254712345678"
        }

        response = client.post("/api/bookings", json=booking_data)
        assert response.status_code == 400
        assert "exceeds maximum allowed" in response.json()["detail"]

    def test_create_booking_below_min_maids(self, client, db_session):
        """Test that being below min maids fails"""
        from app.models.service import ServicePackage, TransportLocation

        package = ServicePackage(
            package_type="bridal_small",
            name="Small Bridal Package",
            base_bride_price=12000,
            base_maid_price=4500,
            max_maids=3,
            min_maids=1,
            duration_minutes=240,
            is_active=True
        )
        location = TransportLocation(
            location_name="Nairobi CBD",
            transport_cost=500,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        booking_date = (date.today() + timedelta(days=3)).isoformat()
        booking_data = {
            "package_id": str(package.id),
            "booking_date": booking_date,
            "booking_time": "10:00:00",
            "location_id": str(location.id),
            "num_brides": 1,
            "num_maids": 0,  # Below min of 1
            "guest_email": "guest@example.com",
            "guest_name": "Jane Doe",
            "guest_phone": "+254712345678"
        }

        response = client.post("/api/bookings", json=booking_data)
        assert response.status_code == 400
        assert "below minimum required" in response.json()["detail"]

    def test_create_booking_complex_pricing(self, client, db_session):
        """Test complex booking with multiple attendee types"""
        from app.models.service import ServicePackage, TransportLocation

        package = ServicePackage(
            package_type="bridal_large",
            name="Large Bridal Package",
            base_bride_price=15000,
            base_maid_price=5000,
            base_mother_price=7000,
            base_other_price=4000,
            max_maids=10,
            min_maids=4,
            duration_minutes=300,
            is_active=True
        )
        location = TransportLocation(
            location_name="Westlands",
            transport_cost=800,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        booking_date = (date.today() + timedelta(days=7)).isoformat()
        booking_data = {
            "package_id": str(package.id),
            "booking_date": booking_date,
            "booking_time": "09:00:00",
            "location_id": str(location.id),
            "num_brides": 1,
            "num_maids": 5,
            "num_mothers": 2,
            "num_others": 3,
            "wedding_theme": "Rustic Outdoor",
            "special_requests": "Natural makeup look preferred",
            "guest_email": "bride@example.com",
            "guest_name": "Mary Smith",
            "guest_phone": "+254700123456"
        }

        response = client.post("/api/bookings", json=booking_data)
        assert response.status_code == 201

        data = response.json()
        # 1 bride (15000) + 5 maids (25000) + 2 mothers (14000) + 3 others (12000) = 66000
        # Transport = 800
        # Total = 66800
        # Deposit = 33400
        assert float(data["subtotal"]) == 66000
        assert float(data["transport_cost"]) == 800
        assert float(data["total_amount"]) == 66800
        assert float(data["deposit_amount"]) == 33400
        assert data["wedding_theme"] == "Rustic Outdoor"
        assert data["special_requests"] == "Natural makeup look preferred"

    def test_booking_number_format(self, client, db_session):
        """Test that booking numbers follow correct format"""
        from app.models.service import ServicePackage, TransportLocation
        import re

        package = ServicePackage(
            package_type="regular",
            name="Regular Makeup",
            base_other_price=3000,
            duration_minutes=60,
            is_active=True
        )
        location = TransportLocation(
            location_name="Nairobi CBD",
            transport_cost=500,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        booking_date = (date.today() + timedelta(days=3)).isoformat()
        booking_data = {
            "package_id": str(package.id),
            "booking_date": booking_date,
            "booking_time": "10:00:00",
            "location_id": str(location.id),
            "num_others": 1,
            "guest_email": "guest@example.com",
            "guest_name": "Jane Doe",
            "guest_phone": "+254712345678"
        }

        response = client.post("/api/bookings", json=booking_data)
        assert response.status_code == 201

        data = response.json()
        # Format: BK{YYYYMMDD}{####}
        pattern = r"^BK\d{8}\d{4}$"
        assert re.match(pattern, data["booking_number"])

    def test_booking_number_uniqueness(self, client, db_session):
        """Test that booking numbers are unique"""
        from app.models.service import ServicePackage, TransportLocation

        package = ServicePackage(
            package_type="regular",
            name="Regular Makeup",
            base_other_price=3000,
            duration_minutes=60,
            is_active=True
        )
        location = TransportLocation(
            location_name="Nairobi CBD",
            transport_cost=500,
            is_active=True
        )
        db_session.add_all([package, location])
        db_session.commit()
        db_session.refresh(package)
        db_session.refresh(location)

        booking_numbers = set()

        # Create 5 bookings
        for i in range(5):
            booking_date = (date.today() + timedelta(days=3 + i)).isoformat()
            booking_data = {
                "package_id": str(package.id),
                "booking_date": booking_date,
                "booking_time": f"{10 + i}:00:00",
                "location_id": str(location.id),
                "num_others": 1,
                "guest_email": f"guest{i}@example.com",
                "guest_name": f"Guest {i}",
                "guest_phone": f"+25470000{i:04d}"
            }

            response = client.post("/api/bookings", json=booking_data)
            assert response.status_code == 201

            data = response.json()
            booking_numbers.add(data["booking_number"])

        # All booking numbers should be unique
        assert len(booking_numbers) == 5
