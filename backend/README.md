# Glam by Lynn - Backend API

FastAPI backend for the Glam by Lynn web application.

## Features

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Powerful ORM for PostgreSQL
- **Alembic** - Database migrations
- **JWT Authentication** - Secure token-based auth
- **Google OAuth** - Social authentication
- **Pytest** - Comprehensive testing
- **Docker** - Containerization support

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip or poetry

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Create database:**
   ```bash
   createdb glam_by_lynn
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

### Running the Server

**Development:**
```bash
uvicorn app.main:app --reload
```

**Production:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**With Docker:**
```bash
# From project root
docker-compose up backend
```

### API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Testing

### Quick Start

**Run all tests:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=app --cov-report=html
```

**Run specific markers:**
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m fixture       # Fixture tests only
```

### Test Fixtures

Comprehensive test fixtures are available for all database models:
- User fixtures (regular users, admin users, guest users)
- Product fixtures (brands, categories, products, variants)
- Service fixtures (packages, locations, availability)
- Booking fixtures (with deposit calculation)
- Order fixtures (orders, carts, promo codes, wishlists)
- Content fixtures (reviews, testimonials, gallery posts)

See [app/tests/README.md](app/tests/README.md) for complete testing documentation.

### PostgreSQL Requirement for Tests

**IMPORTANT**: Tests require PostgreSQL due to schema features (ARRAY, JSONB, UUID).
SQLite is not supported for testing.

Configure test database:
```python
# In app/tests/conftest.py
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/glam_by_lynn_test"
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API route handlers
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings
│   │   ├── database.py      # Database connection
│   │   └── security.py      # Auth utilities
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── db/                  # Database utilities
│   ├── tests/               # Test files
│   │   ├── conftest.py      # Pytest fixtures
│   │   └── test_*.py        # Test modules
│   └── main.py              # FastAPI application
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── pytest.ini               # Pytest configuration
└── .env.example             # Environment variables template
```

## Database Migrations

Alembic is configured to automatically use the database URL from your `.env` file.

**Create a new migration:**
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migration:**
```bash
alembic downgrade -1
```

**View migration history:**
```bash
alembic history
```

**Check current version:**
```bash
alembic current
```

For a comprehensive migration guide, see [../docs/MIGRATIONS.md](../docs/MIGRATIONS.md)

## Code Quality

**Format code:**
```bash
black app/
```

**Lint code:**
```bash
flake8 app/
```

**Type checking:**
```bash
mypy app/
```

## Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `FRONTEND_URL` - Frontend application URL

## Contributing

1. Pick an issue from GitHub
2. Create a feature branch
3. Write tests first (TDD)
4. Implement feature
5. Ensure all tests pass
6. Create Pull Request

## License

Proprietary - All rights reserved by Glam by Lynn
