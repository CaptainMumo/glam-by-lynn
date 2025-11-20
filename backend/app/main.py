"""
Glam by Lynn - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import check_db_connection
from app.core.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    AuthRateLimitMiddleware,
)

# Import routers
from app.routers import auth, services, bookings, gallery, testimonials, products as public_products, promo_codes as public_promo_codes, reviews as public_reviews, cart, wishlist
from app.api.routes import brands, categories, products, product_images, product_variants, service_packages, orders
from app.api.routes.admin import locations as admin_locations, calendar as admin_calendar, bookings as admin_bookings, gallery as admin_gallery, users as admin_users, testimonials as admin_testimonials, promo_codes as admin_promo_codes, analytics as admin_analytics

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise web application for makeup services and beauty product e-commerce",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting (general)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    requests_per_hour=settings.RATE_LIMIT_PER_MINUTE * 60,
)

# Add stricter rate limiting for auth endpoints
app.add_middleware(AuthRateLimitMiddleware)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Glam by Lynn API is running",
        "version": settings.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health/db", tags=["Health"])
async def database_health_check():
    """
    Database health check endpoint

    Returns:
        JSONResponse: Database connection status
    """
    is_healthy = check_db_connection()
    status_code = 200 if is_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "database": "connected" if is_healthy else "disconnected",
            "status": "healthy" if is_healthy else "unhealthy"
        }
    )


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(services.router, prefix="/api")  # Public services API
app.include_router(bookings.router, prefix="/api")  # Public bookings API
app.include_router(gallery.router, prefix="/api")  # Public gallery API
app.include_router(testimonials.router, prefix="/api")  # Public testimonials API
app.include_router(public_products.router)  # Public products API
app.include_router(public_promo_codes.router, prefix="/api")  # Public promo codes API
app.include_router(public_reviews.router, prefix="/api")  # Public reviews API
app.include_router(cart.router, prefix="/api")  # Shopping cart API
app.include_router(wishlist.router, prefix="/api")  # Wishlist API
app.include_router(brands.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(product_images.router, prefix="/api")
app.include_router(product_variants.router, prefix="/api")
app.include_router(service_packages.router, prefix="/api")  # Admin services API
app.include_router(orders.router, prefix="/api")  # Orders API
app.include_router(admin_locations.router, prefix="/api")  # Admin locations API
app.include_router(admin_calendar.router, prefix="/api")  # Admin calendar API
app.include_router(admin_bookings.router, prefix="/api")  # Admin bookings API
app.include_router(admin_gallery.router, prefix="/api")  # Admin gallery API
app.include_router(admin_testimonials.router, prefix="/api")  # Admin testimonials API
app.include_router(admin_promo_codes.router, prefix="/api")  # Admin promo codes API
app.include_router(admin_analytics.router, prefix="/api")  # Admin analytics API
app.include_router(admin_users.router, prefix="/api")  # Admin users API


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
