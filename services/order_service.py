"""
Business logic for order management.
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from models.schemas import Order, OrderItem, User, Item, PromoCode
from config import Config

logger = logging.getLogger(__name__)


def generate_order_number() -> str:
    """Generate unique order number."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"ORD-{timestamp}"


def calculate_order_total(
    items: List[Dict],
    delivery_method: str = "pickup",
    promo_code: Optional[str] = None,
    db: Session = None
) -> Dict[str, float]:
    """
    Calculate order total with delivery and discounts.
    
    Args:
        items: List of dicts with 'price' and 'quantity'
        delivery_method: 'pickup' or 'delivery'
        promo_code: Optional promo code
        db: Database session
        
    Returns:
        Dict with subtotal, delivery, discount, and total
    """
    # Calculate subtotal
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    
    # Delivery cost
    delivery_cost = 0.0
    if delivery_method == "delivery":
        delivery_cost = Config.DELIVERY_PRICE / 100  # Convert from kopiykas to UAH
    
    # Apply promo code
    discount = 0.0
    if promo_code and db:
        promo = db.query(PromoCode).filter(
            PromoCode.code == promo_code.upper()
        ).first()
        
        if promo and promo.is_valid():
            discount = subtotal * (promo.discount_percent / 100)
    
    # Calculate total
    total = subtotal + delivery_cost - discount
    
    return {
        'subtotal': round(subtotal, 2),
        'delivery': round(delivery_cost, 2),
        'discount': round(discount, 2),
        'total': round(total, 2)
    }


def create_order(
    user: User,
    items_data: List[Dict],
    delivery_method: str,
    address: Optional[str],
    phone: str,
    promo_code: Optional[str],
    db: Session
) -> Order:
    """
    Create a new order.
    
    Args:
        user: User object
        items_data: List of dicts with item_id, size, quantity, price
        delivery_method: 'pickup' or 'delivery'
        address: Delivery address (optional for pickup)
        phone: Contact phone
        promo_code: Promo code (optional)
        db: Database session
        
    Returns:
        Created Order object
    """
    # Calculate totals
    totals = calculate_order_total(
        items_data,
        delivery_method,
        promo_code,
        db
    )
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        user_id=user.id,
        total=totals['total'],
        status='pending',
        delivery_method=delivery_method,
        address=address,
        phone=phone,
        promo_code=promo_code,
        discount=totals['discount']
    )
    
    db.add(order)
    db.flush()  # Get order ID
    
    # Create order items
    for item_data in items_data:
        order_item = OrderItem(
            order_id=order.id,
            item_id=item_data['item_id'],
            size=item_data['size'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.add(order_item)
    
    # Update promo code usage if applicable
    if promo_code:
        promo = db.query(PromoCode).filter(
            PromoCode.code == promo_code.upper()
        ).first()
        if promo:
            promo.usage_count += 1
    
    db.commit()
    db.refresh(order)
    
    logger.info(f"Order {order.order_number} created by user {user.tg_id}")
    
    return order


def get_user_orders(user: User, db: Session) -> List[Order]:
    """Get all orders for a user."""
    return db.query(Order).filter(
        Order.user_id == user.id
    ).order_by(Order.created_at.desc()).all()


def get_order_by_number(order_number: str, db: Session) -> Optional[Order]:
    """Get order by order number."""
    return db.query(Order).filter(
        Order.order_number == order_number
    ).first()


def get_all_orders(
        db: Session,
        status: Optional[str] = None,
        limit: int = 50
) -> List[Order]:
    """
    Get all orders (admin function).

    Args:
        db: Database session
        status: Filter by status (optional)
        limit: Maximum orders to return

    Returns:
        List of orders
    """
    query = db.query(Order).order_by(Order.created_at.desc())

    if status:
        query = query.filter(Order.status == status)

    return query.limit(limit).all()


def update_order_status(
    order: Order,
    new_status: str,
    db: Session
) -> Order:
    """
    Update order status.
    
    Args:
        order: Order object
        new_status: New status (pending/confirmed/paid/shipped/cancelled)
        db: Database session
        
    Returns:
        Updated order
    """
    valid_statuses = ['pending', 'confirmed', 'paid', 'shipped', 'cancelled']
    
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}")
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    logger.info(f"Order {order.order_number} status updated to {new_status}")
    
    return order


def format_order_items_text(order: Order) -> str:
    """
    Format order items as text for messages.
    
    Args:
        order: Order object
        
    Returns:
        Formatted string
    """
    lines = []
    
    for order_item in order.items:
        item = order_item.item
        line = f"• {item.name} (розмір {order_item.size}) x {order_item.quantity} = {order_item.subtotal():.2f} грн"
        lines.append(line)
    
    return "\n".join(lines)


def validate_promo_code(code: str, db: Session) -> Optional[PromoCode]:
    """
    Validate promo code.
    
    Args:
        code: Promo code string
        db: Database session
        
    Returns:
        PromoCode object if valid, None otherwise
    """
    promo = db.query(PromoCode).filter(
        PromoCode.code == code.upper()
    ).first()
    
    if promo and promo.is_valid():
        return promo
    
    return None


def get_order_summary_dict(order: Order, db: Session = None) -> Dict:
    """
    Get order summary as dictionary.

    Args:
        order: Order object
        db: Database session (optional, for loading relationships)

    Returns:
        Dictionary with order details
    """
    # If order has items loaded, use them
    items_text = ""

    if hasattr(order, 'items') and order.items:
        items_text = format_order_items_text(order)
    else:
        # Try to load items if db provided
        if db:
            from models.schemas import OrderItem, Item
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

            lines = []
            for oi in order_items:
                item = db.query(Item).filter(Item.id == oi.item_id).first()
                if item:
                    line = f"• {item.name} (розмір {oi.size}) x {oi.quantity} = {oi.subtotal():.2f} грн"
                else:
                    line = f"• Товар #{oi.item_id} (розмір {oi.size}) x {oi.quantity} = {oi.subtotal():.2f} грн"
                lines.append(line)

            items_text = "\n".join(lines)
        else:
            items_text = "Не вдалося завантажити товари"

    # Delivery text
    delivery_text = "Самовивіз (безкоштовно)"
    delivery_cost = 0.0

    if order.delivery_method == "delivery":
        delivery_cost = Config.DELIVERY_PRICE / 100
        delivery_text = f"Доставка ({delivery_cost:.2f} грн)"

    # Calculate subtotal
    subtotal = order.total - delivery_cost + order.discount

    return {
        'order_number': order.order_number,
        'items': items_text,
        'subtotal': subtotal,
        'delivery': delivery_cost,
        'discount': order.discount,
        'total': order.total,
        'delivery_method': delivery_text,
        'address': order.address or "Самовивіз",
        'phone': order.phone,
        'status': order.status,
        'created_at': order.created_at.strftime("%d.%m.%Y %H:%M")
    }