"""
Handlers for catalog browsing and product viewing.
"""
import logging
from telebot import TeleBot, types

from models.db import get_db_session
from models.schemas import Item
from utils.locales import MSG
from utils.keyboards import create_catalog_keyboard, create_product_keyboard
from config import Config

logger = logging.getLogger(__name__)


def show_catalog(message: types.Message, bot: TeleBot, page: int = 0):
    """Show catalog of products."""
    db = get_db_session()
    
    try:
        items = db.query(Item).all()
        
        if not items:
            bot.send_message(message.chat.id, MSG.CATALOG_EMPTY)
            return
        
        logger.info(f"User {message.from_user.id} viewing catalog (page {page})")
        
        keyboard = create_catalog_keyboard(items, page, Config.ITEMS_PER_PAGE)
        
        bot.send_message(
            message.chat.id,
            MSG.CATALOG_HEADER,
            reply_markup=keyboard
        )
    
    finally:
        db.close()


def show_product_details(call: types.CallbackQuery, bot: TeleBot):
    """Show detailed product information."""
    item_id = int(call.data.split(":")[1])
    db = get_db_session()
    
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        
        if not item:
            bot.answer_callback_query(call.id, MSG.ERROR_PRODUCT_NOT_FOUND)
            return
        
        logger.info(f"User {call.from_user.id} viewing product {item.id}")
        
        # Format product details
        sizes_str = ", ".join(item.get_sizes())
        
        text = MSG.PRODUCT_DETAILS.format(
            name=item.name,
            price=f"{item.price:.2f}",
            sizes=sizes_str,
            description=item.description or "Немає опису"
        )
        
        keyboard = create_product_keyboard(item.id)
        
        # Send with image if available
        first_image = item.get_first_image()
        
        if first_image:
            try:
                bot.send_photo(
                    call.message.chat.id,
                    first_image,
                    caption=text,
                    reply_markup=keyboard
                )
            except Exception as e:
                logger.warning(f"Failed to send image: {e}")
                # Fallback to text only
                bot.send_message(
                    call.message.chat.id,
                    text,
                    reply_markup=keyboard
                )
        else:
            bot.send_message(
                call.message.chat.id,
                text,
                reply_markup=keyboard
            )
        
        # Delete the catalog message
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        bot.answer_callback_query(call.id)
    
    finally:
        db.close()


def handle_back_to_catalog(call: types.CallbackQuery, bot: TeleBot):
    """Handle back to catalog button."""
    # Delete current message
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    # Create a fake message to reuse show_catalog
    fake_message = types.Message(
        message_id=0,
        from_user=call.from_user,
        date=0,
        chat=call.message.chat,
        content_type='text',
        options={},
        json_string='{}'
    )
    
    show_catalog(fake_message, bot)
    bot.answer_callback_query(call.id)


def handle_catalog_pagination(call: types.CallbackQuery, bot: TeleBot):
    """Handle catalog page navigation."""
    page = int(call.data.split(":")[1])
    
    db = get_db_session()
    
    try:
        items = db.query(Item).all()
        keyboard = create_catalog_keyboard(items, page, Config.ITEMS_PER_PAGE)
        
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
        
        bot.answer_callback_query(call.id)
    
    finally:
        db.close()


def register_catalog_handlers(bot: TeleBot):
    """Register all catalog-related handlers."""
    
    @bot.message_handler(commands=['catalog'])
    def catalog_wrapper(message):
        show_catalog(message, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("item:"))
    def product_details_wrapper(call):
        show_product_details(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_catalog")
    def back_to_catalog_wrapper(call):
        handle_back_to_catalog(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("catalog_page:"))
    def catalog_page_wrapper(call):
        handle_catalog_pagination(call, bot)