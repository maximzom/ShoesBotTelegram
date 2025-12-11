"""
Database seeding with extensive product data.
"""
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.schemas import Item, PromoCode


def seed_extensive_data(db: Session):
    """Seed database with extensive sample data, avoiding duplicates."""
    print("🌱 Seeding database with extensive data...")

    items_added = 0
    promos_added = 0

    # 1. First, get all existing SKUs and codes
    existing_skus = {item.sku for item in db.query(Item.sku).all()}
    existing_codes = {promo.code for promo in db.query(PromoCode.code).all()}

    # 2. Define extensive shoe items (20+ products)
    items_to_add = [
        # Men's shoes
        {
            'sku': 'NIKE-AIR-001',
            'name': 'Nike Air Max 270',
            'description': 'Легкі та зручні кросівки Nike Air Max 270 з інноваційною технологією амортизації.',
            'price': 2499.00,
            'sizes': ["38", "39", "40", "41", "42", "43"],
            'category': 'men'
        },
        {
            'sku': 'ADIDAS-UB-002',
            'name': 'Adidas Ultraboost 22',
            'description': 'Преміальні бігові кросівки з революційною підошвою Boost.',
            'price': 3299.00,
            'sizes': ["39", "40", "41", "42", "43", "44"],
            'category': 'men'
        },
        {
            'sku': 'NIKE-AF-003',
            'name': 'Nike Air Force 1',
            'description': 'Культові кросівки Nike Air Force 1 у білому кольорі.',
            'price': 2899.00,
            'sizes': ["38", "39", "40", "41", "42", "43", "44"],
            'category': 'men'
        },
        {
            'sku': 'ADIDAS-ST-004',
            'name': 'Adidas Stan Smith',
            'description': 'Класичні кросівки Adidas Stan Smith з натуральної шкіри.',
            'price': 2199.00,
            'sizes': ["38", "39", "40", "41", "42"],
            'category': 'men'
        },
        {
            'sku': 'PUMA-RS-005',
            'name': 'Puma RS-X',
            'description': 'Ретро-кросівки Puma RS-X з яскравим дизайном.',
            'price': 2399.00,
            'sizes': ["39", "40", "41", "42", "43"],
            'category': 'men'
        },
        {
            'sku': 'NEW-BALANCE-006',
            'name': 'New Balance 574',
            'description': 'Класичні кросівки New Balance 574 з підвищеною зручністю.',
            'price': 1999.00,
            'sizes': ["38", "39", "40", "41", "42", "43"],
            'category': 'men'
        },
        {
            'sku': 'REEBOK-CLASSIC-007',
            'name': 'Reebok Classic Leather',
            'description': 'Класичні шкіряні кросівки Reebok.',
            'price': 1899.00,
            'sizes': ["39", "40", "41", "42", "43"],
            'category': 'men'
        },
        {
            'sku': 'NIKE-JORDAN-008',
            'name': 'Nike Air Jordan 1',
            'description': 'Культові баскетбольні кросівки Air Jordan 1.',
            'price': 4599.00,
            'sizes': ["40", "41", "42", "43", "44"],
            'category': 'men'
        },
        # Women's shoes
        {
            'sku': 'PUMA-CALI-101',
            'name': 'Puma Cali Sport Жіночі',
            'description': 'Стильні жіночі кросівки Puma Cali Sport у класичному білому кольорі.',
            'price': 1899.00,
            'sizes': ["35", "36", "37", "38", "39", "40"],
            'category': 'women'
        },
        {
            'sku': 'NIKE-AIR-MAX-102',
            'name': 'Nike Air Max Excee Жіночі',
            'description': 'Жіночі кросівки Nike Air Max Excee з модернізованим дизайном.',
            'price': 2699.00,
            'sizes': ["36", "37", "38", "39", "40"],
            'category': 'women'
        },
        {
            'sku': 'ADIDAS-SU-103',
            'name': 'Adidas Superstar Жіночі',
            'description': 'Культові жіночі кросівки Adidas Superstar.',
            'price': 2299.00,
            'sizes': ["35", "36", "37", "38", "39"],
            'category': 'women'
        },
        {
            'sku': 'CONVERSE-104',
            'name': 'Converse Chuck Taylor All Star',
            'description': 'Класичні кеди Converse Chuck Taylor All Star.',
            'price': 1499.00,
            'sizes': ["36", "37", "38", "39", "40"],
            'category': 'women'
        },
        {
            'sku': 'VANS-105',
            'name': 'Vans Old Skool',
            'description': 'Культові кеди Vans Old Skool з класичним дизайном.',
            'price': 1799.00,
            'sizes': ["36", "37", "38", "39", "40"],
            'category': 'women'
        },
        {
            'sku': 'SKECHERS-106',
            'name': 'Skechers D\'Lites',
            'description': 'Зручні жіночі кросівки Skechers з підвищеною амортизацією.',
            'price': 1599.00,
            'sizes': ["35", "36", "37", "38", "39", "40"],
            'category': 'women'
        },
        # Kids shoes
        {
            'sku': 'NIKE-KIDS-201',
            'name': 'Nike Kids Revolution 6',
            'description': 'Дитячі бігові кросівки Nike Revolution 6.',
            'price': 1299.00,
            'sizes': ["28", "29", "30", "31", "32"],
            'category': 'kids'
        },
        {
            'sku': 'ADIDAS-KIDS-202',
            'name': 'Adidas Kids Grand Court',
            'description': 'Дитячі кросівки Adidas Grand Court для щоденного носіння.',
            'price': 1399.00,
            'sizes': ["27", "28", "29", "30", "31"],
            'category': 'kids'
        },
        {
            'sku': 'PUMA-KIDS-203',
            'name': 'Puma Kids Mirage Sport',
            'description': 'Дитячі спортивні кросівки Puma Mirage Sport.',
            'price': 1199.00,
            'sizes': ["26", "27", "28", "29", "30"],
            'category': 'kids'
        },
        {
            'sku': 'NIKE-KIDS-204',
            'name': 'Nike Kids Flex Runner',
            'description': 'Легкі дитячі кросівки для активного відпочинку.',
            'price': 999.00,
            'sizes': ["25", "26", "27", "28", "29"],
            'category': 'kids'
        },
        # Sport shoes
        {
            'sku': 'NIKE-RUN-301',
            'name': 'Nike Pegasus 39',
            'description': 'Бігові кросівки Nike Pegasus 39 для тренувань.',
            'price': 3199.00,
            'sizes': ["39", "40", "41", "42", "43"],
            'category': 'men'
        },
        {
            'sku': 'ASICS-GEL-302',
            'name': 'Asics Gel-Kayano 29',
            'description': 'Професійні бігові кросівки Asics Gel-Kayano 29.',
            'price': 4499.00,
            'sizes': ["39", "40", "41", "42", "43", "44"],
            'category': 'men'
        },
        # Winter shoes
        {
            'sku': 'TIMBERLAND-401',
            'name': 'Timberland Premium Boots',
            'description': 'Чоботи Timberland Premium для холодної погоди.',
            'price': 5899.00,
            'sizes': ["39", "40", "41", "42", "43"],
            'category': 'men'
        },
        {
            'sku': 'DR-MARTENS-402',
            'name': 'Dr. Martens 1460',
            'description': 'Культові черевики Dr. Martens 1460.',
            'price': 4999.00,
            'sizes': ["38", "39", "40", "41", "42"],
            'category': 'men'
        },
        # Slippers
        {
            'sku': 'CROCS-501',
            'name': 'Crocs Classic Clog',
            'description': 'Класичні крокси Crocs для щоденного носіння.',
            'price': 899.00,
            'sizes': ["38", "39", "40", "41", "42", "43"],
            'category': 'men'
        },
        # Running shoes
        {
            'sku': 'BROOKS-GHOST-601',
            'name': 'Brooks Ghost 14',
            'description': 'Бігові кросівки Brooks Ghost 14 з нейтральною пронацією.',
            'price': 3799.00,
            'sizes': ["39", "40", "41", "42", "43", "44"],
            'category': 'men'
        },
        {
            'sku': 'HOKA-602',
            'name': 'Hoka One One Clifton 8',
            'description': 'Ультралегкі бігові кросівки Hoka Clifton 8.',
            'price': 4199.00,
            'sizes': ["39", "40", "41", "42", "43"],
            'category': 'men'
        },
    ]

    # 3. Add items only if they don't exist
    for item_data in items_to_add:
        if item_data['sku'] in existing_skus:
            print(f"⚠️  Item {item_data['sku']} already exists, skipping...")
            continue

        item = Item(
            sku=item_data['sku'],
            name=item_data['name'],
            description=item_data['description'],
            price=item_data['price'],
            sizes=json.dumps(item_data['sizes']),
            images=json.dumps([]),
            category=item_data['category']
        )

        db.add(item)
        items_added += 1
        print(f"✓ Added item: {item_data['name']} ({item_data['sku']})")

    # 4. Define promo codes
    promos_to_add = [
        {
            'code': 'WELCOME10',
            'discount_percent': 10.0,
            'valid_until': datetime.now() + timedelta(days=30),
            'usage_limit': 100,
            'is_active': True
        },
        {
            'code': 'SUMMER25',
            'discount_percent': 25.0,
            'valid_until': datetime.now() + timedelta(days=60),
            'usage_limit': 50,
            'is_active': True
        },
        {
            'code': 'FIRSTORDER',
            'discount_percent': 15.0,
            'valid_until': datetime.now() + timedelta(days=90),
            'usage_limit': None,
            'is_active': True
        },
        {
            'code': 'NEWYEAR2024',
            'discount_percent': 20.0,
            'valid_until': datetime.now() + timedelta(days=45),
            'usage_limit': 200,
            'is_active': True
        },
        {
            'code': 'BLACKFRIDAY',
            'discount_percent': 30.0,
            'valid_until': datetime.now() + timedelta(days=15),
            'usage_limit': 100,
            'is_active': True
        },
        {
            'code': 'VIP15',
            'discount_percent': 15.0,
            'valid_until': None,
            'usage_limit': None,
            'is_active': True
        },
        {
            'code': 'LOYALTY20',
            'discount_percent': 20.0,
            'valid_until': datetime.now() + timedelta(days=180),
            'usage_limit': 500,
            'is_active': True
        },
        {
            'code': 'FREESHIP',
            'discount_percent': 0.0,  # Special code for free shipping
            'valid_until': datetime.now() + timedelta(days=30),
            'usage_limit': 200,
            'is_active': True
        },
    ]

    # 5. Add promo codes only if they don't exist
    for promo_data in promos_to_add:
        if promo_data['code'] in existing_codes:
            print(f"⚠️  Promo code {promo_data['code']} already exists, skipping...")
            continue

        promo = PromoCode(
            code=promo_data['code'],
            discount_percent=promo_data['discount_percent'],
            valid_until=promo_data['valid_until'],
            usage_limit=promo_data['usage_limit'],
            is_active=promo_data['is_active']
        )

        db.add(promo)
        promos_added += 1
        print(f"✓ Added promo code: {promo_data['code']} ({promo_data['discount_percent']}%)")

    # 6. Commit only if we added something
    if items_added > 0 or promos_added > 0:
        db.commit()
        print(f"✅ Database seeded: {items_added} new items, {promos_added} new promo codes")
    else:
        print("✅ Database already contains all seed data")

    return items_added, promos_added