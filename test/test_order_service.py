"""
Unit tests for order service.
Run with: pytest tests/test_order_service.py -v
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from services.order_service import (
    generate_order_number,
    calculate_order_total,
    create_order,
    get_order_summary_dict,
    update_order_status
)
from models.schemas import User, Item, Order, OrderItem, PromoCode


class TestGenerateOrderNumber:
    """Test order number generation."""

    def test_generate_order_number_format(self):
        """Test that order number has correct format."""
        order_number = generate_order_number()

        assert order_number.startswith("ORD-")
        assert len(order_number) > 10  # ORD-YYYYMMDD-HHMMSS

        # Check date format in order number
        parts = order_number.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # HHMMSS


class TestCalculateOrderTotal:
    """Test order total calculation."""

    def test_calculate_subtotal_only(self):
        """Test calculation with only subtotal."""
        items = [
            {'price': 100.0, 'quantity': 2},  # 200
            {'price': 50.0, 'quantity': 1},   # 50
        ]

        totals = calculate_order_total(items)

        assert totals['subtotal'] == 250.0
        assert totals['delivery'] == 0.0
        assert totals['discount'] == 0.0
        assert totals['total'] == 250.0

    def test_calculate_with_delivery(self):
        """Test calculation with delivery."""
        items = [{'price': 100.0, 'quantity': 1}]

        # Mock Config
        with patch('services.order_service.Config') as mock_config:
            mock_config.DELIVERY_PRICE = 10000  # 100.00 UAH
            totals = calculate_order_total(items, delivery_method="delivery")

            assert totals['subtotal'] == 100.0
            assert totals['delivery'] == 100.0
            assert totals['discount'] == 0.0
            assert totals['total'] == 200.0

    def test_calculate_with_promo_code(self):
        """Test calculation with promo code."""
        items = [{'price': 1000.0, 'quantity': 1}]

        # Mock database session and promo code
        mock_db = Mock()
        mock_promo = Mock()
        mock_promo.discount_percent = 10.0
        mock_promo.is_valid = Mock(return_value=True)

        mock_db.query.return_value.filter.return_value.first.return_value = mock_promo

        totals = calculate_order_total(
            items,
            delivery_method="pickup",
            promo_code="TEST10",
            db=mock_db
        )

        assert totals['subtotal'] == 1000.0
        assert totals['delivery'] == 0.0
        assert totals['discount'] == 100.0  # 10% of 1000
        assert totals['total'] == 900.0

    def test_calculate_with_invalid_promo_code(self):
        """Test calculation with invalid promo code."""
        items = [{'price': 1000.0, 'quantity': 1}]

        # Mock database session with no promo code
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        totals = calculate_order_total(
            items,
            delivery_method="pickup",
            promo_code="INVALID",
            db=mock_db
        )

        assert totals['subtotal'] == 1000.0
        assert totals['delivery'] == 0.0
        assert totals['discount'] == 0.0
        assert totals['total'] == 1000.0

    def test_calculate_with_expired_promo_code(self):
        """Test calculation with expired promo code."""
        items = [{'price': 1000.0, 'quantity': 1}]

        # Mock database session with expired promo code
        mock_db = Mock()
        mock_promo = Mock()
        mock_promo.discount_percent = 10.0
        mock_promo.is_valid = Mock(return_value=False)  # Expired

        mock_db.query.return_value.filter.return_value.first.return_value = mock_promo

        totals = calculate_order_total(
            items,
            delivery_method="pickup",
            promo_code="EXPIRED",
            db=mock_db
        )

        assert totals['subtotal'] == 1000.0
        assert totals['delivery'] == 0.0
        assert totals['discount'] == 0.0
        assert totals['total'] == 1000.0

    def test_calculate_empty_items(self):
        """Test calculation with empty items list."""
        items = []

        totals = calculate_order_total(items)

        assert totals['subtotal'] == 0.0
        assert totals['delivery'] == 0.0
        assert totals['discount'] == 0.0
        assert totals['total'] == 0.0


class TestCreateOrder:
    """Test order creation."""

    @patch('services.order_service.generate_order_number')
    @patch('services.order_service.calculate_order_total')
    def test_create_order_without_promo(self, mock_calculate, mock_generate):
        """Test creating order without promo code."""
        # Setup mocks
        mock_generate.return_value = "TEST-ORDER-123"
        mock_calculate.return_value = {
            'subtotal': 3000.0,
            'delivery': 0.0,
            'discount': 0.0,
            'total': 3000.0
        }

        # Mock user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.tg_id = 123456

        # Mock items data
        items_data = [
            {
                'item_id': 1,
                'size': '42',
                'quantity': 2,
                'price': 1500.0
            }
        ]

        # Mock database session
        mock_db = Mock()
        mock_db.add = Mock()
        mock_db.flush = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # Mock promo query (returns None)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Capture created order
        captured_order = None
        def capture_add(obj):
            nonlocal captured_order
            if isinstance(obj, Order):
                captured_order = obj
                # Set some attributes for the order
                obj.id = 1
                obj.order_number = "TEST-ORDER-123"
                obj.total = 3000.0
                obj.status = 'pending'

        mock_db.add.side_effect = capture_add

        # Create order
        order = create_order(
            user=mock_user,
            items_data=items_data,
            delivery_method="pickup",
            address=None,
            phone="+380501234567",
            promo_code=None,
            db=mock_db
        )

        # Verify order was created
        assert captured_order is not None
        assert captured_order.order_number == "TEST-ORDER-123"
        assert captured_order.total == 3000.0
        assert captured_order.status == 'pending'
        assert captured_order.user_id == 1

        # Verify mocks were called
        mock_generate.assert_called_once()
        mock_calculate.assert_called_once()
        assert mock_db.add.call_count >= 2  # Order + order items
        mock_db.commit.assert_called_once()

    @patch('services.order_service.generate_order_number')
    @patch('services.order_service.calculate_order_total')
    def test_create_order_with_promo(self, mock_calculate, mock_generate):
        """Test creating order with promo code."""
        # Setup mocks
        mock_generate.return_value = "TEST-ORDER-456"
        mock_calculate.return_value = {
            'subtotal': 1000.0,
            'delivery': 0.0,
            'discount': 100.0,  # 10% of 1000
            'total': 900.0
        }

        # Mock user
        mock_user = Mock(spec=User)
        mock_user.id = 1

        # Mock items data
        items_data = [
            {
                'item_id': 1,
                'size': '42',
                'quantity': 1,
                'price': 1000.0
            }
        ]

        # Mock database session
        mock_db = Mock()
        mock_db.add = Mock()
        mock_db.flush = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # Mock promo code
        mock_promo = Mock(spec=PromoCode)
        mock_promo.code = "TEST10"
        mock_promo.discount_percent = 10.0
        mock_promo.usage_count = 0

        # Mock promo query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_promo

        # Capture created order
        captured_order = None
        def capture_add(obj):
            nonlocal captured_order
            if isinstance(obj, Order):
                captured_order = obj
                obj.id = 1
                obj.order_number = "TEST-ORDER-456"
                obj.total = 900.0
                obj.status = 'pending'

        mock_db.add.side_effect = capture_add

        # Create order
        order = create_order(
            user=mock_user,
            items_data=items_data,
            delivery_method="pickup",
            address=None,
            phone="+380501234567",
            promo_code="TEST10",
            db=mock_db
        )

        # Verify order was created with promo
        assert captured_order is not None
        assert captured_order.order_number == "TEST-ORDER-456"
        assert captured_order.total == 900.0
        assert captured_order.status == 'pending'

        # Verify promo code usage was incremented
        assert mock_promo.usage_count == 1


class TestOrderSummary:
    """Test order summary functions."""

    @patch('services.order_service.Config')
    def test_get_order_summary_dict(self, mock_config):
        """Test getting order summary as dictionary."""
        # Mock config
        mock_config.DELIVERY_PRICE = 10000  # 100.00 UAH

        # Create real Order object
        order = Order(
            order_number="ORD-20240101-120000",
            user_id=1,
            total=1500.0,
            status='pending',
            delivery_method='pickup',
            address=None,
            phone="+380501234567",
            discount=0.0,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )

        # Create real Item and OrderItem objects
        item = Item(name="Nike Air Max", price=1500.0)
        order_item = OrderItem(
            order_id=1,
            item_id=1,
            size='42',
            quantity=1,
            price=1500.0
        )
        order_item.item = item

        # Manually set items relationship
        order.items = [order_item]

        # Get summary
        summary = get_order_summary_dict(order)

        # Verify summary
        assert summary['order_number'] == "ORD-20240101-120000"
        assert summary['total'] == 1500.0
        assert summary['status'] == 'pending'
        assert summary['delivery_method'] == "Самовивіз (безкоштовно)"
        assert summary['address'] == "Самовивіз"
        assert summary['phone'] == "+380501234567"
        assert summary['discount'] == 0.0
        assert summary['created_at'] == "01.01.2024 12:00"
        assert "Nike Air Max" in summary['items']


# Run tests with: pytest tests/test_order_service.py -v --cov=services.order_service
if __name__ == "__main__":
    pytest.main([__file__, "-v"])