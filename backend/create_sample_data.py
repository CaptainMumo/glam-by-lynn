"""Create sample data for testing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from decimal import Decimal
from app.core.database import get_db, engine
from app.models.service import ServicePackage, TransportLocation
from app.models.user import User
from sqlalchemy.orm import Session

def create_sample_data():
    """Create sample data for testing."""
    db = next(get_db())

    try:
        # Create service packages
        print("Creating service packages...")
        packages = [
            ServicePackage(
                package_type="bridal_large",
                name="Grand Bridal Package",
                description="Our premium bridal package for large wedding parties. Includes bride, up to 10 bridesmaids, mothers, and additional attendees. Perfect for grand weddings!",
                base_bride_price=Decimal("15000.00"),
                base_maid_price=Decimal("3500.00"),
                base_mother_price=Decimal("4000.00"),
                base_other_price=Decimal("3000.00"),
                min_maids=3,
                max_maids=10,
                includes_facial=True,
                duration_minutes=480,
                is_active=True,
                display_order=1
            ),
            ServicePackage(
                package_type="bridal_small",
                name="Intimate Bridal Package",
                description="Perfect for intimate weddings. Includes bride, up to 3 bridesmaids, and mothers.",
                base_bride_price=Decimal("12000.00"),
                base_maid_price=Decimal("3000.00"),
                base_mother_price=Decimal("3500.00"),
                base_other_price=Decimal("2500.00"),
                min_maids=0,
                max_maids=3,
                includes_facial=True,
                duration_minutes=360,
                is_active=True,
                display_order=2
            ),
            ServicePackage(
                package_type="bride_only",
                name="Bride Only Package",
                description="Exclusive service for the bride. Includes professional makeup and hairstyling with facial treatment.",
                base_bride_price=Decimal("10000.00"),
                base_maid_price=None,
                base_mother_price=None,
                base_other_price=None,
                min_maids=0,
                max_maids=None,
                includes_facial=True,
                duration_minutes=180,
                is_active=True,
                display_order=3
            ),
            ServicePackage(
                package_type="regular",
                name="Special Event Makeup",
                description="Professional makeup for special occasions - parties, photoshoots, corporate events, etc.",
                base_bride_price=Decimal("5000.00"),
                base_maid_price=None,
                base_mother_price=None,
                base_other_price=None,
                min_maids=0,
                max_maids=None,
                includes_facial=False,
                duration_minutes=120,
                is_active=True,
                display_order=4
            ),
            ServicePackage(
                package_type="regular",
                name="Natural Glam Makeup",
                description="Fresh, natural makeup look perfect for daytime events and professional settings.",
                base_bride_price=Decimal("4000.00"),
                base_maid_price=None,
                base_mother_price=None,
                base_other_price=None,
                min_maids=0,
                max_maids=None,
                includes_facial=False,
                duration_minutes=90,
                is_active=True,
                display_order=5
            ),
        ]

        for pkg in packages:
            db.add(pkg)

        # Create transport locations
        print("Creating transport locations...")
        locations = [
            TransportLocation(
                location_name="Nairobi CBD",
                county="Nairobi",
                transport_cost=Decimal("0.00"),
                is_free=True,
                is_active=True
            ),
            TransportLocation(
                location_name="Westlands",
                county="Nairobi",
                transport_cost=Decimal("500.00"),
                is_free=False,
                is_active=True
            ),
            TransportLocation(
                location_name="Karen",
                county="Nairobi",
                transport_cost=Decimal("1000.00"),
                is_free=False,
                is_active=True
            ),
            TransportLocation(
                location_name="Kileleshwa",
                county="Nairobi",
                transport_cost=Decimal("700.00"),
                is_free=False,
                is_active=True
            ),
            TransportLocation(
                location_name="Kitisuru",
                county="Nairobi",
                transport_cost=Decimal("1200.00"),
                is_free=False,
                is_active=True
            ),
            TransportLocation(
                location_name="Kitui Town",
                county="Kitui",
                transport_cost=Decimal("0.00"),
                is_free=True,
                is_active=True
            ),
            TransportLocation(
                location_name="Mwingi",
                county="Kitui",
                transport_cost=Decimal("800.00"),
                is_free=False,
                is_active=True
            ),
        ]

        for location in locations:
            db.add(location)

        # Commit all changes
        db.commit()
        print("✓ Sample data created successfully!")
        print(f"✓ Created {len(packages)} service packages")
        print(f"✓ Created {len(locations)} transport locations")

    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
