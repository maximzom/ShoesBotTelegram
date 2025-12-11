#!/usr/bin/env python3
"""
Backup orders to CSV file.
Run with: python scripts/backup_orders.py
"""
import os
import sys
import csv
import logging
from datetime import datetime
from typing import List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.db import get_db_session
from models.schemas import Order, OrderItem, User, Item

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backup_orders_to_csv(output_file: str = None, limit: int = None):
    """
    Backup all orders to CSV file.

    Args:
        output_file: Output CSV file path (optional)
        limit: Maximum number of orders to export (optional)
    """
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"backups/orders_{timestamp}.csv"

    # Ensure backup directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    db = get_db_session()

    try:
        # Query orders
        query = db.query(Order).order_by(Order.created_at.desc())

        if limit:
            query = query.limit(limit)

        orders = query.all()

        logger.info(f"Exporting {len(orders)} orders to {output_file}")

        # Prepare CSV data
        csv_data = []

        for order in orders:
            user = order.user

            # Get order items
            for order_item in order.items:
                item = order_item.item

                csv_data.append({
                    'order_number': order.order_number,
                    'order_date': order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'status': order.status,
                    'customer_id': user.tg_id,
                    'customer_username': user.username or '',
                    'customer_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                    'customer_phone': user.phone or '',
                    'item_sku': item.sku,
                    'item_name': item.name,
                    'item_size': order_item.size,
                    'item_quantity': order_item.quantity,
                    'item_price': order_item.price,
                    'item_subtotal': order_item.subtotal(),
                    'delivery_method': order.delivery_method,
                    'delivery_address': order.address or '',
                    'promo_code': order.promo_code or '',
                    'discount': order.discount,
                    'order_total': order.total
                })

        # Write to CSV
        if csv_data:
            fieldnames = csv_data[0].keys()

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

            logger.info(f"Successfully exported {len(csv_data)} order items to {output_file}")

        else:
            logger.warning("No orders to export")

    except Exception as e:
        logger.error(f"Error exporting orders: {e}")

    finally:
        db.close()


def backup_users_to_csv(output_file: str = None):
    """
    Backup all users to CSV file.

    Args:
        output_file: Output CSV file path (optional)
    """
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"backups/users_{timestamp}.csv"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    db = get_db_session()

    try:
        users = db.query(User).all()

        logger.info(f"Exporting {len(users)} users to {output_file}")

        csv_data = []

        for user in users:
            # Get user statistics
            total_orders = len(user.orders)
            total_feedback = len(user.feedbacks)

            csv_data.append({
                'user_id': user.tg_id,
                'username': user.username or '',
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'phone': user.phone or '',
                'language': user.language,
                'registration_date': user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'total_orders': total_orders,
                'total_feedback': total_feedback,
                'state': user.state or ''
            })

        if csv_data:
            fieldnames = csv_data[0].keys()

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

            logger.info(f"Successfully exported {len(csv_data)} users to {output_file}")

        else:
            logger.warning("No users to export")

    except Exception as e:
        logger.error(f"Error exporting users: {e}")

    finally:
        db.close()


def backup_products_to_csv(output_file: str = None):
    """
    Backup all products to CSV file.

    Args:
        output_file: Output CSV file path (optional)
    """
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"backups/products_{timestamp}.csv"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    db = get_db_session()

    try:
        products = db.query(Item).all()

        logger.info(f"Exporting {len(products)} products to {output_file}")

        csv_data = []

        for product in products:
            sizes = product.get_sizes()

            csv_data.append({
                'sku': product.sku,
                'name': product.name,
                'description': product.description or '',
                'price': product.price,
                'sizes': ', '.join(sizes),
                'category': product.category or '',
                'created_date': product.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'image_count': len(product.get_images())
            })

        if csv_data:
            fieldnames = csv_data[0].keys()

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

            logger.info(f"Successfully exported {len(csv_data)} products to {output_file}")

        else:
            logger.warning("No products to export")

    except Exception as e:
        logger.error(f"Error exporting products: {e}")

    finally:
        db.close()


def main():
    """Main backup script."""
    import argparse

    parser = argparse.ArgumentParser(description="Backup database to CSV")
    parser.add_argument('--type', choices=['orders', 'users', 'products', 'all'],
                        default='orders', help='What to backup')
    parser.add_argument('--output', help='Output CSV file (optional)')
    parser.add_argument('--limit', type=int, help='Limit number of records')

    args = parser.parse_args()

    if args.type == 'orders' or args.type == 'all':
        backup_orders_to_csv(args.output, args.limit)

    if args.type == 'users' or args.type == 'all':
        backup_users_to_csv(args.output)

    if args.type == 'products' or args.type == 'all':
        backup_products_to_csv(args.output)


if __name__ == "__main__":
    main()