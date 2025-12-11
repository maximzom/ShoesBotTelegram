"""
Script to check current database contents.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.db import get_db_session
from models.schemas import Item, PromoCode, User, Order


def check_database():
    """Check and display database contents."""
    print("=" * 50)
    print("DATABASE STATUS CHECK")
    print("=" * 50)

    db = get_db_session()

    try:
        # Count items
        item_count = db.query(Item).count()
        print(f"📦 Products in database: {item_count}")

        # List all products
        if item_count > 0:
            print("\n📋 Product list:")
            print("-" * 50)
            for item in db.query(Item).order_by(Item.category, Item.name).all():
                print(f"{item.id:3d} | {item.sku:15s} | {item.name:30s} | {item.price:8.2f} грн | {item.category}")

        # Count promo codes
        promo_count = db.query(PromoCode).count()
        active_promos = db.query(PromoCode).filter(PromoCode.is_active == True).count()
        print(f"\n🎟️  Promo codes: {promo_count} total, {active_promos} active")

        if promo_count > 0:
            print("\n📋 Active promo codes:")
            print("-" * 50)
            from datetime import datetime
            now = datetime.now()
            for promo in db.query(PromoCode).filter(PromoCode.is_active == True).order_by(PromoCode.code).all():
                valid = "✓" if promo.is_valid() else "✗"
                expiry = promo.valid_until.strftime("%d.%m.%Y") if promo.valid_until else "No expiry"
                print(
                    f"{valid} {promo.code:15s} | {promo.discount_percent:4.1f}% | Uses: {promo.usage_count:3d}/{promo.usage_limit or '∞':5s} | Valid until: {expiry}")

        # Count users
        user_count = db.query(User).count()
        print(f"\n👤 Registered users: {user_count}")

        # Count orders
        order_count = db.query(Order).count()
        print(f"\n📦 Total orders: {order_count}")

        if order_count > 0:
            order_stats = db.query(Order.status, db.func.count(Order.status)).group_by(Order.status).all()
            print("   Order status breakdown:")
            for status, count in order_stats:
                print(f"   - {status:15s}: {count}")

        print("\n" + "=" * 50)
        print("Check complete!")

        # Database file info
        from config import Config
        if "sqlite" in Config.DB_URL:
            db_path = Config.DB_URL.replace("sqlite:///", "")
            if os.path.exists(db_path):
                size = os.path.getsize(db_path) / 1024  # KB
                print(f"\n💾 Database file: {db_path}")
                print(f"   Size: {size:.2f} KB")

    except Exception as e:
        print(f"✗ Error checking database: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    check_database()