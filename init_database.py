"""
Manual database initialization script.
Run this to seed database with extensive data.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.db import init_db, get_db_session
from seed_data import seed_extensive_data


def main():
    """Initialize database with extensive data."""
    print("=" * 50)
    print("Database Initialization Tool")
    print("=" * 50)

    # Initialize database tables
    init_db()
    print("✓ Database tables created")

    # Get session
    db = get_db_session()

    try:
        # Seed with extensive data
        items_count, promos_count = seed_extensive_data(db)

        print(f"✓ Added {items_count} products")
        print(f"✓ Added {promos_count} promo codes")
        print("✓ Database seeded successfully!")

    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()

    finally:
        db.close()

    print("=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()