"""
Promo code handlers for users.
"""
import logging
from telebot import TeleBot, types

from models.db import get_db_session
from models.schemas import PromoCode
from utils.locales import MSG
from utils.keyboards import create_main_keyboard

logger = logging.getLogger(__name__)


def show_promo_codes(message: types.Message, bot: TeleBot):
    """Show active promo codes to users."""
    db = get_db_session()

    try:
        # Get all active promo codes
        promos = db.query(PromoCode).filter(
            PromoCode.is_active == True
        ).order_by(PromoCode.discount_percent.desc()).all()

        if not promos:
            bot.send_message(
                message.chat.id,
                "🎟️ Наразі активних промокодів немає.\n"
                "Слідкуйте за нашими акціями!"
            )
            return

        # Format promo codes list
        promo_text = "🎟️ **Активні промокоди:**\n\n"

        for promo in promos:
            # Check if promo is still valid
            if not promo.is_valid():
                continue

            promo_text += f"**{promo.code}** - {promo.discount_percent:.0f}% знижки\n"

            if promo.valid_until:
                from datetime import datetime
                valid_str = promo.valid_until.strftime("%d.%m.%Y")
                promo_text += f"⏰ Діє до: {valid_str}\n"

            if promo.usage_limit:
                remaining = promo.usage_limit - promo.usage_count
                if remaining > 0:
                    promo_text += f"📊 Залишилося: {remaining} використань\n"

            promo_text += "\n"

        promo_text += "\n💡 **Як використати промокод?**\n"
        promo_text += "1. Додайте товар в кошик\n"
        promo_text += "2. На етапі підтвердження замовлення\n"
        promo_text += "3. Введіть код промокоду\n"
        promo_text += "4. Знижка буде застосована автоматично!"

        bot.send_message(
            message.chat.id,
            promo_text,
            reply_markup=create_main_keyboard(),
            parse_mode="Markdown"
        )

        logger.info(f"User {message.from_user.id} viewed promo codes")

    except Exception as e:
        logger.error(f"Error showing promo codes: {e}")
        bot.send_message(message.chat.id, MSG.ERROR_GENERAL)

    finally:
        db.close()


def register_promo_handlers(bot: TeleBot):
    """Register promo code handlers."""

    @bot.message_handler(commands=['promo', 'promocodes', 'промокоды', 'промокоди', 'скидки', 'знижки'])
    def promo_wrapper(message):
        show_promo_codes(message, bot)

    # Add to command synonyms
    from utils.command_matcher import COMMAND_SYNONYMS
    COMMAND_SYNONYMS['🎟️ Промокоди'].extend([
        'promo', 'promocodes', 'промокоды', 'промокоди',
        'скидки', 'знижки', 'discounts', 'акции', 'акції'
    ])