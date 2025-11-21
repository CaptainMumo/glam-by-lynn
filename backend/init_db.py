"""Initialize database tables."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base

# Import all models to register them with Base
from app.models.user import User
from app.models.product import Brand, Category, Product, ProductImage, ProductVideo, ProductVariant
from app.models.service import ServicePackage, TransportLocation, CalendarAvailability
from app.models.booking import Booking
from app.models.order import Cart, CartItem, Order, OrderItem, PromoCode, Wishlist
from app.models.content import Review, GalleryPost, Testimonial, VisionRegistration, AdminActivityLog

def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    init_database()
