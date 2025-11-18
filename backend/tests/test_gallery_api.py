"""Tests for gallery API endpoints."""
from datetime import datetime, timedelta

import pytest
from fastapi import status

from app.models.content import GalleryPost


@pytest.fixture
def sample_gallery_posts(db_session):
    """Create sample gallery posts for testing."""
    now = datetime.utcnow()

    posts = [
        # Published image posts
        GalleryPost(
            media_type="image",
            media_url="https://example.com/image1.jpg",
            thumbnail_url="https://example.com/thumb1.jpg",
            caption="Beautiful bridal makeup",
            tags=["bridal", "makeup", "wedding"],
            source_type="instagram",
            is_featured=True,
            display_order=1,
            published_at=now - timedelta(days=5),
        ),
        GalleryPost(
            media_type="image",
            media_url="https://example.com/image2.jpg",
            thumbnail_url="https://example.com/thumb2.jpg",
            caption="Glam makeup look",
            tags=["glam", "makeup"],
            source_type="original",
            is_featured=False,
            display_order=2,
            published_at=now - timedelta(days=3),
        ),
        # Published video posts
        GalleryPost(
            media_type="video",
            media_url="https://example.com/video1.mp4",
            thumbnail_url="https://example.com/video1_thumb.jpg",
            caption="Makeup tutorial",
            tags=["tutorial", "makeup"],
            source_type="tiktok",
            is_featured=False,
            display_order=3,
            published_at=now - timedelta(days=2),
        ),
        # Future post (not yet published)
        GalleryPost(
            media_type="image",
            media_url="https://example.com/future.jpg",
            caption="Future post",
            tags=["future"],
            source_type="instagram",
            is_featured=False,
            display_order=4,
            published_at=now + timedelta(days=1),
        ),
    ]

    for post in posts:
        db_session.add(post)
    db_session.commit()

    # Refresh all posts
    for post in posts:
        db_session.refresh(post)

    return posts


def test_list_gallery_posts_default(client, sample_gallery_posts):
    """Test listing gallery posts with default pagination."""
    response = client.get("/api/gallery")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pageSize" in data
    assert "totalPages" in data

    # Should return 3 published posts (excluding future post)
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["pageSize"] == 20
    assert data["totalPages"] == 1

    # Check ordering: featured first, then by display_order
    items = data["items"]
    assert items[0]["isFeatured"] is True
    assert items[0]["displayOrder"] == 1


def test_list_gallery_posts_pagination(client, sample_gallery_posts):
    """Test gallery posts pagination."""
    # Request first page with page_size=2
    response = client.get("/api/gallery?page=1&page_size=2")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["pageSize"] == 2
    assert data["totalPages"] == 2

    # Request second page
    response = client.get("/api/gallery?page=2&page_size=2")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 1
    assert data["page"] == 2
    assert data["pageSize"] == 2


def test_list_gallery_posts_filter_by_media_type(client, sample_gallery_posts):
    """Test filtering gallery posts by media type."""
    # Filter for images only
    response = client.get("/api/gallery?media_type=image")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # 2 published image posts
    assert data["total"] == 2
    assert len(data["items"]) == 2

    for item in data["items"]:
        assert item["mediaType"] == "image"

    # Filter for videos only
    response = client.get("/api/gallery?media_type=video")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # 1 published video post
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["mediaType"] == "video"


def test_list_gallery_posts_filter_by_source_type(client, sample_gallery_posts):
    """Test filtering gallery posts by source type."""
    # Filter for instagram posts
    response = client.get("/api/gallery?source_type=instagram")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # 1 published instagram post (excluding future post)
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["sourceType"] == "instagram"

    # Filter for tiktok posts
    response = client.get("/api/gallery?source_type=tiktok")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["sourceType"] == "tiktok"

    # Filter for original posts
    response = client.get("/api/gallery?source_type=original")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["sourceType"] == "original"


