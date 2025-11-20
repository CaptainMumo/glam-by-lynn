"""
Tests for booking cancellation API endpoints
"""
import pytest
from datetime import date, time, timedelta


class TestBookingCancellationAPI:
    """Test suite for booking cancellation endpoints"""

    def test_cancel_booking_success(self, client, db_session, admin_user, admin_headers):
        """Test successfully cancelling a booking"""
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

        # Create booking (3 days in future - well within 24 hour window)
        booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=3),
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

        # Cancel booking
        response = client.put(f"/api/bookings/{booking.id}/cancel", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "cancelled"
        assert data["booking_number"] == "BK0001"
        assert "admin_notes" in data
        assert data["admin_notes"] is not None  # Should have cancellation note

    def test_cancel_booking_no_auth(self, client, db_session, admin_user):
        """Test that cancelling without authentication fails"""
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
            booking_date=date.today() + timedelta(days=3),
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

        # Try to cancel without authentication
        response = client.put(f"/api/bookings/{booking.id}/cancel")
        assert response.status_code == 401

    def test_cancel_other_user_booking(self, client, db_session, admin_user, regular_user, user_headers):
        """Test that users cannot cancel other users' bookings"""
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
            user_id=admin_user.id,  # Admin's booking
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=3),
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

        # Try to cancel with regular user credentials
        response = client.put(f"/api/bookings/{booking.id}/cancel", headers=user_headers)
        assert response.status_code == 404  # Not found (doesn't have access)

    def test_cancel_booking_less_than_24_hours(self, client, db_session, admin_user, admin_headers):
        """Test that cancelling with less than 24 hours notice fails"""
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

        # Create booking for tomorrow (less than 24 hours)
        booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=1),
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

        # Try to cancel
        response = client.put(f"/api/bookings/{booking.id}/cancel", headers=admin_headers)
        assert response.status_code == 400
        assert "24 hours" in response.json()["detail"]

    def test_cancel_already_cancelled_booking(self, client, db_session, admin_user, admin_headers):
        """Test that cancelling an already cancelled booking fails"""
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

        # Create already cancelled booking
        booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=3),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="cancelled"  # Already cancelled
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        # Try to cancel again
        response = client.put(f"/api/bookings/{booking.id}/cancel", headers=admin_headers)
        assert response.status_code == 400
        assert "already cancelled" in response.json()["detail"]

    def test_cancel_completed_booking(self, client, db_session, admin_user, admin_headers):
        """Test that cancelling a completed booking fails"""
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

        # Create completed booking
        booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() - timedelta(days=5),  # Past date
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="completed"
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        # Try to cancel
        response = client.put(f"/api/bookings/{booking.id}/cancel", headers=admin_headers)
        assert response.status_code == 400
        assert "completed" in response.json()["detail"].lower()

    def test_cancel_nonexistent_booking(self, client, admin_headers):
        """Test cancelling a booking that doesn't exist"""
        from uuid import uuid4

        fake_id = uuid4()
        response = client.put(f"/api/bookings/{fake_id}/cancel", headers=admin_headers)
        assert response.status_code == 404

    def test_cancelled_booking_frees_slot(self, client, db_session, admin_user, admin_headers):
        """Test that cancelled bookings free up the calendar slot"""
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
        booking_date = date.today() + timedelta(days=5)
        booking_time_slot = time(14, 0)

        booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=booking_date,
            booking_time=booking_time_slot,
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="confirmed"
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        # Check availability - slot should be unavailable
        response = client.get(
            f"/api/bookings/availability?start_date={booking_date.isoformat()}&days=1"
        )
        assert response.status_code == 200
        data = response.json()

        # Find the time slot in the response
        date_availability = data["dates"][0]
        slot_14_00 = next((s for s in date_availability["slots"] if s["time"] == "14:00:00"), None)
        assert slot_14_00 is not None
        assert slot_14_00["is_available"] is False
        assert slot_14_00["reason"] == "Booked"

        # Cancel the booking
        cancel_response = client.put(f"/api/bookings/{booking.id}/cancel", headers=admin_headers)
        assert cancel_response.status_code == 200

        # Check availability again - slot should now be available
        response = client.get(
            f"/api/bookings/availability?start_date={booking_date.isoformat()}&days=1"
        )
        assert response.status_code == 200
        data = response.json()

        date_availability = data["dates"][0]
        slot_14_00 = next((s for s in date_availability["slots"] if s["time"] == "14:00:00"), None)
        assert slot_14_00 is not None
        assert slot_14_00["is_available"] is True
        assert slot_14_00["reason"] is None

    def test_cancellation_adds_admin_notes(self, client, db_session, admin_user, admin_headers):
        """Test that cancellation adds timestamp to admin notes"""
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

        # Create booking with existing admin notes
        booking = Booking(
            booking_number="BK0001",
            user_id=admin_user.id,
            package_id=package.id,
            location_id=location.id,
            booking_date=date.today() + timedelta(days=3),
            booking_time=time(10, 0),
            num_others=1,
            subtotal=3000,
            transport_cost=500,
            total_amount=3500,
            status="pending",
            admin_notes="Previous note"
        )
        db_session.add(booking)
        db_session.commit()
        db_session.refresh(booking)

        # Cancel booking
        response = client.put(f"/api/bookings/{booking.id}/cancel", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert "Previous note" in data["admin_notes"]
        assert "Cancelled" in data["admin_notes"]
        # Should have timestamp in format [YYYY-MM-DD HH:MM]
        import re
        assert re.search(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]", data["admin_notes"])
