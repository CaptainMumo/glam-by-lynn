# Database Migrations Guide

## Overview

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations. Alembic provides a way to manage database schema changes in a systematic and version-controlled manner.

## Setup

Alembic is already configured in the `backend/` directory. The configuration automatically uses the database URL from your environment variables.

## Migration Workflow

### 1. Creating a New Migration

When you add or modify database models, create a new migration:

```bash
cd backend
source venv/bin/activate

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Example:
alembic revision --autogenerate -m "Add users table"
```

**Important:** Always review the auto-generated migration file before applying it. Alembic may not detect all changes correctly.

### 2. Applying Migrations

Apply pending migrations to the database:

```bash
# Upgrade to the latest version
alembic upgrade head

# Upgrade by one version
alembic upgrade +1

# Upgrade to a specific version
alembic upgrade <revision_id>
```

### 3. Rolling Back Migrations

Rollback database changes:

```bash
# Downgrade by one version
alembic downgrade -1

# Downgrade to a specific version
alembic downgrade <revision_id>

# Downgrade to base (remove all migrations)
alembic downgrade base
```

### 4. Viewing Migration History

```bash
# Show current migration version
alembic current

# Show all migration history
alembic history

# Show migration history with details
alembic history --verbose
```

## Configuration

### Database URL

The database URL is automatically loaded from your environment variables (`DATABASE_URL` in `.env`).

**Default (Development):**
```
DATABASE_URL=sqlite:///./app.db
```

**Production (PostgreSQL):**
```
DATABASE_URL=postgresql://user:password@localhost:5432/glam_by_lynn
```

### Migration Files Location

Migrations are stored in: `backend/alembic/versions/`

### Configuration Files

- `backend/alembic.ini` - Alembic configuration
- `backend/alembic/env.py` - Migration environment setup
- `backend/alembic/script.py.mako` - Migration template

## Important Notes

### When Creating Models

1. **Import models in env.py:** For Alembic to detect your models, they must be imported in `alembic/env.py`:

```python
# In alembic/env.py
from app.models import user, product, booking, order  # etc.
```

2. **Use SQLAlchemy Base:** All models must inherit from the Base class:

```python
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    # ...
```

### Best Practices

1. **Review Auto-Generated Migrations:**
   - Always review migrations before applying them
   - Alembic may miss some changes (indexes, constraints, etc.)
   - Add any missing changes manually

2. **Test Migrations:**
   - Test upgrade and downgrade on development database
   - Ensure downgrade works correctly
   - Test with production-like data

3. **Descriptive Names:**
   - Use clear, descriptive migration names
   - Example: "add_user_email_verification" not "update_users"

4. **One Change Per Migration:**
   - Keep migrations focused on single logical changes
   - Easier to rollback and debug

5. **Never Edit Applied Migrations:**
   - Once a migration is applied to production, never edit it
   - Create a new migration for corrections

## Common Commands

### Development Workflow

```bash
# 1. Create new model or modify existing one
# 2. Generate migration
alembic revision --autogenerate -m "Add feature X"

# 3. Review migration file in alembic/versions/
# 4. Apply migration
alembic upgrade head

# 5. Test rollback
alembic downgrade -1

# 6. Re-apply
alembic upgrade head
```

### Production Deployment

```bash
# 1. Pull latest code
git pull origin main

# 2. Activate environment
source venv/bin/activate

# 3. Apply migrations
alembic upgrade head

# 4. Restart application
# (deployment specific)
```

## Troubleshooting

### "Can't locate revision identified by 'xxx'"

This means the alembic_version table is out of sync. Options:

```bash
# Check current version
alembic current

# Stamp database with current version
alembic stamp head
```

### "Target database is not up to date"

Your database is behind. Apply pending migrations:

```bash
alembic upgrade head
```

### "Multiple head revisions are present"

You have a branched migration history. Merge them:

```bash
alembic merge -m "Merge migrations" <rev1> <rev2>
```

### Manual Migration Creation

If auto-generation doesn't work:

```bash
# Create empty migration
alembic revision -m "Description"

# Edit the generated file manually
```

## Migration File Structure

```python
"""Description of migration

Revision ID: xxx
Revises: yyy
Create Date: 2025-01-16 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'xxx'
down_revision: Union[str, Sequence[str], None] = 'yyy'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop table
    op.drop_table('users')
```

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Database Schema](./DATABASE_SCHEMA.md)

## Next Steps

After setting up Alembic, proceed to Issue #4 to implement the complete database schema from `DATABASE_SCHEMA.md`.

---

**Last Updated:** 2025-01-16
