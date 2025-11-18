"""Tests for admin gallery management API."""
from datetime import datetime, timedelta

import pytest
from fastapi import status

from app.models.content import GalleryPost
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
def sample_gallery_posts(db_session):
    """Create sample gallery posts for testing."""
    posts = [
        GalleryPost(
            media_type="image",
            media_url="https://example.com/image1.jpg",
            thumbnail_url="https://example.com/thumb1.jpg",
            caption="Bridal makeup look",
            tags=["bridal", "wedding", "makeup"],
            source_type="instagram",
            is_featured=True,
            display_order=1,
            published_at=datetime.utcnow() - timedelta(days=5),
        ),
        GalleryPost(
            media_type="video",
            media_url="https://example.com/video1.mp4",
            thumbnail_url="https://example.com/thumb2.jpg",
            caption="Makeup tutorial",
            tags=["tutorial", "makeup"],
            source_type="tiktok",
            is_featured=False,
            display_order=2,
            published_at=datetime.utcnow() - timedelta(days=3),
        ),
        GalleryPost(
            media_type="image",
            media_url="https://example.com/image2.jpg",
            caption="Evening makeup",
            tags=["evening", "glam"],
            source_type="original",
            is_featured=False,
            display_order=3,
            published_at=datetime.utcnow() - timedelta(days=1),
        ),
        # Unpublished post
        GalleryPost(
            media_type="image",
            media_url="https://example.com/image3.jpg",
            caption="Upcoming post",
            tags=["preview"],
            source_type="original",
            is_featured=False,
            display_order=4,
            published_at=datetime.utcnow() + timedelta(days=7),
        ),
    ]
    for post in posts:
        db_session.add(post)
    db_session.commit()
    for post in posts:
        db_session.refresh(post)
    return posts


# Test: List all gallery posts (admin only)
def test_list_all_gallery_posts(client, admin_token, sample_gallery_posts):
    """Test listing all gallery posts including unpublished (admin only)."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/admin/gallery", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 4  # All posts including unpublished
    assert len(data["items"]) == 4


def test_list_gallery_posts_with_pagination(client, admin_token, sample_gallery_posts):
    """Test gallery post listing with pagination."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/admin/gallery?skip=0&limit=2", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 4
    assert data["page"] == 1
    assert data["pageSize"] == 2
    assert data["totalPages"] == 2


def test_list_gallery_posts_filter_by_media_type(client, admin_token, sample_gallery_posts):
    """Test filtering gallery posts by media type."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/admin/gallery?mediaType=image", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 3  # 3 images
    for item in data["items"]:
        assert item["mediaType"] == "image"


def test_list_gallery_posts_filter_by_source_type(client, admin_token, sample_gallery_posts):
    """Test filtering gallery posts by source type."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/admin/gallery?sourceType=instagram", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["sourceType"] == "instagram"


def test_list_gallery_posts_filter_by_featured(client, admin_token, sample_gallery_posts):
    """Test filtering gallery posts by featured status."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/admin/gallery?isFeatured=true", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["isFeatured"] is True


def test_list_gallery_posts_ordering(client, admin_token, sample_gallery_posts):
    """Test that gallery posts are ordered correctly (featured first, then display_order)."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/admin/gallery", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    items = data["items"]

    # First item should be featured
    assert items[0]["isFeatured"] is True

    # Display orders should be ascending for non-featured items
    non_featured = [item for item in items if not item["isFeatured"]]
    display_orders = [item["displayOrder"] for item in non_featured]
    assert display_orders == sorted(display_orders)


