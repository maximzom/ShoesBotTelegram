"""
Helper functions for the bot.
"""
import re
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP


def format_price(price: float, currency: str = "грн") -> str:
    """
    Format price for display.

    Args:
        price: Price value
        currency: Currency symbol

    Returns:
        Formatted price string
    """
    # Round to 2 decimal places
    rounded = Decimal(str(price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Format with thousand separators
    parts = str(rounded).split('.')
    integer_part = parts[0]

    # Add thousand separators
    if len(integer_part) > 3:
        integer_part = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1 ', integer_part)

    formatted = integer_part

    if len(parts) > 1:
        decimal_part = parts[1].ljust(2, '0')
        formatted += f'.{decimal_part}'
    else:
        formatted += '.00'

    return f"{formatted} {currency}"


def format_datetime(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
    """
    Format datetime for display.

    Args:
        dt: Datetime object
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    if not dt:
        return ""

    return dt.strftime(format_str)


def truncate_text(text: str, max_length: int = 100, ellipsis: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        ellipsis: Ellipsis string

    Returns:
        Truncated text
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - len(ellipsis)] + ellipsis


def safe_json_loads(text: str, default: Any = None) -> Any:
    """
    Safely load JSON string.

    Args:
        text: JSON string
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    if not text:
        return default

    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: Any = None) -> str:
    """
    Safely dump data to JSON string.

    Args:
        data: Data to serialize
        default: Default value for non-serializable objects

    Returns:
        JSON string
    """
    try:
        return json.dumps(data, ensure_ascii=False, default=default)
    except (TypeError, ValueError):
        return "{}"


def parse_human_size(size: str) -> Optional[str]:
    """
    Parse human-readable size to standardized format.

    Args:
        size: Size string (e.g., "38", "38.5", "38-39")

    Returns:
        Standardized size or None
    """
    if not size:
        return None

    # Remove whitespace
    size = size.strip()

    # Handle ranges like "38-39" - take the first size
    if '-' in size:
        size = size.split('-')[0]

    # Handle EU sizes (e.g., "38", "38.5")
    try:
        # Try to parse as float
        size_float = float(size)

        # Check if it's a common shoe size
        if 20 <= size_float <= 50:
            # Return as string without trailing .0
            if size_float.is_integer():
                return str(int(size_float))
            return str(size_float)
    except ValueError:
        pass

    # Handle text sizes
    size_lower = size.lower()
    size_map = {
        'xs': '35-36',
        's': '37-38',
        'm': '39-40',
        'l': '41-42',
        'xl': '43-44',
        'xxl': '45-46'
    }

    return size_map.get(size_lower)


def calculate_delivery_date(order_date: datetime, working_days: int = 3) -> datetime:
    """
    Calculate expected delivery date.

    Args:
        order_date: Order date
        working_days: Number of working days for delivery

    Returns:
        Expected delivery date
    """
    delivery_date = order_date

    # Skip weekends
    days_added = 0
    while days_added < working_days:
        delivery_date += timedelta(days=1)

        # Monday=0, Sunday=6
        if delivery_date.weekday() < 5:  # Monday-Friday
            days_added += 1

    return delivery_date


def format_delivery_timeframe(order_date: datetime) -> str:
    """
    Format delivery timeframe for user.

    Args:
        order_date: Order date

    Returns:
        Formatted delivery timeframe
    """
    delivery_date = calculate_delivery_date(order_date)

    today = datetime.now().date()
    order_day = order_date.date()
    delivery_day = delivery_date.date()

    if order_day == today:
        if delivery_day == order_day + timedelta(days=1):
            return "завтра"
        elif delivery_day == order_day + timedelta(days=2):
            return "післязавтра"

    # Format as "15 січня"
    month_names = [
        "січня", "лютого", "березня", "квітня", "травня", "червня",
        "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"
    ]

    day = delivery_day.day
    month = month_names[delivery_day.month - 1]

    return f"{day} {month}"


def generate_order_summary_text(items: List[Dict], totals: Dict) -> str:
    """
    Generate order summary text.

    Args:
        items: List of item dictionaries
        totals: Dictionary with totals

    Returns:
        Formatted summary text
    """
    lines = ["📦 **Ваше замовлення:**"]

    for item in items:
        line = f"• {item['name']} (розмір {item['size']}) x {item['quantity']} = {item['subtotal']:.2f} грн"
        lines.append(line)

    lines.append("")
    lines.append("💰 **Підсумок:**")
    lines.append(f"Сума товарів: {totals['subtotal']:.2f} грн")

    if totals['delivery'] > 0:
        lines.append(f"Доставка: {totals['delivery']:.2f} грн")

    if totals['discount'] > 0:
        lines.append(f"Знижка: -{totals['discount']:.2f} грн")

    lines.append(f"**Всього: {totals['total']:.2f} грн**")

    return "\n".join(lines)


def mask_sensitive_data(text: str) -> str:
    """
    Mask sensitive data in text for logging.

    Args:
        text: Text to mask

    Returns:
        Masked text
    """
    # Mask phone numbers
    text = re.sub(r'(\+?\d[\d\-\(\) ]{7,}\d)', '***', text)

    # Mask email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***', text)

    # Mask credit card numbers (simplified)
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '**** **** **** ****', text)

    return text