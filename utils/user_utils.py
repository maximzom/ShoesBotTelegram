"""
User utilities for safe database operations.
"""
import logging
from typing import Optional, Dict, Any
from telebot import types
from sqlalchemy.orm import Session

from models.db import get_db_session
from models.schemas import User

logger = logging.getLogger(__name__)


def get_user_safe(tg_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user data safely without returning SQLAlchemy object.

    Args:
        tg_id: Telegram user ID

    Returns:
        Dictionary with user data or None
    """
    db = get_db_session()

    try:
        user = db.query(User).filter(User.tg_id == tg_id).first()

        if not user:
            return None

        return {
            'id': user.id,
            'tg_id': user.tg_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'language': user.language
        }

    except Exception as e:
        logger.error(f"Error getting user {tg_id}: {e}")
        return None

    finally:
        db.close()


def create_or_update_user_safe(message: types.Message) -> Dict[str, Any]:
    """
    Create or update user safely.

    Args:
        message: Telegram message

    Returns:
        Dictionary with user data
    """
    db = get_db_session()

    try:
        user = db.query(User).filter(User.tg_id == message.from_user.id).first()

        if not user:
            user = User(
                tg_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language="uk"
            )
            db.add(user)
            db.commit()
            logger.info(f"New user created: {user.tg_id}")
        else:
            updated = False

            if user.username != message.from_user.username:
                user.username = message.from_user.username
                updated = True

            if user.first_name != message.from_user.first_name:
                user.first_name = message.from_user.first_name
                updated = True

            if user.last_name != message.from_user.last_name:
                user.last_name = message.from_user.last_name
                updated = True

            if updated:
                db.commit()

        return {
            'id': user.id,
            'tg_id': user.tg_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }

    except Exception as e:
        logger.error(f"Error creating/updating user: {e}")
        db.rollback()

        return {
            'tg_id': message.from_user.id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }

    finally:
        db.close()