"""
Promo code management service.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from models.schemas import PromoCode
from utils.validators import validate_promo_discount

logger = logging.getLogger(__name__)


def create_promo_code(
        db: Session,
        code: str,
        discount_percent: float,
        valid_days: Optional[int] = None,
        usage_limit: Optional[int] = None,
        is_active: bool = True
) -> Optional[PromoCode]:
    """
    Create a new promo code.

    Args:
        db: Database session
        code: Promo code (case insensitive)
        discount_percent: Discount percentage (1-100)
        valid_days: Number of days code is valid (optional)
        usage_limit: Maximum number of uses (optional)
        is_active: Whether code is active

    Returns:
        Created PromoCode object or None
    """
    # Validate discount
    if not validate_promo_discount(str(discount_percent)):
        logger.error(f"Invalid discount percentage: {discount_percent}")
        return None

    # Check if code already exists
    existing = db.query(PromoCode).filter(PromoCode.code == code.upper()).first()
    if existing:
        logger.error(f"Promo code already exists: {code}")
        return None

    # Calculate expiry date
    valid_until = None
    if valid_days:
        valid_until = datetime.utcnow() + timedelta(days=valid_days)

    # Create promo code
    promo = PromoCode(
        code=code.upper(),
        discount_percent=discount_percent,
        valid_until=valid_until,
        usage_limit=usage_limit,
        is_active=is_active
    )

    db.add(promo)
    db.commit()
    db.refresh(promo)

    logger.info(f"Promo code created: {promo.code} ({discount_percent}%)")

    return promo


def validate_promo_code(db: Session, code: str) -> Optional[PromoCode]:
    """
    Validate promo code and return if valid.

    Args:
        db: Database session
        code: Promo code to validate

    Returns:
        Valid PromoCode object or None
    """
    promo = db.query(PromoCode).filter(PromoCode.code == code.upper()).first()

    if not promo:
        logger.warning(f"Promo code not found: {code}")
        return None

    if not promo.is_valid():
        logger.warning(f"Promo code invalid: {code}")
        return None

    return promo


def apply_promo_code(
        db: Session,
        code: str,
        subtotal: float
) -> Dict[str, any]:
    """
    Apply promo code to order subtotal.

    Args:
        db: Database session
        code: Promo code to apply
        subtotal: Order subtotal

    Returns:
        Dictionary with discount details
    """
    promo = validate_promo_code(db, code)

    if not promo:
        return {
            'valid': False,
            'discount_amount': 0.0,
            'discount_percent': 0.0,
            'total': subtotal,
            'message': 'Промокод недійсний'
        }

    # Calculate discount
    discount_amount = subtotal * (promo.discount_percent / 100)
    total = subtotal - discount_amount

    # Increment usage count (but don't commit yet - commit when order is created)
    promo.usage_count += 1

    return {
        'valid': True,
        'discount_amount': round(discount_amount, 2),
        'discount_percent': promo.discount_percent,
        'total': round(total, 2),
        'message': f"Промокод застосовано! Знижка: {promo.discount_percent}%"
    }


def get_all_promo_codes(db: Session, active_only: bool = False) -> List[PromoCode]:
    """
    Get all promo codes.

    Args:
        db: Database session
        active_only: Only return active codes

    Returns:
        List of promo codes
    """
    query = db.query(PromoCode)

    if active_only:
        query = query.filter(PromoCode.is_active == True)

    return query.order_by(PromoCode.created_at.desc()).all()


def update_promo_code(
        db: Session,
        code: str,
        **kwargs
) -> Optional[PromoCode]:
    """
    Update promo code.

    Args:
        db: Database session
        code: Promo code to update
        **kwargs: Fields to update

    Returns:
        Updated PromoCode object or None
    """
    promo = db.query(PromoCode).filter(PromoCode.code == code.upper()).first()

    if not promo:
        logger.error(f"Promo code not found: {code}")
        return None

    # Update fields
    if 'discount_percent' in kwargs:
        discount = kwargs['discount_percent']
        if validate_promo_discount(str(discount)):
            promo.discount_percent = discount
        else:
            logger.error(f"Invalid discount: {discount}")
            return None

    if 'valid_until' in kwargs:
        promo.valid_until = kwargs['valid_until']

    if 'usage_limit' in kwargs:
        promo.usage_limit = kwargs['usage_limit']

    if 'is_active' in kwargs:
        promo.is_active = kwargs['is_active']

    db.commit()
    db.refresh(promo)

    logger.info(f"Promo code updated: {promo.code}")

    return promo


def deactivate_promo_code(db: Session, code: str) -> bool:
    """
    Deactivate promo code.

    Args:
        db: Database session
        code: Promo code to deactivate

    Returns:
        True if deactivated, False otherwise
    """
    promo = db.query(PromoCode).filter(PromoCode.code == code.upper()).first()

    if not promo:
        logger.error(f"Promo code not found: {code}")
        return False

    promo.is_active = False
    db.commit()

    logger.info(f"Promo code deactivated: {promo.code}")

    return True


def get_promo_stats(db: Session) -> Dict:
    """
    Get promo code statistics.

    Args:
        db: Database session

    Returns:
        Dictionary with statistics
    """
    total_codes = db.query(PromoCode).count()
    active_codes = db.query(PromoCode).filter(PromoCode.is_active == True).count()

    # Most used codes
    most_used = db.query(PromoCode).order_by(PromoCode.usage_count.desc()).limit(5).all()

    # Expired codes
    expired = db.query(PromoCode).filter(
        PromoCode.valid_until < datetime.utcnow(),
        PromoCode.is_active == True
    ).count()

    # Total discount given
    result = db.query(
        db.func.sum(PromoCode.usage_count * PromoCode.discount_percent / 100)
    ).first()

    # This is an approximation - would need actual order data for exact amount
    estimated_savings = float(result[0] or 0) * 1000  # Assuming average order of 1000 UAH

    return {
        'total_codes': total_codes,
        'active_codes': active_codes,
        'expired_codes': expired,
        'most_used': [
            {
                'code': p.code,
                'uses': p.usage_count,
                'discount': p.discount_percent
            }
            for p in most_used
        ],
        'estimated_savings': round(estimated_savings, 2)
    }