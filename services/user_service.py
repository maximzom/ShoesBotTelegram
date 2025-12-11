"""
Business logic for user management.
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.schemas import User, Order, Feedback
from utils.validators import validate_phone, mask_phone

logger = logging.getLogger(__name__)


def create_or_update_user(
        db: Session,
        tg_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        language: str = "uk"
) -> User:
    """
    Create new user or update existing.

    Args:
        db: Database session
        tg_id: Telegram user ID
        username: Telegram username
        first_name: First name
        last_name: Last name
        phone: Phone number
        language: Language code

    Returns:
        User object
    """
    user = db.query(User).filter(User.tg_id == tg_id).first()

    if user:
        # Update existing user
        updated = False

        if username != user.username:
            user.username = username
            updated = True

        if first_name != user.first_name:
            user.first_name = first_name
            updated = True

        if last_name != user.last_name:
            user.last_name = last_name
            updated = True

        if phone and validate_phone(phone):
            user.phone = phone
            updated = True

        if language and language != user.language:
            user.language = language
            updated = True

        if updated:
            db.commit()
            db.refresh(user)
            logger.info(f"User updated: {user.tg_id}")

    else:
        # Create new user
        user = User(
            tg_id=tg_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone if phone and validate_phone(phone) else None,
            language=language
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user created: {user.tg_id}")

    return user


def update_user_phone(db: Session, tg_id: int, phone: str) -> bool:
    """
    Update user phone number.

    Args:
        db: Database session
        tg_id: Telegram user ID
        phone: Phone number

    Returns:
        True if updated, False otherwise
    """
    if not validate_phone(phone):
        logger.error(f"Invalid phone number: {phone}")
        return False

    user = db.query(User).filter(User.tg_id == tg_id).first()

    if not user:
        logger.error(f"User not found: {tg_id}")
        return False

    user.phone = phone
    db.commit()

    logger.info(f"Phone updated for user: {tg_id}")
    return True


def update_user_language(db: Session, tg_id: int, language: str) -> bool:
    """
    Update user language preference.

    Args:
        db: Database session
        tg_id: Telegram user ID
        language: Language code

    Returns:
        True if updated, False otherwise
    """
    user = db.query(User).filter(User.tg_id == tg_id).first()

    if not user:
        logger.error(f"User not found: {tg_id}")
        return False

    user.language = language
    db.commit()

    logger.info(f"Language updated for user {tg_id}: {language}")
    return True


def get_user_stats(db: Session, tg_id: int) -> Optional[Dict]:
    """
    Get user statistics.

    Args:
        db: Database session
        tg_id: Telegram user ID

    Returns:
        Dictionary with user statistics or None
    """
    user = db.query(User).filter(User.tg_id == tg_id).first()

    if not user:
        return None

    # Count orders
    total_orders = db.query(Order).filter(Order.user_id == user.id).count()

    # Count orders by status
    pending_orders = db.query(Order).filter(
        Order.user_id == user.id,
        Order.status == 'pending'
    ).count()

    completed_orders = db.query(Order).filter(
        Order.user_id == user.id,
        Order.status.in_(['confirmed', 'shipped'])
    ).count()

    # Total spent
    total_spent_result = db.query(
        func.sum(Order.total)
    ).filter(
        Order.user_id == user.id,
        Order.status.in_(['confirmed', 'shipped', 'paid'])
    ).first()

    total_spent = float(total_spent_result[0] or 0)

    # Feedback count
    feedback_count = db.query(Feedback).filter(Feedback.user_id == user.id).count()

    return {
        'user_id': user.id,
        'tg_id': user.tg_id,
        'username': user.username,
        'name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_spent': total_spent,
        'feedback_count': feedback_count,
        'created_at': user.created_at.strftime("%d.%m.%Y"),
        'phone': mask_phone(user.phone) if user.phone else "Не вказано"
    }


def get_all_users(db: Session, limit: int = 100) -> List[User]:
    """
    Get all users (admin function).

    Args:
        db: Database session
        limit: Maximum users to return

    Returns:
        List of users
    """
    return db.query(User).order_by(User.created_at.desc()).limit(limit).all()


def get_active_users(db: Session, days: int = 30) -> List[User]:
    """
    Get users active in last N days.

    Args:
        db: Database session
        days: Number of days to look back

    Returns:
        List of active users
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Users who placed orders in last N days
    return db.query(User).join(Order).filter(
        Order.created_at >= cutoff_date
    ).distinct().all()


def delete_user(db: Session, tg_id: int) -> bool:
    """
    Delete user (admin function).

    Args:
        db: Database session
        tg_id: Telegram user ID

    Returns:
        True if deleted, False otherwise
    """
    user = db.query(User).filter(User.tg_id == tg_id).first()

    if not user:
        logger.error(f"User not found for deletion: {tg_id}")
        return False

    db.delete(user)
    db.commit()

    logger.info(f"User deleted: {tg_id}")
    return True