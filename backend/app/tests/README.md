# Testing Documentation

## Overview

This directory contains comprehensive test fixtures and tests for the Glam by Lynn backend application.

## Test Fixtures

### Available Fixtures

The `conftest.py` file provides comprehensive fixtures for all database models:

#### Base Fixtures
- `db` - Database session for each test
- `client` - FastAPI test client
- `faker` - Faker instance for generating test data

#### User Fixtures
- `create_user` - Factory to create custom users
- `user` - Default regular user
- `admin_user` - Admin user with super_admin role

#### Product Fixtures
- `create_brand` - Factory to create brands
- `brand` - Default brand
- `create_category` - Factory to create categories (with hierarchy support)
- `category` - Default category
- `create_product` - Factory to create products
- `product` - Default product with brand and category

#### Service Fixtures
- `create_service_package` - Factory to create service packages
- `service_package` - Default service package
- `create_transport_location` - Factory to create transport locations
- `transport_location` - Default transport location

#### Booking Fixtures
- `create_booking` - Factory to create bookings (user or guest)
- `booking` - Default booking with all relationships

#### Order Fixtures
- `create_promo_code` - Factory to create promo codes
- `promo_code` - Default promo code
- `create_order` - Factory to create orders (user or guest)
- `order` - Default order
- `create_cart` - Factory to create carts
- `cart` - Default cart

#### Content Fixtures
- `create_review` - Factory to create reviews
- `review` - Default review
- `create_testimonial` - Factory to create testimonials
- `testimonial` - Default testimonial

#### Utility Fixtures
- `sample_uuid` - Generate UUIDs
- `sample_date` - Current date
- `sample_datetime` - Current datetime

## PostgreSQL Requirement

**IMPORTANT**: The database schema uses PostgreSQL-specific features:
- `ARRAY` type for tags columns
- `JSONB` type for admin activity logs
- `UUID` type for primary keys
- GIN indexes for array and JSONB columns

**SQLite is NOT supported for testing**. Tests will fail with SQLite due to unsupported column types.

### Running Tests with PostgreSQL

To run tests with full feature support, configure a PostgreSQL test database:

```python
# In conftest.py, change:
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/glam_by_lynn_test"
```

### Test Database Setup

1. Create PostgreSQL test database:
   ```bash
   createdb glam_by_lynn_test
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Tests automatically create/drop tables for each test function

## Running Tests

### All Tests
```bash
pytest
```

### With Coverage
```bash
pytest --cov=app --cov-report=html
```

### Specific Markers
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Fixture tests only
pytest -m fixture

# Exclude slow tests
pytest -m "not slow"
```

### Specific Test File
```bash
pytest app/tests/test_fixtures.py
```

### Specific Test Class or Function
```bash
pytest app/tests/test_fixtures.py::TestUserFixtures
pytest app/tests/test_fixtures.py::TestUserFixtures::test_create_user_fixture
```

## Test Markers

Available pytest markers:
- `unit` - Unit tests (isolated, no external dependencies)
- `integration` - Integration tests (database, external services)
- `slow` - Slow-running tests
- `fixture` - Tests for pytest fixtures

## Coverage Requirements

- Minimum coverage: 70%
- Coverage reports generated in:
  - Terminal (with missing lines)
  - HTML: `htmlcov/index.html`
  - JSON: `coverage.json`

## Writing Tests

### Using Factory Fixtures

```python
def test_custom_user(create_user):
    """Create a user with custom attributes."""
    user = create_user(
        email="custom@example.com",
        full_name="Custom User",
        is_admin=True,
        admin_role="product_manager"
    )
    assert user.email == "custom@example.com"
    assert user.is_admin is True
```

### Using Default Fixtures

```python
def test_with_defaults(user, product, order):
    """Use pre-configured fixtures."""
    assert user.id is not None
    assert product.brand_id is not None
    assert order.user_id == user.id
```

### Testing Guest Functionality

```python
def test_guest_order(create_order):
    """Test guest checkout."""
    order = create_order(
        guest_email="guest@example.com",
        guest_name="Guest User",
        guest_phone="123456789"
    )
    assert order.user_id is None
    assert order.guest_email == "guest@example.com"
```

## Best Practices

1. **Use Factory Fixtures for Customization**: Use `create_*` fixtures when you need custom attributes
2. **Use Default Fixtures for Speed**: Use default fixtures (`user`, `product`, etc.) for standard scenarios
3. **Isolate Tests**: Each test should be independent and not rely on other tests
4. **Clean Test Data**: Fixtures automatically clean up after each test
5. **Mark Tests Appropriately**: Use pytest markers to categorize tests
6. **Test Edge Cases**: Test validation, constraints, and error conditions
7. **Keep Tests Fast**: Use unit tests where possible, integration tests when necessary

## Future Enhancements

- Add factory_boy for more advanced test data generation
- Add pytest-postgresql for automatic PostgreSQL test database setup
- Add API endpoint integration tests
- Add authentication/authorization tests
- Add performance/load tests
