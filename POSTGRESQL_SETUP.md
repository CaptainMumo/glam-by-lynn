# PostgreSQL Setup for Glam by Lynn

This project requires PostgreSQL because the database models use PostgreSQL-specific features:
- ARRAY data type for tags
- JSONB for structured data
- GIN indexes for array/text search
- Partial/conditional indexes

**SQLite is not supported** due to these PostgreSQL-specific features.

## Quick Setup (Recommended)

Run the automated setup script:

```bash
cd backend
./setup_postgres.sh
```

This will create:
- PostgreSQL user: `glam_user`
- Development database: `glam_by_lynn`
- Test database: `glam_by_lynn_test`

## Manual Setup

If you prefer manual setup or need different credentials:

### 1. Create PostgreSQL User

```bash
sudo -u postgres psql
```

```sql
CREATE USER glam_user WITH PASSWORD 'your_secure_password';
ALTER USER glam_user CREATEDB;
```

### 2. Create Databases

```sql
CREATE DATABASE glam_by_lynn OWNER glam_user;
CREATE DATABASE glam_by_lynn_test OWNER glam_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE glam_by_lynn TO glam_user;
GRANT ALL PRIVILEGES ON DATABASE glam_by_lynn_test TO glam_user;
```

### 3. Configure Environment

Create `backend/.env` file:

```env
# Database
DATABASE_URL=postgresql://glam_user:your_secure_password@localhost:5432/glam_by_lynn

# For tests (optional, falls back to DATABASE_URL)
TEST_DATABASE_URL=postgresql://glam_user:your_secure_password@localhost:5432/glam_by_lynn_test

# App config
APP_NAME="Glam by Lynn"
APP_VERSION="1.0.0"
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-min-32-characters-long
HOST=0.0.0.0
PORT=8000

# Frontend
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=["http://localhost:3000"]

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=
```

### 4. Run Migrations

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head
```

### 5. Verify Setup

```bash
# Test database connection
python -c "from app.core.database import engine; print('✓ Connected to:', engine.url)"

# Run tests
pytest --no-cov  # Quick test without coverage
pytest           # Full test with coverage
```

## Connection String Format

```
postgresql://username:password@host:port/database_name
```

Example:
```
postgresql://glam_user:glam_password_dev@localhost:5432/glam_by_lynn
```

## Troubleshooting

### "role does not exist"
Create the PostgreSQL user first (see step 1 above).

### "database does not exist"
Create the databases (see step 2 above).

### "password authentication failed"
Check your password in the connection string matches the user's password.

### "peer authentication failed"
You're trying to connect via Unix socket. Use `localhost` in the connection string for TCP/IP authentication:
```
postgresql://user:pass@localhost:5432/db  # TCP/IP ✓
postgresql:///db                            # Unix socket (requires peer auth)
```

### Tests fail with ARRAY errors
You're using SQLite instead of PostgreSQL. Update `DATABASE_URL` in `.env`.

## Security Notes

- **Never commit `.env` files** - They contain sensitive credentials
- Use strong, unique passwords for production
- Restrict database access by IP in production
- Use environment-specific credentials (dev, test, prod)
