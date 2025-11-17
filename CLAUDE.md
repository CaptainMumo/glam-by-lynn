# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Glam by Lynn** is an enterprise web application for a makeup artist and beauty business in Kenya. It combines makeup service booking, e-commerce for beauty products, and a 2026 vision showcase for future expansion (salon/spa/barbershop).

**Brand Identity:**
- Business locations: Nairobi and Kitui, Kenya
- Brand colors: Black and Light Pink
- Visual branding: "Glam by" in white/foreground, "Lynn" in pink/secondary

## Development Commands

### Backend (FastAPI)
```bash
# From /backend directory

# Start development server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Install dependencies
pip install -r requirements.txt

# Database migrations
alembic upgrade head                    # Run migrations
alembic revision --autogenerate -m "description"  # Create migration
alembic current                         # Show current migration
alembic downgrade -1                    # Rollback one migration

# Testing
pytest                                  # Run all tests
pytest --cov=app tests/                # Run with coverage
pytest tests/test_auth.py              # Run specific test file
pytest -v                              # Verbose output
```

### Frontend (Next.js)
```bash
# From /frontend directory

# Start development server
npm run dev                            # Start on port 3000

# Install dependencies
npm install

# Code quality
npm run lint                           # Run ESLint
npm run lint:fix                       # Auto-fix linting issues
npm run format                         # Format with Prettier
npm run format:check                   # Check formatting
npm run type-check                     # TypeScript type checking

# Build and production
npm run build                          # Build for production
npm start                              # Start production server

# Add shadcn/ui components
npx shadcn@latest add <component-name> # Install UI component
```

## Architecture & Key Patterns

### Authentication Flow

The app uses a **dual-authentication architecture** combining NextAuth.js (frontend) with FastAPI backend validation:

1. **Frontend (NextAuth.js)**:
   - Google OAuth provider configured in `frontend/src/lib/auth.ts`
   - Custom sign-in page at `/auth/signin`
   - JWT-based sessions (30-day expiry)

2. **Backend Integration**:
   - On Google sign-in, frontend calls `POST /api/auth/google-login` on FastAPI backend
   - Backend creates/retrieves user and returns user data with admin flags
   - User data stored in JWT token and session

3. **Admin Roles**:
   - Five role types: `super_admin`, `product_manager`, `booking_manager`, `content_editor`, `artist`
   - Check roles using `useAuth()`, `isAdmin()`, `hasAdminRole()`, `isSuperAdmin()` helpers
   - Admin status refreshed from backend every hour via JWT callback

### Database & ORM

**Backend uses SQLAlchemy 2.0 with Alembic migrations:**

- **Session management**: Use FastAPI's dependency injection with `get_db()` from `app/core/database.py`
- **Base model**: Import from `app.core.database.Base`
- **Models location**: `app/models/`
- **Connection pooling**: Pre-configured with pool_pre_ping, 10 connections, 20 max overflow
- **Migration workflow**: Always use Alembic for schema changes (never `Base.metadata.create_all()` in production)

