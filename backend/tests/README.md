# Backend API Tests

## Prerequisites

The tests require a PostgreSQL database because the application models use PostgreSQL-specific features (ARRAY, JSONB, GIN indexes, partial indexes).

### Setting up Test Database

1. **Install PostgreSQL** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib

   # MacOS
   brew install postgresql
   ```

2. **Create test database**:
   ```bash
   # Start PostgreSQL service
   sudo service postgresql start  # Linux
   brew services start postgresql  # MacOS

   # Create test database
   createdb glam_by_lynn_test
   ```

3. **Set environment variable** (optional):
   ```bash
   export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/glam_by_lynn_test"
   ```

   Or create a `.env.test` file:
   ```
   TEST_DATABASE_URL=postgresql://username:password@localhost:5432/glam_by_lynn_test
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_brands.py

# Run with coverage report
pytest --cov=app --cov-report=html

# Run without coverage (faster)
pytest --no-cov
```

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `test_*.py` - Test files for each API module

## Coverage Requirements

Minimum coverage threshold: **70%** for:
- Branch coverage
- Function coverage
- Line coverage
- Statement coverage

## Note

If you encounter `ARRAY` type errors, ensure you're using PostgreSQL for tests, not SQLite.
The models are specifically designed for PostgreSQL and cannot run on SQLite.
