"""
Input validation utilities for the shoe shop bot.
"""
import re
from typing import List, Optional
from config import Config


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> validate_phone("+380501234567")
        True
        >>> validate_phone("0501234567")
        False
    """
    pattern = re.compile(Config.PHONE_PATTERN)
    return bool(pattern.match(phone.strip()))


def validate_price(price_str: str) -> Optional[float]:
    """
    Validate and parse price string.
    
    Args:
        price_str: Price as string
        
    Returns:
        Float price if valid, None otherwise
        
    Examples:
        >>> validate_price("1500")
        1500.0
        >>> validate_price("1500.50")
        1500.5
        >>> validate_price("abc")
        None
    """
    try:
        price = float(price_str.strip().replace(",", "."))
        if Config.MIN_PRICE <= price <= Config.MAX_PRICE:
            return price
        return None
    except (ValueError, AttributeError):
        return None


def validate_sizes(sizes_str: str) -> Optional[List[str]]:
    """
    Validate and parse sizes string.
    
    Args:
        sizes_str: Comma-separated sizes
        
    Returns:
        List of valid sizes if valid, None otherwise
        
    Examples:
        >>> validate_sizes("38,39,40,41")
        ['38', '39', '40', '41']
        >>> validate_sizes("38, 39, 40")
        ['38', '39', '40']
    """
    try:
        sizes = [s.strip() for s in sizes_str.split(",")]
        # Check if all sizes are valid
        valid_sizes = [s for s in sizes if s in Config.AVAILABLE_SIZES]
        
        if valid_sizes and len(valid_sizes) == len(sizes):
            return valid_sizes
        return None
    except (ValueError, AttributeError):
        return None


def validate_quantity(quantity_str: str) -> Optional[int]:
    """
    Validate and parse quantity string.
    
    Args:
        quantity_str: Quantity as string
        
    Returns:
        Integer quantity if valid (1-99), None otherwise
        
    Examples:
        >>> validate_quantity("5")
        5
        >>> validate_quantity("0")
        None
        >>> validate_quantity("100")
        None
    """
    try:
        quantity = int(quantity_str.strip())
        if 1 <= quantity <= 99:
            return quantity
        return None
    except (ValueError, AttributeError):
        return None


def validate_promo_discount(discount_str: str) -> Optional[float]:
    """
    Validate promo code discount percentage.
    
    Args:
        discount_str: Discount percentage as string
        
    Returns:
        Float discount if valid (0-100), None otherwise
    """
    try:
        discount = float(discount_str.strip().replace(",", "."))
        if 0 < discount <= 100:
            return discount
        return None
    except (ValueError, AttributeError):
        return None


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


def mask_phone(phone: str) -> str:
    """
    Mask phone number for logging (privacy).
    
    Args:
        phone: Phone number
        
    Returns:
        Masked phone number
        
    Examples:
        >>> mask_phone("+380501234567")
        '+38****4567'
    """
    if len(phone) < 6:
        return "***"
    
    return phone[:3] + "****" + phone[-4:]


def validate_sku(sku: str) -> bool:
    """
    Validate SKU format.
    
    Args:
        sku: Stock keeping unit code
        
    Returns:
        True if valid format
    """
    # SKU should be alphanumeric, 3-50 chars
    pattern = re.compile(r"^[A-Z0-9_-]{3,50}$", re.IGNORECASE)
    return bool(pattern.match(sku.strip()))