Example dependency usage:
```python
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Frontend Architecture

**Next.js App Router with TypeScript:**

- **Pages**: Located in `frontend/src/app/` following App Router conventions
- **API Routes**: NextAuth handler at `/api/auth/[...nextauth]/route.ts`
- **Components**: Organized in `frontend/src/components/`
  - UI primitives from shadcn/ui in `components/ui/`
  - Layout components: `Header.tsx`, `Footer.tsx`
- **Hooks**: Custom hooks in `frontend/src/hooks/`
  - `useAuth()` - Primary authentication hook
  - `useRequireAuth()`, `useRequireAdmin()` - Protected route helpers
- **Config**: API endpoints and configuration in `frontend/src/config/`
- **Types**: TypeScript type definitions in `frontend/src/types/`

### API Communication

**Frontend to Backend:**

- Base URL from `NEXT_PUBLIC_API_URL` environment variable
- Axios configured with centralized API endpoints in `frontend/src/config/api.ts`
- Endpoints follow pattern: `API_ENDPOINTS.{RESOURCE}.{ACTION}`
- Backend CORS configured to allow frontend origin from `settings.ALLOWED_ORIGINS`

### Styling & UI

**Tailwind CSS 4 with shadcn/ui components:**

- Custom theme using OKLCH color space
- CSS variables defined in `frontend/src/app/globals.css`
- Color palette:
  - `--background`, `--foreground` (black/white)
  - `--secondary` (light pink - main brand accent)
  - `--muted`, `--border`, etc.
- Component pattern: Use `cn()` utility from `lib/utils.ts` to merge Tailwind classes
- Import UI components from `@/components/ui/*`

## Project Structure Notes

### Backend Layout
```
backend/app/
├── api/routes/          # API endpoint handlers (commented out in main.py)
├── core/                # Config, database, security
│   ├── config.py       # Settings from environment
│   └── database.py     # SQLAlchemy setup
├── models/              # SQLAlchemy ORM models
├── routers/             # FastAPI routers (auth.router currently active)
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
└── tests/               # Pytest test files
```

### Frontend Layout
```
frontend/src/
├── app/                 # Next.js pages (App Router)
│   ├── page.tsx        # Homepage
│   ├── services/       # Services catalog
│   ├── products/       # Product catalog
│   ├── gallery/        # Portfolio gallery
│   ├── about/          # About page
│   ├── contact/        # Contact page
│   ├── faq/            # FAQ page
│   ├── privacy/        # Privacy policy
│   ├── terms/          # Terms of service
│   └── api/auth/       # NextAuth API route
├── components/
│   ├── Header.tsx      # Main navigation with auth actions
│   ├── Footer.tsx      # Footer with 4-column grid links
│   └── ui/             # shadcn/ui primitives
├── config/             # API configuration
├── hooks/              # React hooks (useAuth, etc.)
├── lib/                # Utilities (auth.ts, utils.ts)
└── types/              # TypeScript definitions
```

## Environment Configuration

### Backend (.env)
Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret
- `FRONTEND_URL` - Frontend URL for CORS

### Frontend (.env.local)
Required variables:
- `NEXT_PUBLIC_API_URL` - Backend API base URL (public, client-accessible)
- `NEXTAUTH_URL` - Frontend URL for NextAuth
- `NEXTAUTH_SECRET` - NextAuth session encryption key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret

**Important**: Both frontend and backend need the same Google OAuth credentials.

## Development Workflow

1. **Issue-based development**: Work on features from [GitHub Issues](https://github.com/CaptainMumo/glam-by-lynn/issues)
2. **Branch naming**: `feature/issue-{number}-{short-description}`
3. **Commit convention**: Follow [Conventional Commits](https://www.conventionalcommits.org/)
   - `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`
4. **Testing required**: Backend uses pytest, ensure tests pass before PR
5. **Migration workflow**: Use Alembic for all database schema changes

## Running the Full Stack

Both servers must run simultaneously for full functionality:

```bash
# Terminal 1 - Backend
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Access points:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs (dev only): http://localhost:8000/docs

## Important Implementation Details

### Admin System
- Admin flags (`isAdmin`, `adminRole`) stored in backend database
- Frontend JWT token includes admin data from backend response
- Token refreshes admin status from backend every 60 minutes
- Use `useAuth()` hook to access current user's admin status
- Admin navigation link in Header only visible when `isAdmin === true`

### Database Sessions
- Never create database sessions manually
- Always use FastAPI's `Depends(get_db)` dependency injection
- Sessions auto-close and rollback on errors via context manager

### Component Imports
- Use `@/` alias for absolute imports from `src/` directory
- UI components: `@/components/ui/*`
- Hooks: `@/hooks/*`
- Config: `@/config/*`
- Lib utilities: `@/lib/*`

### Google OAuth Configuration
- NextAuth requires both `signIn` and `jwt` callbacks for proper user data flow
- Backend `/api/auth/google-login` endpoint must return `id`, `isAdmin`, `adminRole`
- Session strategy is JWT (not database sessions)
