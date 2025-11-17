"""
Tests for public Service Package API endpoints
"""
import pytest
from uuid import uuid4


class TestPublicServicePackagesAPI:
    """Test suite for public service packages endpoints (no authentication required)"""

    def test_list_active_services(self, client, db_session):
        """Test listing active service packages"""
        from app.models.service import ServicePackage

        # Create test service packages
        active_package = ServicePackage(
            package_type="bridal_large",
            name="Luxury Bridal Package",
            description="Complete bridal makeup for large parties",
            base_bride_price=15000,
            base_maid_price=5000,
            base_mother_price=7000,
            base_other_price=4000,
            max_maids=10,
            min_maids=4,
            includes_facial=True,
            duration_minutes=300,
            is_active=True,
            display_order=1
        )
        inactive_package = ServicePackage(
            package_type="regular",
            name="Inactive Package",
            description="This should not appear",
            base_other_price=3000,
            duration_minutes=60,
            is_active=False
        )
        db_session.add_all([active_package, inactive_package])
        db_session.commit()

        # List services (no auth required)
        response = client.get("/api/services")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1  # Only active package
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Luxury Bridal Package"
        assert data["items"][0]["is_active"] is True

    def test_list_services_with_pagination(self, client, db_session):
        """Test service packages listing with pagination"""
        from app.models.service import ServicePackage

        # Create 25 active service packages
        for i in range(25):
            package = ServicePackage(
                package_type="regular",
                name=f"Package {i}",
                description=f"Description {i}",
                base_other_price=3000 + i * 100,
                duration_minutes=60,
                is_active=True,
                display_order=i
            )
            db_session.add(package)
        db_session.commit()

        # Get first page
        response = client.get("/api/services?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 3
        assert len(data["items"]) == 10

        # Get second page
        response = client.get("/api/services?page=2&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10

        # Get last page
        response = client.get("/api/services?page=3&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5

    def test_filter_services_by_package_type(self, client, db_session):
        """Test filtering service packages by type"""
        from app.models.service import ServicePackage

        bridal_package = ServicePackage(
            package_type="bridal_large",
            name="Bridal Package",
            base_bride_price=15000,
            duration_minutes=300,
            is_active=True
        )
        regular_package = ServicePackage(
            package_type="regular",
            name="Regular Package",
            base_other_price=3000,
            duration_minutes=60,
            is_active=True
        )
        db_session.add_all([bridal_package, regular_package])
        db_session.commit()

        # Filter by bridal_large
        response = client.get("/api/services?package_type=bridal_large")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["package_type"] == "bridal_large"

        # Filter by regular
        response = client.get("/api/services?package_type=regular")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["package_type"] == "regular"

    def test_get_service_details_by_id(self, client, db_session):
        """Test getting a specific active service package by ID"""
        from app.models.service import ServicePackage

        package = ServicePackage(
            package_type="bride_only",
            name="Bride Only Package",
            description="Makeup for bride only",
            base_bride_price=10000,
            includes_facial=True,
            duration_minutes=180,
            is_active=True
        )
        db_session.add(package)
        db_session.commit()
        db_session.refresh(package)

        # Get package details (no auth required)
        response = client.get(f"/api/services/{package.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Bride Only Package"
        assert data["package_type"] == "bride_only"
        assert float(data["base_bride_price"]) == 10000
        assert data["includes_facial"] is True
        assert data["is_active"] is True

    def test_get_inactive_service_returns_404(self, client, db_session):
        """Test that inactive service packages return 404 for public endpoint"""
        from app.models.service import ServicePackage

        inactive_package = ServicePackage(
            package_type="regular",
            name="Inactive Package",
            base_other_price=3000,
            duration_minutes=60,
            is_active=False
        )
        db_session.add(inactive_package)
        db_session.commit()
        db_session.refresh(inactive_package)

        # Try to get inactive package (should return 404)
        response = client.get(f"/api/services/{inactive_package.id}")
        assert response.status_code == 404

    def test_get_nonexistent_service_returns_404(self, client):
        """Test getting a service package that doesn't exist"""
        fake_id = uuid4()
        response = client.get(f"/api/services/{fake_id}")
        assert response.status_code == 404

    def test_services_ordered_by_display_order(self, client, db_session):
        """Test that service packages are ordered by display_order"""
        from app.models.service import ServicePackage

        # Create packages with different display orders
        package1 = ServicePackage(
            package_type="regular",
            name="Package C",
            base_other_price=3000,
            duration_minutes=60,
            is_active=True,
            display_order=3
        )
        package2 = ServicePackage(
            package_type="regular",
            name="Package A",
            base_other_price=3000,
            duration_minutes=60,
            is_active=True,
            display_order=1
        )
        package3 = ServicePackage(
            package_type="regular",
            name="Package B",
            base_other_price=3000,
            duration_minutes=60,
            is_active=True,
            display_order=2
        )
        db_session.add_all([package1, package2, package3])
        db_session.commit()

        response = client.get("/api/services")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 3
        # Should be ordered by display_order
        assert data["items"][0]["name"] == "Package A"  # display_order = 1
        assert data["items"][1]["name"] == "Package B"  # display_order = 2
        assert data["items"][2]["name"] == "Package C"  # display_order = 3

    def test_service_pricing_breakdown_included(self, client, db_session):
        """Test that pricing breakdown is included in response"""
        from app.models.service import ServicePackage

        package = ServicePackage(
            package_type="bridal_large",
            name="Full Bridal Package",
            description="Complete bridal party makeup",
            base_bride_price=15000,
            base_maid_price=5000,
            base_mother_price=7000,
            base_other_price=4000,
            max_maids=10,
            min_maids=4,
            includes_facial=True,
            duration_minutes=300,
            is_active=True
        )
        db_session.add(package)
        db_session.commit()
        db_session.refresh(package)

        response = client.get(f"/api/services/{package.id}")
        assert response.status_code == 200

        data = response.json()
        # Verify all pricing fields are present
        assert "base_bride_price" in data
        assert "base_maid_price" in data
        assert "base_mother_price" in data
        assert "base_other_price" in data
        assert float(data["base_bride_price"]) == 15000
        assert float(data["base_maid_price"]) == 5000
        assert float(data["base_mother_price"]) == 7000
        assert float(data["base_other_price"]) == 4000

    def test_service_metadata_included(self, client, db_session):
        """Test that service metadata (duration, facial, etc.) is included"""
        from app.models.service import ServicePackage

        package = ServicePackage(
            package_type="bridal_small",
            name="Small Bridal Package",
            description="Perfect for intimate weddings",
            base_bride_price=12000,
            base_maid_price=4500,
            max_maids=3,
            min_maids=1,
            includes_facial=True,
            duration_minutes=240,
            is_active=True
        )
        db_session.add(package)
        db_session.commit()
        db_session.refresh(package)

        response = client.get(f"/api/services/{package.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["includes_facial"] is True
        assert data["duration_minutes"] == 240
        assert data["max_maids"] == 3
        assert data["min_maids"] == 1
        assert data["description"] == "Perfect for intimate weddings"

    def test_empty_services_list(self, client, db_session):
        """Test listing services when none exist"""
        response = client.get("/api/services")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
        assert data["page"] == 1
        assert data["total_pages"] == 1
