"""
Tests for Brand API endpoints
"""
import pytest
from uuid import uuid4


class TestBrandAPI:
    """Test suite for Brand CRUD operations"""

    def test_list_brands_as_admin(self, client, admin_headers, db_session):
        """Test listing brands as admin"""
        # Create test brands
        from app.models.product import Brand
        brand1 = Brand(name="Test Brand 1", slug="test-brand-1", is_active=True)
        brand2 = Brand(name="Test Brand 2", slug="test-brand-2", is_active=False)
        db_session.add_all([brand1, brand2])
        db_session.commit()

        # List all brands
        response = client.get("/api/admin/brands", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_brands_as_regular_user(self, client, user_headers):
        """Test listing brands as regular user (should fail)"""
        response = client.get("/api/admin/brands", headers=user_headers)
        assert response.status_code == 403

    def test_list_brands_unauthenticated(self, client):
        """Test listing brands without authentication (should fail)"""
        response = client.get("/api/admin/brands")
        assert response.status_code == 401

    def test_filter_brands_by_active_status(self, client, admin_headers, db_session):
        """Test filtering brands by active status"""
        from app.models.product import Brand
        brand1 = Brand(name="Active Brand", slug="active-brand", is_active=True)
        brand2 = Brand(name="Inactive Brand", slug="inactive-brand", is_active=False)
        db_session.add_all([brand1, brand2])
        db_session.commit()

        # Filter active brands
        response = client.get("/api/admin/brands?is_active=true", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Active Brand"

    def test_search_brands(self, client, admin_headers, db_session):
        """Test searching brands by name"""
        from app.models.product import Brand
        brand1 = Brand(name="MAC Cosmetics", slug="mac-cosmetics", description="Makeup brand")
        brand2 = Brand(name="NYX", slug="nyx", description="Budget makeup")
        db_session.add_all([brand1, brand2])
        db_session.commit()

        # Search for "MAC"
        response = client.get("/api/admin/brands?search=MAC", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "MAC Cosmetics"

    def test_get_brand_by_id(self, client, admin_headers, db_session):
        """Test getting a specific brand by ID"""
        from app.models.product import Brand
        brand = Brand(name="Test Brand", slug="test-brand")
        db_session.add(brand)
        db_session.commit()
        db_session.refresh(brand)

        response = client.get(f"/api/admin/brands/{brand.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Brand"
        assert data["slug"] == "test-brand"

    def test_get_nonexistent_brand(self, client, admin_headers):
        """Test getting a brand that doesn't exist"""
        fake_id = uuid4()
        response = client.get(f"/api/admin/brands/{fake_id}", headers=admin_headers)
        assert response.status_code == 404

    def test_create_brand(self, client, admin_headers):
        """Test creating a new brand"""
        brand_data = {
            "name": "New Brand",
            "description": "A new brand",
            "is_active": True
        }
        response = client.post("/api/admin/brands", json=brand_data, headers=admin_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Brand"
        assert data["slug"] == "new-brand"
        assert data["is_active"] is True

    def test_create_brand_with_logo(self, client, admin_headers):
        """Test creating a brand with logo URL"""
        brand_data = {
            "name": "Brand With Logo",
            "logo_url": "https://example.com/logo.png",
            "is_active": True
        }
        response = client.post("/api/admin/brands", json=brand_data, headers=admin_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["logo_url"] == "https://example.com/logo.png"

    def test_create_duplicate_brand(self, client, admin_headers, db_session):
        """Test creating a brand with duplicate name"""
        from app.models.product import Brand
        brand = Brand(name="Existing Brand", slug="existing-brand")
        db_session.add(brand)
        db_session.commit()

        brand_data = {
            "name": "Existing Brand",
            "is_active": True
        }
        response = client.post("/api/admin/brands", json=brand_data, headers=admin_headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_brand(self, client, admin_headers, db_session):
        """Test updating a brand"""
        from app.models.product import Brand
        brand = Brand(name="Old Name", slug="old-name")
        db_session.add(brand)
        db_session.commit()
        db_session.refresh(brand)

        update_data = {
            "name": "New Name",
            "description": "Updated description"
        }
        response = client.put(f"/api/admin/brands/{brand.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["slug"] == "new-name"
        assert data["description"] == "Updated description"

    def test_update_brand_to_duplicate_name(self, client, admin_headers, db_session):
        """Test updating a brand to a name that already exists"""
        from app.models.product import Brand
        brand1 = Brand(name="Brand 1", slug="brand-1")
        brand2 = Brand(name="Brand 2", slug="brand-2")
        db_session.add_all([brand1, brand2])
        db_session.commit()
        db_session.refresh(brand1)

        update_data = {"name": "Brand 2"}
        response = client.put(f"/api/admin/brands/{brand1.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_nonexistent_brand(self, client, admin_headers):
        """Test updating a brand that doesn't exist"""
        fake_id = uuid4()
        update_data = {"name": "New Name"}
        response = client.put(f"/api/admin/brands/{fake_id}", json=update_data, headers=admin_headers)
        assert response.status_code == 404

    def test_delete_brand(self, client, admin_headers, db_session):
        """Test deleting a brand"""
        from app.models.product import Brand
        brand = Brand(name="To Delete", slug="to-delete")
        db_session.add(brand)
        db_session.commit()
        db_session.refresh(brand)

        response = client.delete(f"/api/admin/brands/{brand.id}", headers=admin_headers)
        assert response.status_code == 204

        # Verify brand is deleted
        db_session.expire_all()
        deleted_brand = db_session.query(Brand).filter(Brand.id == brand.id).first()
        assert deleted_brand is None

    def test_delete_brand_with_products(self, client, admin_headers, db_session):
        """Test deleting a brand that has associated products"""
        from app.models.product import Brand, Product, Category

        # Create category first
        category = Category(name="Test Category", slug="test-category")
        db_session.add(category)
        db_session.commit()

        brand = Brand(name="Brand With Products", slug="brand-with-products")
        db_session.add(brand)
        db_session.commit()
        db_session.refresh(brand)

        # Create product associated with brand
        product = Product(
            title="Test Product",
            slug="test-product",
            brand_id=brand.id,
            category_id=category.id,
            base_price=100
        )
        db_session.add(product)
        db_session.commit()

        response = client.delete(f"/api/admin/brands/{brand.id}", headers=admin_headers)
        assert response.status_code == 400
        assert "associated products" in response.json()["detail"]

    def test_delete_nonexistent_brand(self, client, admin_headers):
        """Test deleting a brand that doesn't exist"""
        fake_id = uuid4()
        response = client.delete(f"/api/admin/brands/{fake_id}", headers=admin_headers)
        assert response.status_code == 404

    def test_pagination(self, client, admin_headers, db_session):
        """Test brand list pagination"""
        from app.models.product import Brand
        # Create 25 brands
        for i in range(25):
            brand = Brand(name=f"Brand {i}", slug=f"brand-{i}")
            db_session.add(brand)
        db_session.commit()

        # Get first page
        response = client.get("/api/admin/brands?page=1&page_size=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 3
        assert len(data["items"]) == 10

        # Get second page
        response = client.get("/api/admin/brands?page=2&page_size=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10

        # Get last page
        response = client.get("/api/admin/brands?page=3&page_size=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