def test_list_gallery_posts_unauthorized(client, sample_gallery_posts):
    """Test that listing gallery posts requires authentication."""
    response = client.get("/api/admin/gallery")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_gallery_posts_non_admin(client, regular_token, sample_gallery_posts):
    """Test that regular users cannot access admin gallery listing."""
    headers = {"Authorization": f"Bearer {regular_token}"}
    response = client.get("/api/admin/gallery", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test: Get gallery post by ID
def test_get_gallery_post_by_id(client, admin_token, sample_gallery_posts):
    """Test getting a specific gallery post by ID."""
    post = sample_gallery_posts[0]
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/api/admin/gallery/{post.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(post.id)
    assert data["mediaType"] == post.media_type
    assert data["mediaUrl"] == post.media_url
    assert data["caption"] == post.caption


def test_get_unpublished_gallery_post(client, admin_token, sample_gallery_posts):
    """Test that admin can get unpublished gallery posts."""
    unpublished_post = sample_gallery_posts[3]
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/api/admin/gallery/{unpublished_post.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(unpublished_post.id)


def test_get_gallery_post_not_found(client, admin_token):
    """Test getting a non-existent gallery post."""
    from uuid import uuid4
    fake_id = uuid4()
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/api/admin/gallery/{fake_id}", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_gallery_post_unauthorized(client, sample_gallery_posts):
    """Test that getting a gallery post requires authentication."""
    post = sample_gallery_posts[0]
    response = client.get(f"/api/admin/gallery/{post.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_gallery_post_non_admin(client, regular_token, sample_gallery_posts):
    """Test that regular users cannot access admin gallery detail."""
    post = sample_gallery_posts[0]
    headers = {"Authorization": f"Bearer {regular_token}"}
    response = client.get(f"/api/admin/gallery/{post.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test: Create gallery post
def test_create_gallery_post(client, admin_token):
    """Test creating a new gallery post."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "mediaType": "image",
        "mediaUrl": "https://example.com/new-image.jpg",
        "thumbnailUrl": "https://example.com/new-thumb.jpg",
        "caption": "New makeup look",
        "tags": ["new", "makeup", "glam"],
        "sourceType": "original",
        "isFeatured": False,
        "displayOrder": 10,
    }
    response = client.post("/api/admin/gallery", json=data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result["mediaType"] == "image"
    assert result["mediaUrl"] == data["mediaUrl"]
    assert result["caption"] == data["caption"]
    assert result["tags"] == data["tags"]
    assert result["sourceType"] == "original"
    assert result["isFeatured"] is False
    assert result["displayOrder"] == 10
    assert "id" in result
    assert "publishedAt" in result


def test_create_gallery_post_minimal(client, admin_token):
    """Test creating a gallery post with minimal required fields."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "mediaType": "video",
        "mediaUrl": "https://example.com/video.mp4",
    }
    response = client.post("/api/admin/gallery", json=data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result["mediaType"] == "video"
    assert result["mediaUrl"] == data["mediaUrl"]
    assert result["isFeatured"] is False  # Default
    assert result["displayOrder"] == 0  # Default


def test_create_gallery_post_invalid_media_type(client, admin_token):
    """Test creating a gallery post with invalid media type."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "mediaType": "audio",  # Invalid
        "mediaUrl": "https://example.com/audio.mp3",
    }
    response = client.post("/api/admin/gallery", json=data, headers=headers)

    assert response.status_code == 422  # Validation error


def test_create_gallery_post_invalid_source_type(client, admin_token):
    """Test creating a gallery post with invalid source type."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {
        "mediaType": "image",
        "mediaUrl": "https://example.com/image.jpg",
        "sourceType": "facebook",  # Invalid
    }
    response = client.post("/api/admin/gallery", json=data, headers=headers)

    assert response.status_code == 422  # Validation error


def test_create_gallery_post_unauthorized(client):
    """Test that creating a gallery post requires authentication."""
    data = {
        "mediaType": "image",
        "mediaUrl": "https://example.com/image.jpg",
    }
    response = client.post("/api/admin/gallery", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_gallery_post_non_admin(client, regular_token):
    """Test that regular users cannot create gallery posts."""
    headers = {"Authorization": f"Bearer {regular_token}"}
    data = {
        "mediaType": "image",
        "mediaUrl": "https://example.com/image.jpg",
    }
    response = client.post("/api/admin/gallery", json=data, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test: Update gallery post
def test_update_gallery_post(client, admin_token, sample_gallery_posts):
    """Test updating a gallery post."""
    post = sample_gallery_posts[0]
    headers = {"Authorization": f"Bearer {admin_token}"}
    update_data = {
        "caption": "Updated caption",
        "isFeatured": False,
        "displayOrder": 100,
    }
    response = client.put(f"/api/admin/gallery/{post.id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["caption"] == "Updated caption"
    assert result["isFeatured"] is False
    assert result["displayOrder"] == 100
    # Other fields should remain unchanged
    assert result["mediaType"] == post.media_type
    assert result["mediaUrl"] == post.media_url


def test_update_gallery_post_tags(client, admin_token, sample_gallery_posts):
    """Test updating gallery post tags."""
    post = sample_gallery_posts[0]
    headers = {"Authorization": f"Bearer {admin_token}"}
    update_data = {
        "tags": ["updated", "tags", "list"],
    }
    response = client.put(f"/api/admin/gallery/{post.id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["tags"] == ["updated", "tags", "list"]


def test_update_gallery_post_not_found(client, admin_token):
    """Test updating a non-existent gallery post."""
    from uuid import uuid4
    fake_id = uuid4()
    headers = {"Authorization": f"Bearer {admin_token}"}
    update_data = {"caption": "Updated"}
    response = client.put(f"/api/admin/gallery/{fake_id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_gallery_post_unauthorized(client, sample_gallery_posts):
    """Test that updating a gallery post requires authentication."""
    post = sample_gallery_posts[0]
    update_data = {"caption": "Updated"}
    response = client.put(f"/api/admin/gallery/{post.id}", json=update_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_gallery_post_non_admin(client, regular_token, sample_gallery_posts):
    """Test that regular users cannot update gallery posts."""
    post = sample_gallery_posts[0]
    headers = {"Authorization": f"Bearer {regular_token}"}
    update_data = {"caption": "Updated"}
    response = client.put(f"/api/admin/gallery/{post.id}", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test: Delete gallery post
def test_delete_gallery_post(client, admin_token, sample_gallery_posts, db_session):
    """Test deleting a gallery post."""
    post = sample_gallery_posts[0]
    post_id = post.id
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/api/admin/gallery/{post_id}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify post is deleted
    from app.models.content import GalleryPost
    deleted_post = db_session.query(GalleryPost).filter(GalleryPost.id == post_id).first()
    assert deleted_post is None


def test_delete_gallery_post_not_found(client, admin_token):
    """Test deleting a non-existent gallery post."""
    from uuid import uuid4
    fake_id = uuid4()
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/api/admin/gallery/{fake_id}", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_gallery_post_unauthorized(client, sample_gallery_posts):
    """Test that deleting a gallery post requires authentication."""
    post = sample_gallery_posts[0]
    response = client.delete(f"/api/admin/gallery/{post.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_gallery_post_non_admin(client, regular_token, sample_gallery_posts):
    """Test that regular users cannot delete gallery posts."""
    post = sample_gallery_posts[0]
    headers = {"Authorization": f"Bearer {regular_token}"}
    response = client.delete(f"/api/admin/gallery/{post.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