def test_list_gallery_posts_combined_filters(client, sample_gallery_posts):
    """Test combining multiple filters."""
    # Filter for image posts from instagram
    response = client.get("/api/gallery?media_type=image&source_type=instagram")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["mediaType"] == "image"
    assert data["items"][0]["sourceType"] == "instagram"


def test_list_gallery_posts_invalid_media_type(client):
    """Test invalid media_type parameter."""
    response = client.get("/api/gallery?media_type=audio")

    # Should return 422 validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_gallery_posts_invalid_source_type(client):
    """Test invalid source_type parameter."""
    response = client.get("/api/gallery?source_type=facebook")

    # Should return 422 validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_gallery_posts_invalid_page(client):
    """Test invalid page parameter."""
    response = client.get("/api/gallery?page=0")

    # Should return 422 validation error (page must be >= 1)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_gallery_posts_invalid_page_size(client):
    """Test invalid page_size parameter."""
    # page_size too large
    response = client.get("/api/gallery?page_size=101")

    # Should return 422 validation error (page_size must be <= 100)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_gallery_posts_empty_results(client, db_session):
    """Test listing gallery posts when none exist."""
    response = client.get("/api/gallery")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["page"] == 1
    assert data["totalPages"] == 0


def test_list_gallery_posts_excludes_future_posts(client, sample_gallery_posts):
    """Test that future posts are not included in results."""
    response = client.get("/api/gallery")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # Should only have 3 posts (excluding the future one)
    assert data["total"] == 3

    # Verify none of the returned posts are the future post
    for item in data["items"]:
        assert item["caption"] != "Future post"


def test_gallery_post_response_schema(client, sample_gallery_posts):
    """Test that gallery post response has all required fields."""
    response = client.get("/api/gallery")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["items"]) > 0

    # Check first item has all required fields
    item = data["items"][0]
    assert "id" in item
    assert "mediaType" in item
    assert "mediaUrl" in item
    assert "thumbnailUrl" in item
    assert "caption" in item
    assert "tags" in item
    assert "sourceType" in item
    assert "isFeatured" in item
    assert "displayOrder" in item
    assert "publishedAt" in item

    # Verify data types
    assert isinstance(item["mediaType"], str)
    assert isinstance(item["mediaUrl"], str)
    assert isinstance(item["isFeatured"], bool)
    assert isinstance(item["displayOrder"], int)
    assert isinstance(item["tags"], list)


def test_gallery_posts_ordering(client, db_session):
    """Test that gallery posts are ordered correctly."""
    now = datetime.utcnow()

    # Create posts with different ordering attributes
    posts = [
        GalleryPost(
            media_type="image",
            media_url="https://example.com/a.jpg",
            caption="Not featured, order 2",
            source_type="original",
            is_featured=False,
            display_order=2,
            published_at=now - timedelta(days=1),
        ),
        GalleryPost(
            media_type="image",
            media_url="https://example.com/b.jpg",
            caption="Featured, order 1",
            source_type="original",
            is_featured=True,
            display_order=1,
            published_at=now - timedelta(days=3),
        ),
        GalleryPost(
            media_type="image",
            media_url="https://example.com/c.jpg",
            caption="Not featured, order 1",
            source_type="original",
            is_featured=False,
            display_order=1,
            published_at=now - timedelta(days=2),
        ),
    ]

    for post in posts:
        db_session.add(post)
    db_session.commit()

    response = client.get("/api/gallery")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    items = data["items"]

    # Order should be:
    # 1. Featured first (is_featured=True)
    # 2. Then by display_order (ascending)
    # 3. Then by published_at (descending)

    # First item should be featured
    assert items[0]["isFeatured"] is True
    assert items[0]["caption"] == "Featured, order 1"

    # Second item should have display_order=1 and not featured
    assert items[1]["isFeatured"] is False
    assert items[1]["displayOrder"] == 1
    assert items[1]["caption"] == "Not featured, order 1"

    # Third item should have display_order=2
    assert items[2]["displayOrder"] == 2
    assert items[2]["caption"] == "Not featured, order 2"
