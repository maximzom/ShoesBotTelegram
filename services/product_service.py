"""
Business logic for product management.
"""
import logging
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from models.schemas import Item
from utils.validators import validate_price, validate_sizes, validate_sku

logger = logging.getLogger(__name__)


def create_item(
        db: Session,
        sku: str,
        name: str,
        price: float,
        sizes: List[str],
        description: Optional[str] = None,
        category: Optional[str] = None,
        images: Optional[List[str]] = None
) -> Optional[Item]:
    """
    Create a new product item.

    Args:
        db: Database session
        sku: Unique SKU code
        name: Product name
        price: Product price
        sizes: List of available sizes
        description: Product description (optional)
        category: Product category (optional)
        images: List of image file IDs (optional)

    Returns:
        Created Item object or None if validation fails
    """
    # Validate inputs
    if not validate_sku(sku):
        logger.error(f"Invalid SKU: {sku}")
        return None

    if not name or len(name.strip()) < 2:
        logger.error(f"Invalid product name: {name}")
        return None

    if not validate_price(str(price)):
        logger.error(f"Invalid price: {price}")
        return None

    if not sizes or not validate_sizes(','.join(sizes)):
        logger.error(f"Invalid sizes: {sizes}")
        return None

    # Check if SKU already exists
    existing = db.query(Item).filter(Item.sku == sku.upper()).first()
    if existing:
        logger.error(f"SKU already exists: {sku}")
        return None

    # Create item
    item = Item(
        sku=sku.upper(),
        name=name.strip(),
        price=price,
        description=description.strip() if description else None,
        category=category.lower() if category else None
    )

    item.set_sizes(sizes)

    if images:
        item.set_images(images)

    db.add(item)
    db.commit()
    db.refresh(item)

    logger.info(f"Product created: {item.sku} - {item.name}")

    return item


def update_item(
        db: Session,
        item_id: int,
        **kwargs
) -> Optional[Item]:
    """
    Update existing product item.

    Args:
        db: Database session
        item_id: ID of item to update
        **kwargs: Fields to update

    Returns:
        Updated Item object or None if not found
    """
    item = db.query(Item).filter(Item.id == item_id).first()

    if not item:
        logger.error(f"Item not found: {item_id}")
        return None

    # Update fields
    if 'sku' in kwargs:
        sku = kwargs['sku'].upper()
        if validate_sku(sku):
            # Check if SKU is unique
            existing = db.query(Item).filter(Item.sku == sku, Item.id != item_id).first()
            if not existing:
                item.sku = sku
            else:
                logger.error(f"SKU already exists: {sku}")
                return None

    if 'name' in kwargs and kwargs['name']:
        item.name = kwargs['name'].strip()

    if 'price' in kwargs:
        price = kwargs['price']
        if validate_price(str(price)):
            item.price = price
        else:
            logger.error(f"Invalid price: {price}")
            return None

    if 'sizes' in kwargs:
        sizes = kwargs['sizes']
        if validate_sizes(','.join(sizes)):
            item.set_sizes(sizes)
        else:
            logger.error(f"Invalid sizes: {sizes}")
            return None

    if 'description' in kwargs:
        item.description = kwargs['description'].strip() if kwargs['description'] else None

    if 'category' in kwargs:
        category = kwargs['category']
        if category in ['men', 'women', 'kids', None]:
            item.category = category

    if 'images' in kwargs:
        item.set_images(kwargs['images'])

    db.commit()
    db.refresh(item)

    logger.info(f"Product updated: {item.sku}")

    return item


def delete_item(db: Session, item_id: int) -> bool:
    """
    Delete product item.

    Args:
        db: Database session
        item_id: ID of item to delete

    Returns:
        True if deleted, False otherwise
    """
    item = db.query(Item).filter(Item.id == item_id).first()

    if not item:
        logger.error(f"Item not found for deletion: {item_id}")
        return False

    db.delete(item)
    db.commit()

    logger.info(f"Product deleted: {item.sku}")

    return True


def get_items_by_category(db: Session, category: str) -> List[Item]:
    """
    Get items by category.

    Args:
        db: Database session
        category: Category name (men/women/kids)

    Returns:
        List of items in category
    """
    return db.query(Item).filter(Item.category == category).all()


def search_items(db: Session, query: str) -> List[Item]:
    """
    Search items by name or description.

    Args:
        db: Database session
        query: Search query

    Returns:
        List of matching items
    """
    search_term = f"%{query}%"
    return db.query(Item).filter(
        (Item.name.ilike(search_term)) |
        (Item.description.ilike(search_term))
    ).all()


def get_item_stats(db: Session) -> Dict:
    """
    Get product statistics.

    Args:
        db: Database session

    Returns:
        Dictionary with statistics
    """
    total_items = db.query(Item).count()

    categories = db.query(Item.category).distinct().all()
    category_counts = {}

    for category in categories:
        if category[0]:  # category is a tuple
            count = db.query(Item).filter(Item.category == category[0]).count()
            category_counts[category[0]] = count

    # Price statistics
    result = db.query(
        db.func.min(Item.price).label('min_price'),
        db.func.max(Item.price).label('max_price'),
        db.func.avg(Item.price).label('avg_price')
    ).first()

    return {
        'total_items': total_items,
        'categories': category_counts,
        'price_min': result.min_price or 0,
        'price_max': result.max_price or 0,
        'price_avg': float(result.avg_price or 0)
    }