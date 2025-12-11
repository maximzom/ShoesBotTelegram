#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.db import get_db_session
from models.schemas import Item, PromoCode


def add_sample_products():
    db = get_db_session()

    try:
        existing_count = db.query(Item).count()
        print(f"Найдено товаров в базе: {existing_count}")

        if existing_count > 0:
            print("База уже содержит товары. Хотите продолжить? (y/N)")
            choice = input().strip().lower()
            if choice != 'y':
                return

        # Добавляем товары
        products = [
            {
                'sku': 'NIKE-AIR-001',
                'name': 'Nike Air Max 270',
                'description': 'Легкі та зручні кросівки Nike Air Max 270 з інноваційною технологією амортизації. Ідеальні для повсякденного носіння та бігу.',
                'price': 2499.00,
                'sizes': ["38", "39", "40", "41", "42", "43"],
                'category': 'men'
            },
            {
                'sku': 'ADIDAS-UB-002',
                'name': 'Adidas Ultraboost 22',
                'description': 'Преміальні бігові кросівки з революційною підошвою Boost. Забезпечують максимальний комфорт та повернення енергії.',
                'price': 3299.00,
                'sizes': ["39", "40", "41", "42", "43", "44"],
                'category': 'men'
            },
            {
                'sku': 'PUMA-WOMEN-003',
                'name': 'Puma Cali Sport Жіночі',
                'description': 'Стильні жіночі кросівки Puma Cali Sport у класичному білому кольорі. Комфортна підошва для цілоденного носіння.',
                'price': 1899.00,
                'sizes': ["35", "36", "37", "38", "39", "40"],
                'category': 'women'
            },
            {
                'sku': 'NEW-BALANCE-004',
                'name': 'New Balance 574',
                'description': 'Класичні кросівки New Balance 574 з підвищеною зносостійкістю та комфортом. Універсальний вибір для будь-якого стилю.',
                'price': 2199.00,
                'sizes': ["40", "41", "42", "43", "44", "45"],
                'category': 'unisex'
            },
            {
                'sku': 'CONVERSE-005',
                'name': 'Converse Chuck Taylor',
                'description': 'Легендарні кеди Converse Chuck Taylor All Star. Символ вуличної моди та музичної культури.',
                'price': 1499.00,
                'sizes': ["37", "38", "39", "40", "41", "42"],
                'category': 'unisex'
            }
        ]

        for product_data in products:
            # Проверяем, существует ли уже товар с таким SKU
            existing = db.query(Item).filter(Item.sku == product_data['sku']).first()

            if not existing:
                item = Item(
                    sku=product_data['sku'],
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    category=product_data['category']
                )
                item.set_sizes(product_data['sizes'])
                db.add(item)
                print(f"Додано товар: {product_data['name']}")
            else:
                print(f"Товар з SKU {product_data['sku']} вже існує")

        promos = [
            {
                'code': 'WELCOME10',
                'discount': 10.0,
                'days': 30,
                'limit': 100
            },
            {
                'code': 'SUMMER25',
                'discount': 25.0,
                'days': 60,
                'limit': 50
            },
            {
                'code': 'FIRSTORDER',
                'discount': 15.0,
                'days': 90,
                'limit': None
            }
        ]

        for promo_data in promos:
            existing = db.query(PromoCode).filter(PromoCode.code == promo_data['code']).first()

            if not existing:
                promo = PromoCode(
                    code=promo_data['code'],
                    discount_percent=promo_data['discount'],
                    valid_until=datetime.now() + timedelta(days=promo_data['days']),
                    usage_limit=promo_data['limit'],
                    is_active=True
                )
                db.add(promo)
                print(f"Додано промокод: {promo_data['code']}")

        db.commit()
        print(f"\n✅ Успішно додано {len(products)} товарів та {len(promos)} промокодів")

        # Показываем итоги
        total_items = db.query(Item).count()
        total_promos = db.query(PromoCode).count()
        print(f"Загальна кількість товарів: {total_items}")
        print(f"Загальна кількість промокодів: {total_promos}")

    except Exception as e:
        print(f"❌ Помилка: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    add_sample_products()