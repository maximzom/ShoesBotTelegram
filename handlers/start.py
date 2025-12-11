"""
Handlers for basic commands: /start, /help, /info, /hello
"""
import logging
from telebot import TeleBot, types

from models.db import get_db_session
from models.schemas import User
from utils.locales import MSG
from utils.keyboards import create_main_keyboard

logger = logging.getLogger(__name__)


def get_or_create_user(message: types.Message) -> User:
    """Get or create user from message."""
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
            db.refresh(user)
            logger.info(f"New user created: {user.tg_id} ({user.first_name})")
        else:
            # Update user info if changed
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
                db.refresh(user)

        # Возвращаем объект с сессией
        return user
    except Exception as e:
        logger.error(f"Error getting/creating user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def handle_start(message: types.Message, bot: TeleBot):
    """Handle /start command."""
    try:
        user = get_or_create_user(message)

        # Используем message.from_user.id вместо user.tg_id для избежания detached instance
        logger.info(f"User {message.from_user.id} started bot")

        # Send welcome message with main keyboard
        bot.send_message(
            message.chat.id,
            MSG.START,
            reply_markup=create_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in handle_start: {e}")
        # Отправляем сообщение даже если есть ошибка с пользователем
        bot.send_message(
            message.chat.id,
            MSG.START,
            reply_markup=create_main_keyboard()
        )


def handle_help(message: types.Message, bot: TeleBot):
    """Handle /help command."""
    logger.info(f"User {message.from_user.id} requested help")
    
    bot.send_message(
        message.chat.id,
        MSG.HELP
    )


def handle_info(message: types.Message, bot: TeleBot):
    """Handle /info command."""
    logger.info(f"User {message.from_user.id} requested info")
    
    bot.send_message(
        message.chat.id,
        MSG.INFO
    )


def handle_hello(message: types.Message, bot: TeleBot):
    """Handle /hello command."""
    logger.info(f"User {message.from_user.id} said hello")
    
    bot.send_message(
        message.chat.id,
        MSG.HELLO
    )


def handle_main_menu_buttons(message: types.Message, bot: TeleBot):
    """Handle main menu reply keyboard buttons."""
    text = message.text
    
    if text == MSG.BTN_CATALOG:
        # Redirect to catalog handler
        from handlers.catalog import show_catalog
        show_catalog(message, bot)
    
    elif text == MSG.BTN_MY_ORDERS:
        # Redirect to orders handler
        from handlers.orders import show_my_orders
        show_my_orders(message, bot)
    
    elif text == MSG.BTN_INFO:
        handle_info(message, bot)
    
    elif text == MSG.BTN_CONTACT:
        # Show feedback prompt
        from handlers.feedback import start_feedback
        start_feedback(message, bot)


def register_start_handlers(bot: TeleBot):
    """Register all start-related handlers."""
    
    @bot.message_handler(commands=['start'])
    def start_wrapper(message):
        handle_start(message, bot)
    
    @bot.message_handler(commands=['help'])
    def help_wrapper(message):
        handle_help(message, bot)
    
    @bot.message_handler(commands=['info'])
    def info_wrapper(message):
        handle_info(message, bot)
    
    @bot.message_handler(commands=['hello'])
    def hello_wrapper(message):
        handle_hello(message, bot)
    
    # Handle main menu buttons
    @bot.message_handler(func=lambda m: m.text in [
        MSG.BTN_CATALOG, MSG.BTN_MY_ORDERS, MSG.BTN_INFO, MSG.BTN_CONTACT
    ])
    def menu_buttons_wrapper(message):
        handle_main_menu_buttons(message, bot)