"""Create comprehensive sample data for E2E testing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from decimal import Decimal
from app.core.database import get_db
from app.models.service import ServicePackage, TransportLocation
from app.models.product import Brand, Category, Product, ProductImage
from app.models.user import User
from sqlalchemy.orm import Session

def create_brands(db: Session):
    """Create sample brands."""
    print("Creating brands...")
    brands = [
        Brand(
            name="Fenty Beauty",
            slug="fenty-beauty",
            description="Makeup for all. Founded by Rihanna.",
            is_active=True
        ),
        Brand(
            name="MAC Cosmetics",
            slug="mac-cosmetics",
            description="Professional makeup and beauty products.",
            is_active=True
        ),
        Brand(
            name="NYX Professional Makeup",
            slug="nyx-professional-makeup",
            description="Affordable professional makeup.",
            is_active=True
        ),
        Brand(
            name="Maybelline",
            slug="maybelline",
            description="Maybe she's born with it. Maybe it's Maybelline.",
            is_active=True
        ),
        Brand(
            name="L'Oréal Paris",
            slug="loreal-paris",
            description="Because you're worth it.",
            is_active=True
        ),
    ]

    for brand in brands:
        db.add(brand)

    db.flush()
    print(f"✓ Created {len(brands)} brands")
    return brands

def create_categories(db: Session):
    """Create sample categories."""
    print("Creating categories...")
    categories = [
        Category(
            name="Foundation & Concealer",
            slug="foundation-concealer",
            description="Base makeup products for flawless skin",
            is_active=True,
            display_order=1
        ),
        Category(
            name="Lipstick & Lip Gloss",
            slug="lipstick-lip-gloss",
            description="Lip colors and treatments",
            is_active=True,
            display_order=2
        ),
        Category(
            name="Eyeshadow",
            slug="eyeshadow",
            description="Eye makeup palettes and singles",
            is_active=True,
            display_order=3
        ),
        Category(
            name="Mascara & Eyeliner",
            slug="mascara-eyeliner",
            description="Eye definition products",
            is_active=True,
            display_order=4
        ),
        Category(
            name="Brushes & Tools",
            slug="brushes-tools",
            description="Makeup application tools",
            is_active=True,
            display_order=5
        ),
        Category(
            name="Skincare",
            slug="skincare",
            description="Skincare products and treatments",
            is_active=True,
            display_order=6
        ),
    ]

    for category in categories:
        db.add(category)

    db.flush()
    print(f"✓ Created {len(categories)} categories")
    return categories

def create_products(db: Session, brands, categories):
    """Create sample products."""
    print("Creating products...")

    # Helper to find brand/category by name
    brand_map = {b.name: b for b in brands}
    cat_map = {c.name: c for c in categories}

    products = [
        # Foundation products
        Product(
            title="Fenty Beauty Pro Filt'r Soft Matte Foundation",
            slug="fenty-pro-filtr-foundation",
            description="Award-winning soft matte foundation with buildable, medium to full coverage. Available in 50 shades.",
            brand_id=brand_map["Fenty Beauty"].id,
            category_id=cat_map["Foundation & Concealer"].id,
            base_price=Decimal("3800.00"),
            sku="FTY-FOUND-001",
            inventory_count=45,
            is_active=True,
            is_featured=True,
            tags=["foundation", "matte", "full-coverage", "long-wearing"]
        ),
        Product(
            title="MAC Studio Fix Fluid Foundation SPF 15",
            slug="mac-studio-fix-foundation",
            description="Medium to full coverage foundation with a natural matte finish. Oil-free formula.",
            brand_id=brand_map["MAC Cosmetics"].id,
            category_id=cat_map["Foundation & Concealer"].id,
            base_price=Decimal("4200.00"),
            sku="MAC-FOUND-001",
            inventory_count=30,
            is_active=True,
            is_featured=True,
            tags=["foundation", "matte", "spf", "oil-free"]
        ),
        Product(
            title="Maybelline Fit Me Matte + Poreless Foundation",
            slug="maybelline-fit-me-foundation",
            description="Mattifying foundation that fits skin's tone and texture. Refines pores and controls shine.",
            brand_id=brand_map["Maybelline"].id,
            category_id=cat_map["Foundation & Concealer"].id,
            base_price=Decimal("1500.00"),
            sku="MAY-FOUND-001",
            inventory_count=60,
            is_active=True,
            is_featured=False,
            tags=["foundation", "matte", "pore-minimizing", "affordable"]
        ),

        # Lipstick products
        Product(
            title="MAC Retro Matte Lipstick - Ruby Woo",
            slug="mac-ruby-woo-lipstick",
            description="Iconic blue-red matte lipstick. Vivid, intense color with a matte finish.",
            brand_id=brand_map["MAC Cosmetics"].id,
            category_id=cat_map["Lipstick & Lip Gloss"].id,
            base_price=Decimal("2800.00"),
            sku="MAC-LIP-001",
            inventory_count=40,
            is_active=True,
            is_featured=True,
            tags=["lipstick", "matte", "red", "classic"]
        ),
        Product(
            title="Fenty Beauty Stunna Lip Paint",
            slug="fenty-stunna-lip-paint",
            description="Longwear fluid lip color with a soft matte finish. Highly pigmented and comfortable.",
            brand_id=brand_map["Fenty Beauty"].id,
            category_id=cat_map["Lipstick & Lip Gloss"].id,
            base_price=Decimal("2600.00"),
            discount_type="percentage",
            discount_value=Decimal("10.00"),
            sku="FTY-LIP-001",
            inventory_count=35,
            is_active=True,
            is_featured=False,
            tags=["lipstick", "liquid", "long-wear", "matte"]
        ),
        Product(
            title="NYX Butter Gloss",
            slug="nyx-butter-gloss",
            description="Creamy lip gloss with a buttery soft texture and high shine finish.",
            brand_id=brand_map["NYX Professional Makeup"].id,
            category_id=cat_map["Lipstick & Lip Gloss"].id,
            base_price=Decimal("800.00"),
            sku="NYX-LIP-001",
            inventory_count=80,
            is_active=True,
            is_featured=False,
            tags=["lip-gloss", "shine", "moisturizing", "affordable"]
        ),

        # Eyeshadow products
        Product(
            title="NYX Ultimate Shadow Palette - Brights",
            slug="nyx-ultimate-brights-palette",
            description="16 vibrant eyeshadow shades in matte and shimmer finishes. Bold and colorful.",
            brand_id=brand_map["NYX Professional Makeup"].id,
            category_id=cat_map["Eyeshadow"].id,
            base_price=Decimal("1800.00"),
            sku="NYX-EYE-001",
            inventory_count=25,
            is_active=True,
            is_featured=True,
            tags=["eyeshadow", "palette", "colorful", "shimmer", "matte"]
        ),
        Product(
            title="MAC Eye Shadow - Satin Taupe",
            slug="mac-satin-taupe-eyeshadow",
            description="Neutral taupe eyeshadow with a satin finish. Perfect for everyday looks.",
            brand_id=brand_map["MAC Cosmetics"].id,
            category_id=cat_map["Eyeshadow"].id,
            base_price=Decimal("2200.00"),
            sku="MAC-EYE-001",
            inventory_count=50,
            is_active=True,
            is_featured=False,
            tags=["eyeshadow", "single", "neutral", "satin"]
        ),

        # Mascara products
        Product(
            title="Maybelline Sky High Mascara",
            slug="maybelline-sky-high-mascara",
            description="Volumizing and lengthening mascara with a flexible brush for sky-high lashes.",
            brand_id=brand_map["Maybelline"].id,
            category_id=cat_map["Mascara & Eyeliner"].id,
            base_price=Decimal("1200.00"),
            sku="MAY-MAS-001",
            inventory_count=70,
            is_active=True,
            is_featured=True,
            tags=["mascara", "volumizing", "lengthening"]
        ),
        Product(
            title="L'Oréal Paris Paradise Extatic Mascara",
            slug="loreal-paradise-mascara",
            description="Soft bristle brush delivers spectacular volume and length. Smooth application.",
            brand_id=brand_map["L'Oréal Paris"].id,
            category_id=cat_map["Mascara & Eyeliner"].id,
            base_price=Decimal("1400.00"),
            discount_type="fixed",
            discount_value=Decimal("200.00"),
            sku="LOR-MAS-001",
            inventory_count=55,
            is_active=True,
            is_featured=False,
            tags=["mascara", "volumizing", "soft-brush"]
        ),

        # Brushes & Tools
        Product(
            title="Professional Makeup Brush Set - 12 Pieces",
            slug="professional-brush-set-12",
            description="Complete set of 12 professional makeup brushes for face and eyes. Soft synthetic bristles.",
            brand_id=brand_map["NYX Professional Makeup"].id,
            category_id=cat_map["Brushes & Tools"].id,
            base_price=Decimal("3500.00"),
            sku="NYX-TOOL-001",
            inventory_count=20,
            is_active=True,
            is_featured=True,
            tags=["brushes", "tools", "set", "professional"]
        ),
        Product(
            title="Beauty Blender - Original Pink",
            slug="beauty-blender-pink",
            description="The original makeup sponge for flawless foundation application. Edgeless design.",
            brand_id=brand_map["Fenty Beauty"].id,
            category_id=cat_map["Brushes & Tools"].id,
            base_price=Decimal("2200.00"),
            sku="FTY-TOOL-001",
            inventory_count=40,
            is_active=True,
            is_featured=False,
            tags=["sponge", "blender", "foundation", "tool"]
        ),
    ]

    for product in products:
        db.add(product)

    db.flush()
    print(f"✓ Created {len(products)} products")
    return products

def create_product_images(db: Session, products):
    """Create sample product images."""
    print("Creating product images...")

    # Add primary images for each product
    images = []
    for i, product in enumerate(products):
        image = ProductImage(
            product_id=product.id,
            image_url=f"https://via.placeholder.com/500x500/FFB6C1/000000?text={product.title[:20]}",
            alt_text=product.title,
            is_primary=True,
            display_order=0
        )
        images.append(image)
        db.add(image)

    db.flush()
    print(f"✓ Created {len(images)} product images")
    return images

def create_service_packages(db: Session):
    """Create sample service packages."""
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

    db.flush()
    print(f"✓ Created {len(packages)} service packages")
    return packages

def create_transport_locations(db: Session):
    """Create sample transport locations."""
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

    db.flush()
    print(f"✓ Created {len(locations)} transport locations")
    return locations

def seed_database():
    """Main function to seed the database with sample data."""
    print("\n" + "="*60)
    print("  GLAM BY LYNN - DATABASE SEEDING")
    print("="*60 + "\n")

    db = next(get_db())

    try:
        # Create all sample data
        brands = create_brands(db)
        categories = create_categories(db)
        products = create_products(db, brands, categories)
        images = create_product_images(db, products)
        packages = create_service_packages(db)
        locations = create_transport_locations(db)

        # Commit all changes
        db.commit()

        print("\n" + "="*60)
        print("  ✓ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nSummary:")
        print(f"  • {len(brands)} brands")
        print(f"  • {len(categories)} categories")
        print(f"  • {len(products)} products")
        print(f"  • {len(images)} product images")
        print(f"  • {len(packages)} service packages")
        print(f"  • {len(locations)} transport locations")
        print("\nYou can now run E2E tests with real data!\n")

    except Exception as e:
        print(f"\n✗ ERROR SEEDING DATABASE: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
