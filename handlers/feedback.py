"""
Feedback handlers for collecting user feedback.
"""
import logging
from datetime import datetime
from telebot import TeleBot, types

from models.db import get_db_session
from models.schemas import User, Feedback
from utils.locales import MSG
from config import Config

logger = logging.getLogger(__name__)


def start_feedback(message: types.Message, bot: TeleBot):
    """Start feedback collection."""
    bot.send_message(
        message.chat.id,
        MSG.FEEDBACK_PROMPT
    )

    bot.register_next_step_handler(message, process_feedback, bot)


def process_feedback(message: types.Message, bot: TeleBot):
    """Process user feedback."""
    feedback_text = message.text.strip()

    if not feedback_text or len(feedback_text) < 5:
        bot.send_message(message.chat.id, "❌ Відгук занадто короткий. Будь ласка, напишіть щонайменше 5 символів.")
        bot.register_next_step_handler(message, process_feedback, bot)
        return

    db = get_db_session()

    try:
        user = db.query(User).filter(User.tg_id == message.from_user.id).first()

        if not user:
            # Create user if not exists
            user = User(
                tg_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language="uk"
            )
            db.add(user)
            db.flush()

        # Save feedback
        feedback = Feedback(
            user_id=user.id,
            text=feedback_text
        )

        db.add(feedback)
        db.commit()

        logger.info(f"Feedback from user {user.tg_id}: {feedback_text[:50]}...")

        # Send confirmation to user
        bot.send_message(
            message.chat.id,
            MSG.FEEDBACK_THANKS
        )

        # Notify admins
        notify_admins_feedback(user, feedback_text, bot)

    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        bot.send_message(message.chat.id, MSG.ERROR_GENERAL)

    finally:
        db.close()


def notify_admins_feedback(user: User, feedback_text: str, bot: TeleBot):
    """Notify admins about new feedback."""
    text = MSG.ADMIN_FEEDBACK.format(
        user_name=f"{user.first_name or ''} {user.last_name or ''}".strip(),
        username=user.username or "немає",
        tg_id=user.tg_id,
        text=feedback_text,
        created_at=datetime.now().strftime("%d.%m.%Y %H:%M")
    )

    for admin_id in Config.ADMIN_IDS:
        try:
            bot.send_message(admin_id, text)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id} about feedback: {e}")


def register_feedback_handlers(bot: TeleBot):
    """Register feedback handlers."""

    @bot.message_handler(commands=['feedback'])
    def feedback_wrapper(message):
        start_feedback(message, bot)