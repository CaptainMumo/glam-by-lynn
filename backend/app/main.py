"""
Glam by Lynn - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import check_db_connection

# Import routers
from app.routers import auth
# from app.api.routes import products, services, bookings, orders

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
# app.include_router(products.router, prefix="/api/products", tags=["Products"])
# app.include_router(services.router, prefix="/api/services", tags=["Services"])
# app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])
# app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
