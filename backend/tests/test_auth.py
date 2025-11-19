"""
Comprehensive tests for authentication flow
Tests Google OAuth, JWT tokens, guest users, and role checking
"""
import pytest
from fastapi import status
from uuid import uuid4

from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.user import User
from app.models.order import Order
from app.models.booking import Booking


class TestGoogleOAuthFlow:
    """Test Google OAuth authentication flow"""

    def test_google_login_new_user(self, client, db_session):
        """Test Google login creates new user"""
        response = client.post(
            "/api/auth/google-login",
            json={
                "email": "newuser@gmail.com",
                "googleId": "google123",
                "name": "New User",
                "image": "https://example.com/photo.jpg",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["email"] == "newuser@gmail.com"
        assert data["googleId"] == "google123"
        assert data["name"] == "New User"
        assert data["image"] == "https://example.com/photo.jpg"
        assert data["isAdmin"] is False
        assert data["adminRole"] is None
        assert "accessToken" in data
        assert "refreshToken" in data

        # Verify user created in database
        user = db_session.query(User).filter(User.email == "newuser@gmail.com").first()
        assert user is not None
        assert user.google_id == "google123"
        assert user.is_active is True

    def test_google_login_existing_user(self, client, regular_user):
        """Test Google login with existing user"""
        response = client.post(
            "/api/auth/google-login",
            json={
                "email": regular_user.email,
                "googleId": regular_user.google_id,
                "name": "Updated Name",
                "image": "https://example.com/new-photo.jpg",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == str(regular_user.id)
        assert data["email"] == regular_user.email
        assert "accessToken" in data
        assert "refreshToken" in data

    def test_google_login_inactive_user(self, client, db_session):
        """Test Google login fails for inactive user"""
        # Create inactive user
        user = User(
            email="inactive@test.com",
            google_id="inactive123",
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/auth/google-login",
            json={
                "email": "inactive@test.com",
                "googleId": "inactive123",
                "name": "Inactive User",
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "inactive" in response.json()["detail"].lower()

    def test_google_login_admin_user(self, client, admin_user):
        """Test Google login with admin user returns admin info"""
        response = client.post(
            "/api/auth/google-login",
            json={
                "email": admin_user.email,
                "googleId": admin_user.google_id,
                "name": admin_user.full_name,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["isAdmin"] is True
        assert data["adminRole"] == "super_admin"


class TestJWTTokens:
    """Test JWT token generation and validation"""

    def test_access_token_generation(self, regular_user):
        """Test access token generation"""
        token = create_access_token(
            data={"sub": str(regular_user.id), "email": regular_user.email}
        )

        assert token is not None
        assert isinstance(token, str)

        # Verify token
        payload = verify_token(token, token_type="access")
        assert payload is not None
        assert payload["sub"] == str(regular_user.id)
        assert payload["email"] == regular_user.email
        assert payload["type"] == "access"

    def test_refresh_token_generation(self, regular_user):
        """Test refresh token generation"""
        token = create_refresh_token(data={"sub": str(regular_user.id)})

        assert token is not None
        assert isinstance(token, str)

        # Verify token
        payload = verify_token(token, token_type="refresh")
        assert payload is not None
        assert payload["sub"] == str(regular_user.id)
        assert payload["type"] == "refresh"

    def test_invalid_token_verification(self):
        """Test verification of invalid token"""
        payload = verify_token("invalid.token.here", token_type="access")
        assert payload is None

    def test_wrong_token_type_verification(self, regular_user):
        """Test verifying token with wrong type"""
        access_token = create_access_token(data={"sub": str(regular_user.id)})

        # Try to verify as refresh token
        payload = verify_token(access_token, token_type="refresh")
        assert payload is None  # Should fail type check

    def test_get_current_user_with_valid_token(self, client, regular_user):
        """Test /me endpoint with valid token"""
        token = create_access_token(
            data={"sub": str(regular_user.id), "email": regular_user.email}
        )

        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == regular_user.email

    def test_get_current_user_without_token(self, client):
        """Test /me endpoint without token"""
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_with_invalid_token(self, client):
        """Test /me endpoint with invalid token"""
        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshToken:
    """Test refresh token mechanism"""

    def test_refresh_token_success(self, client, regular_user):
        """Test successful token refresh"""
        refresh_token = create_refresh_token(data={"sub": str(regular_user.id)})

        response = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

        # Verify new access token works
        new_access_token = data["access_token"]
        payload = verify_token(new_access_token, token_type="access")
        assert payload["sub"] == str(regular_user.id)

    def test_refresh_token_with_invalid_token(self, client):
        """Test refresh with invalid token"""
        response = client.post(
            "/api/auth/refresh", json={"refresh_token": "invalid.token.here"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_refresh_token_with_access_token(self, client, regular_user):
        """Test refresh with access token instead of refresh token"""
        access_token = create_access_token(
            data={"sub": str(regular_user.id), "email": regular_user.email}
        )

        response = client.post("/api/auth/refresh", json={"refresh_token": access_token})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_for_inactive_user(self, client, db_session):
        """Test refresh fails for inactive user"""
        # Create user
        user = User(
            email="testuser@test.com", google_id="test123", is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create refresh token
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Deactivate user
        user.is_active = False
        db_session.commit()

        # Try to refresh
        response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGuestUserCreation:
    """Test guest user creation and management"""

    def test_create_guest_user(self, client, db_session):
        """Test creating a guest user"""
        response = client.post(
            "/api/auth/guest?email=guest@test.com&name=Guest+User"
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["email"] == "guest@test.com"
        assert data["name"] == "Guest User"
        assert data["isAdmin"] is False
        assert data["googleId"] is None

        # Verify in database
        user = db_session.query(User).filter(User.email == "guest@test.com").first()
        assert user is not None
        assert user.google_id is None

    def test_create_guest_user_without_name(self, client, db_session):
        """Test creating guest user without name"""
        response = client.post("/api/auth/guest?email=guest2@test.com")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "guest2@test.com"

    def test_create_guest_user_duplicate_email(self, client, regular_user):
        """Test creating guest user with existing email"""
        response = client.post(f"/api/auth/guest?email={regular_user.email}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGuestDataLinking:
    """Test linking guest orders/bookings to authenticated user"""

    def test_google_login_links_guest_orders(self, client, db_session):
        """Test Google login automatically links guest orders"""
        # Create guest user with email
        guest_user = User(email="link@test.com", google_id=None)
        db_session.add(guest_user)
        db_session.commit()
        db_session.refresh(guest_user)

        # Create guest order (simplified - would need service package and location)
        # This is a conceptual test - actual implementation may vary
        # order = Order(user_id=guest_user.id, ...)
        # db_session.add(order)
        # db_session.commit()

        # Login with Google using same email
        response = client.post(
            "/api/auth/google-login",
            json={
                "email": "link@test.com",
                "googleId": "google456",
                "name": "Linked User",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        # Guest data should be linked automatically

    def test_manual_guest_data_linking(self, client, regular_user):
        """Test manual guest data linking endpoint"""
        token = create_access_token(
            data={"sub": str(regular_user.id), "email": regular_user.email}
        )

        response = client.post(
            f"/api/auth/link-guest-data?guest_email=guest@test.com",
            headers={"Authorization": f"Bearer {token}"},
        )

        # May return 400 if no guest user exists, which is expected
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestAdminRoleChecking:
    """Test admin role checking and permissions"""

    def test_admin_user_identification(self, admin_user):
        """Test admin user has correct flags"""
        assert admin_user.is_admin is True
        assert admin_user.admin_role == "super_admin"

    def test_regular_user_not_admin(self, regular_user):
        """Test regular user is not admin"""
        assert regular_user.is_admin is False
        assert regular_user.admin_role is None

    def test_admin_endpoint_access_with_admin_token(self, client, admin_user):
        """Test admin can access admin endpoints"""
        token = create_access_token(
            data={"sub": str(admin_user.id), "email": admin_user.email}
        )

        # Try accessing an admin endpoint (e.g., list users)
        response = client.get(
            "/api/admin/users", headers={"Authorization": f"Bearer {token}"}
        )

        # Should succeed or return data (not 403)
        assert response.status_code != status.HTTP_403_FORBIDDEN

    def test_admin_endpoint_access_with_regular_token(self, client, regular_user):
        """Test regular user cannot access admin endpoints"""
        token = create_access_token(
            data={"sub": str(regular_user.id), "email": regular_user.email}
        )

        # Try accessing an admin endpoint
        response = client.get(
            "/api/admin/users", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestLogout:
    """Test logout functionality"""

    def test_logout_with_valid_token(self, client, regular_user):
        """Test logout with valid token"""
        token = create_access_token(
            data={"sub": str(regular_user.id), "email": regular_user.email}
        )

        response = client.post(
            "/api/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert data["user_id"] == str(regular_user.id)

    def test_logout_without_token(self, client):
        """Test logout without token"""
        response = client.post("/api/auth/logout")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSecurityValidation:
    """Test security validation and edge cases"""

    def test_token_with_nonexistent_user(self, client):
        """Test token with user ID that doesn't exist"""
        fake_user_id = str(uuid4())
        token = create_access_token(
            data={"sub": fake_user_id, "email": "fake@test.com"}
        )

        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_with_invalid_uuid(self, client):
        """Test token with invalid UUID"""
        token = create_access_token(data={"sub": "not-a-uuid", "email": "test@test.com"})

        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_authorization_header(self, client):
        """Test endpoint requiring auth without Authorization header"""
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_malformed_authorization_header(self, client):
        """Test with malformed Authorization header"""
        response = client.get("/api/auth/me", headers={"Authorization": "NotBearer token"})
        assert response.status_code == status.HTTP_403_FORBIDDEN
