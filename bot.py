"""
YourShoes Telegram Bot - Main Entry Point
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import telebot

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models.db import init_db
from utils.locales import MSG

# Configure logging
os.makedirs("logs", exist_ok=True)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

file_handler = RotatingFileHandler(
    Config.LOG_FILE,
    maxBytes=Config.LOG_MAX_BYTES,
    backupCount=Config.LOG_BACKUP_COUNT
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(Config.BOT_TOKEN, parse_mode="HTML")


def seed_database_if_empty():
    """Seed database with sample data if empty."""
    from models.db import get_db_session
    from models.schemas import Item
    from seed_data import seed_extensive_data

    db = get_db_session()

    try:
        # Check if we should seed - if less than 5 items
        item_count = db.query(Item).count()

        if item_count < 5:
            logger.info(f"Database has only {item_count} items, seeding...")
            items_added, promos_added = seed_extensive_data(db)
            logger.info(f"Database seeded with {items_added} items and {promos_added} promo codes")
        else:
            logger.info(f"Database already contains {item_count} items, skipping seed")

            # Still try to add any missing items/promos (but don't log as seeding)
            try:
                items_added, promos_added = seed_extensive_data(db)
                if items_added > 0 or promos_added > 0:
                    logger.info(f"Added missing data: {items_added} items, {promos_added} promos")
            except Exception as e:
                logger.warning(f"Could not add missing data: {e}")

    except Exception as e:
        logger.error(f"Error in seed_database_if_empty: {e}")
        # Don't rollback, just log the error - database should still work

    finally:
        db.close()


def register_handlers():
    """Register all handlers in correct order."""
    logger.info("Registering handlers...")

    # Import handlers here to avoid circular imports
    from handlers.start import register_start_handlers
    from handlers.catalog import register_catalog_handlers
    from handlers.orders import register_order_handlers
    from handlers.admin import register_admin_handlers
    from handlers.feedback import register_feedback_handlers
    from handlers.promo import register_promo_handlers

    # Register command handlers first
    register_start_handlers(bot)
    register_catalog_handlers(bot)
    register_order_handlers(bot)
    register_admin_handlers(bot)
    register_feedback_handlers(bot)
    register_promo_handlers(bot)

    # Register catch-all handler LAST
    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def catch_all(message):
        """Catch-all handler for unrecognized messages."""
        try:
            # Only respond to commands
            if message.text and message.text.startswith('/'):
                bot.reply_to(
                    message,
                    "❓ Не розумію цю команду. Використайте /help для списку команд."
                )
            # For non-command messages, you can optionally send a help message
            elif message.text and message.text.strip():
                bot.reply_to(
                    message,
                    "ℹ️ Я розумію лише команди. Напишіть /help щоб побачити список команд."
                )
        except Exception as e:
            logger.error(f"Error in catch_all handler: {e}")

    logger.info("All handlers registered")


def main():
    """Main bot entry point."""
    logger.info("="*50)
    logger.info("Starting YourShoes Telegram Bot")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")

        # Seed database if empty
        seed_database_if_empty()

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    # Get bot info
    try:
        bot_info = bot.get_me()
        logger.info(f"Bot username: @{bot_info.username}")
        logger.info(f"Bot ID: {bot_info.id}")
    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
        sys.exit(1)

    logger.info(f"Admins configured: {len(Config.ADMIN_IDS)}")
    logger.info(f"Database: {Config.DB_URL}")
    logger.info("="*50)

    # Register all handlers
    register_handlers()

    # Start polling
    try:
        logger.info("Starting polling mode...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        logger.error(f"Polling error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)