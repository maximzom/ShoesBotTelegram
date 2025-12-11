#!/usr/bin/env python3
"""
Export data to CSV for analysis.
Run with: python scripts/export_csv.py
"""
import os
import sys
import csv
import logging
from datetime import datetime, timedelta
from typing import List, Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.db import get_db_session
from models.schemas import Order, User, Item, PromoCode
from sqlalchemy import func, and_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_sales_report(start_date: datetime = None, end_date: datetime = None):
    """
    Export sales report to CSV.

    Args:
        start_date: Start date for report (optional)
        end_date: End date for report (optional)
    """
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)

    if not end_date:
        end_date = datetime.now()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"exports/sales_report_{timestamp}.csv"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    db = get_db_session()

    try:
        # Build query
        query = db.query(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        )

        orders = query.order_by(Order.created_at).all()

        logger.info(f"Exporting {len(orders)} orders from {start_date.date()} to {end_date.date()}")

        # Prepare report data
        report_data = []
        daily_totals = {}

        for order in orders:
            order_date = order.created_at.date()

            # Add to daily totals
            if order_date not in daily_totals:
                daily_totals[order_date] = {
                    'orders': 0,
                    'revenue': 0.0,
                    'items': 0
                }

            daily_totals[order_date]['orders'] += 1
            daily_totals[order_date]['revenue'] += order.total
            daily_totals[order_date]['items'] += sum(item.quantity for item in order.items)

            # Add order details
            report_data.append({
                'date': order_date.strftime("%Y-%m-%d"),
                'order_number': order.order_number,
                'status': order.status,
                'customer_id': order.user.tg_id,
                'customer_name': f"{order.user.first_name or ''} {order.user.last_name or ''}".strip(),
                'items': sum(item.quantity for item in order.items),
                'subtotal': order.total - (100.0 if order.delivery_method == 'delivery' else 0) + order.discount,
                'delivery': 100.0 if order.delivery_method == 'delivery' else 0.0,
                'discount': order.discount,
                'total': order.total,
                'delivery_method': order.delivery_method,
                'promo_code': order.promo_code or ''
            })

        # Write detailed report
        if report_data:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = report_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(report_data)

        # Write summary report
        summary_file = f"exports/sales_summary_{timestamp}.csv"

        summary_data = []
        for date, totals in sorted(daily_totals.items()):
            summary_data.append({
                'date': date.strftime("%Y-%m-%d"),
                'orders': totals['orders'],
                'items_sold': totals['items'],
                'revenue': totals['revenue'],
                'avg_order_value': totals['revenue'] / totals['orders'] if totals['orders'] > 0 else 0
            })

        if summary_data:
            with open(summary_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = summary_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(summary_data)

        # Calculate overall statistics
        total_orders = len(orders)
        total_revenue = sum(order.total for order in orders)
        total_items = sum(sum(item.quantity for item in order.items) for order in orders)

        logger.info(f"Report generated:")
        logger.info(f"  - Period: {start_date.date()} to {end_date.date()}")
        logger.info(f"  - Total orders: {total_orders}")
        logger.info(f"  - Total revenue: {total_revenue:.2f} грн")
        logger.info(f"  - Total items sold: {total_items}")
        logger.info(f"  - Files: {output_file}, {summary_file}")

    except Exception as e:
        logger.error(f"Error generating sales report: {e}")

    finally:
        db.close()


def export_customer_report():
    """Export customer analysis report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"exports/customers_{timestamp}.csv"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    db = get_db_session()

    try:
        # Get all users with their order statistics
        users = db.query(User).all()

        customer_data = []

        for user in users:
            orders = user.orders
            feedbacks = user.feedbacks

            if not orders:
                continue  # Skip users without orders

            # Calculate statistics
            total_orders = len(orders)
            total_spent = sum(order.total for order in orders)
            avg_order_value = total_spent / total_orders if total_orders > 0 else 0

            # First and last order dates
            order_dates = [order.created_at for order in orders]
            first_order = min(order_dates) if order_dates else None
            last_order = max(order_dates) if order_dates else None

            # Days since first order
            days_since_first = (datetime.now() - first_order).days if first_order else 0

            customer_data.append({
                'customer_id': user.tg_id,
                'username': user.username or '',
                'name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                'phone': user.phone or '',
                'registration_date': user.created_at.strftime("%Y-%m-%d"),
                'first_order': first_order.strftime("%Y-%m-%d") if first_order else '',
                'last_order': last_order.strftime("%Y-%m-%d") if last_order else '',
                'days_since_first': days_since_first,
                'total_orders': total_orders,
                'total_spent': total_spent,
                'avg_order_value': avg_order_value,
                'feedback_count': len(feedbacks)
            })

        if customer_data:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = customer_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(customer_data)

            logger.info(f"Exported {len(customer_data)} customers to {output_file}")

        else:
            logger.warning("No customer data to export")

    except Exception as e:
        logger.error(f"Error exporting customer report: {e}")

    finally:
        db.close()


def export_product_report():
    """Export product performance report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"exports/products_performance_{timestamp}.csv"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    db = get_db_session()

    try:
        # Get all products
        products = db.query(Item).all()

        product_data = []

        for product in products:
            # Get order items for this product
            order_items = product.order_items

            total_quantity = sum(item.quantity for item in order_items)
            total_revenue = sum(item.subtotal() for item in order_items)

            # Get unique customers who bought this product
            customers = set()
            for item in order_items:
                if item.order and item.order.user:
                    customers.add(item.order.user.tg_id)

            product_data.append({
                'sku': product.sku,
                'name': product.name,
                'category': product.category or '',
                'price': product.price,
                'sizes': ', '.join(product.get_sizes()),
                'total_sold': total_quantity,
                'total_revenue': total_revenue,
                'unique_customers': len(customers),
                'avg_quantity_per_order': total_quantity / len(order_items) if order_items else 0,
                'created_date': product.created_at.strftime("%Y-%m-%d")
            })

        if product_data:
            # Sort by total revenue
            product_data.sort(key=lambda x: x['total_revenue'], reverse=True)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = product_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(product_data)

            logger.info(f"Exported {len(product_data)} products to {output_file}")

            # Print top 5 products
            logger.info("Top 5 products by revenue:")
            for i, product in enumerate(product_data[:5]):
                logger.info(
                    f"  {i + 1}. {product['name']}: {product['total_revenue']:.2f} грн ({product['total_sold']} шт)")

        else:
            logger.warning("No product data to export")

    except Exception as e:
        logger.error(f"Error exporting product report: {e}")

    finally:
        db.close()


def main():
    """Main export script."""
    import argparse

    parser = argparse.ArgumentParser(description="Export data to CSV")
    parser.add_argument('--report', choices=['sales', 'customers', 'products', 'all'],
                        default='sales', help='Report type to generate')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')

    args = parser.parse_args()

    # Parse dates
    start_date = None
    end_date = None

    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")

    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    if args.report == 'sales' or args.report == 'all':
        export_sales_report(start_date, end_date)

    if args.report == 'customers' or args.report == 'all':
        export_customer_report()

    if args.report == 'products' or args.report == 'all':
        export_product_report()


if __name__ == "__main__":
    main()