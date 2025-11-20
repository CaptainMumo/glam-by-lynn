"""
Tests for booking history API endpoints
"""
import pytest
from datetime import date, time, timedelta


class TestBookingHistoryAPI:
    """Test suite for booking history endpoints (authentication required)"""

    def test_list_user_bookings(self, client, db_session, admin_user, admin_headers):
        """Test listing authenticated user's bookings"""
        from app.models.service import ServicePackage, TransportLocation
        from app.models.booking import Booking

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

        # Create bookings for admin user
        booking1 = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=5),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="pending"
        )
        booking2 = Booking(
            booking_number="BK0002",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=10),
            booking_time=time(14, 0),
            num_others=2,
            subtotal=6000,
            transport_cost=500,
            total_amount=6500,
            status="confirmed"
        )
        db_session.add_all([booking1, booking2])
        db_session.commit()

        # List bookings
        response = client.get("/api/bookings", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["page"] == 1

    def test_list_bookings_no_auth(self, client):
        """Test that listing bookings without authentication fails"""
        response = client.get("/api/bookings")
        assert response.status_code == 401  # Unauthorized

    def test_list_bookings_with_pagination(self, client, db_session, admin_user, admin_headers):
        """Test booking list pagination"""
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

        # Create 25 bookings
        for i in range(25):
            booking = Booking(
                booking_number=f"BK{i:04d}",
                user_id=admin_user.id,
                package_id=package.id,
                location_id=location.id,
                booking_date=date.today() + timedelta(days=i+1),
                booking_time=time(10, 0),
                num_others=1,
                subtotal=3000,
                transport_cost=500,
                total_amount=3500,
                status="pending"
            )
            db_session.add(booking)
        db_session.commit()

        # Get first page
        response = client.get("/api/bookings?page=1&page_size=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 3
        assert len(data["items"]) == 10

        # Get second page
        response = client.get("/api/bookings?page=2&page_size=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10

        # Get last page
        response = client.get("/api/bookings?page=3&page_size=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5

    def test_filter_bookings_by_status(self, client, db_session, admin_user, admin_headers):
        """Test filtering bookings by status"""
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

        # Create bookings with different statuses
        pending_booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=5),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="pending"
        )
        confirmed_booking = Booking(
            booking_number="BK0002",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=10),
            booking_time=time(14, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="confirmed"
        )
        completed_booking = Booking(
            booking_number="BK0003",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() - timedelta(days=5),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="completed"
        )
        db_session.add_all([pending_booking, confirmed_booking, completed_booking])
        db_session.commit()

        # Filter by pending
        response = client.get("/api/bookings?status=pending", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "pending"

        # Filter by confirmed
        response = client.get("/api/bookings?status=confirmed", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "confirmed"

        # Filter by completed
        response = client.get("/api/bookings?status=completed", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "completed"

    def test_bookings_sorted_by_date(self, client, db_session, admin_user, admin_headers):
        """Test that bookings are sorted by date (newest first)"""
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

        # Create bookings with different dates (in random order)
        booking1 = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=5),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="pending"
        )
        booking2 = Booking(
            booking_number="BK0002",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=15),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="pending"
        )
        booking3 = Booking(
            booking_number="BK0003",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=10),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="pending"
        )
        db_session.add_all([booking1, booking2, booking3])
        db_session.commit()

        # List bookings
        response = client.get("/api/bookings", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        # Should be sorted by date descending (newest first)
        assert data["items"][0]["booking_number"] == "BK0002"  # 15 days ahead
        assert data["items"][1]["booking_number"] == "BK0003"  # 10 days ahead
        assert data["items"][2]["booking_number"] == "BK0001"  # 5 days ahead

    def test_get_booking_details(self, client, db_session, admin_user, admin_headers):
        """Test getting specific booking details"""
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

        # Create booking
        booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=5),
            booking_time=time(10, 0),
            num_others=1,
            wedding_theme="Elegant Garden",
            special_requests="Natural look preferred",
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            deposit_amount=1750,
            status="pending"
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        # Get booking details
        response = client.get(f"/api/bookings/{booking.id}", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["booking_number"] == "BK0001"
        assert data["status"] == "pending"
        assert data["wedding_theme"] == "Elegant Garden"
        assert data["special_requests"] == "Natural look preferred"
        assert float(data["total_amount"]) == 3500
        assert float(data["deposit_amount"]) == 1750

    def test_get_booking_details_no_auth(self, client, db_session, admin_user):
        """Test that getting booking details without authentication fails"""
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

        booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=5),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="pending"
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        # Try without authentication
        response = client.get(f"/api/bookings/{booking.id}")
        assert response.status_code == 401

    def test_get_booking_other_user(self, client, db_session, admin_user, regular_user, user_headers):
        """Test that users cannot access other users' bookings"""
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

        # Create booking for admin user
        booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,  # Admin user's booking
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=5),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="pending"
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        # Try to access with regular user credentials
        response = client.get(f"/api/bookings/{booking.id}", headers=user_headers)
        assert response.status_code == 404  # Not found (user doesn't have access)

    def test_get_nonexistent_booking(self, client, admin_headers):
        """Test getting a booking that doesn't exist"""
        from uuid import uuid4

        fake_id = uuid4()
        response = client.get(f"/api/bookings/{fake_id}", headers=admin_headers)
        assert response.status_code == 404

    def test_empty_booking_list(self, client, admin_headers):
        """Test listing bookings when user has none"""
        response = client.get("/api/bookings", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
        assert data["page"] == 1
        assert data["total_pages"] == 1
