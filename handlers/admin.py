"""
Admin panel handlers for managing products and orders.
"""
import logging
from telebot import TeleBot, types
import datetime
import io
import csv
from sqlalchemy.orm import Session

from models.db import get_db_session
from models.schemas import User, Item, Order, PromoCode
from utils.locales import MSG
from utils.keyboards import (
    create_admin_keyboard,
    create_remove_item_keyboard,
    create_order_actions_keyboard,
    create_yes_no_keyboard
)
from utils.validators import validate_price, validate_sizes, validate_promo_discount, validate_sku
from services.order_service import update_order_status, get_all_orders
from config import Config

logger = logging.getLogger(__name__)

# Admin state for multi-step flows
admin_states = {}


def handle_admin_command(message: types.Message, bot: TeleBot):
    """Handle /admin command."""
    if not Config.is_admin(message.from_user.id):
        bot.send_message(message.chat.id, MSG.NOT_ADMIN)
        return

    logger.info(f"Admin {message.from_user.id} accessed admin panel")

    bot.send_message(
        message.chat.id,
        MSG.ADMIN_MENU,
        reply_markup=create_admin_keyboard()
    )


def handle_back_from_admin(message: types.Message, bot: TeleBot):
    """Handle back button from admin panel."""
    logger.info(f"User {message.from_user.id} returning from admin panel")

    bot.send_message(
        message.chat.id,
        MSG.START,
        reply_markup=create_main_keyboard()
    )

def start_add_item(message: types.Message, bot: TeleBot):
    """Start adding new item process."""
    if not Config.is_admin(message.from_user.id):
        return

    admin_states[message.from_user.id] = {
        'action': 'add_item',
        'step': 'name'
    }

    bot.send_message(message.chat.id, MSG.ADD_ITEM_NAME)
    bot.register_next_step_handler(message, process_item_name, bot)


def process_item_name(message: types.Message, bot: TeleBot):
    """Process item name."""
    user_id = message.from_user.id

    if user_id not in admin_states:
        return

    admin_states[user_id]['name'] = message.text.strip()
    admin_states[user_id]['step'] = 'sku'

    bot.send_message(message.chat.id, "🏷️ Введіть SKU (унікальний код товару):")
    bot.register_next_step_handler(message, process_item_sku, bot)


def process_item_sku(message: types.Message, bot: TeleBot):
    """Process item SKU."""
    user_id = message.from_user.id

    if user_id not in admin_states:
        return

    sku = message.text.strip().upper()

    if not validate_sku(sku):
        bot.send_message(message.chat.id,
                         "❌ Неправильний формат SKU. Використовуйте латинські літери, цифри, дефіси та підкреслення (3-50 символів)")
        bot.register_next_step_handler(message, process_item_sku, bot)
        return

    # Check if SKU exists
    db = get_db_session()
    try:
        existing = db.query(Item).filter(Item.sku == sku).first()
        if existing:
            bot.send_message(message.chat.id, "❌ Товар з таким SKU вже існує. Введіть інший SKU:")
            bot.register_next_step_handler(message, process_item_sku, bot)
            return
    finally:
        db.close()

    admin_states[user_id]['sku'] = sku
    admin_states[user_id]['step'] = 'price'

    bot.send_message(message.chat.id, MSG.ADD_ITEM_PRICE)
    bot.register_next_step_handler(message, process_item_price, bot)


def process_item_price(message: types.Message, bot: TeleBot):
    """Process item price."""
    user_id = message.from_user.id

    if user_id not in admin_states:
        return

    price = validate_price(message.text)

    if not price:
        bot.send_message(message.chat.id, MSG.INVALID_PRICE)
        bot.register_next_step_handler(message, process_item_price, bot)
        return

    admin_states[user_id]['price'] = price
    admin_states[user_id]['step'] = 'sizes'

    bot.send_message(message.chat.id, MSG.ADD_ITEM_SIZES)
    bot.register_next_step_handler(message, process_item_sizes, bot)


def process_item_sizes(message: types.Message, bot: TeleBot):
    """Process item sizes."""
    user_id = message.from_user.id

    if user_id not in admin_states:
        return

    sizes = validate_sizes(message.text)

    if not sizes:
        bot.send_message(message.chat.id, MSG.INVALID_SIZES)
        bot.register_next_step_handler(message, process_item_sizes, bot)
        return

    admin_states[user_id]['sizes'] = sizes
    admin_states[user_id]['step'] = 'description'

    bot.send_message(message.chat.id, MSG.ADD_ITEM_DESCRIPTION)
    bot.register_next_step_handler(message, process_item_description, bot)


def process_item_description(message: types.Message, bot: TeleBot):
    """Process item description."""
    user_id = message.from_user.id

    if user_id not in admin_states:
        return

    admin_states[user_id]['description'] = message.text.strip()
    admin_states[user_id]['step'] = 'category'

    bot.send_message(message.chat.id, "📂 Введіть категорію (men/women/kids або залиште порожнім):")
    bot.register_next_step_handler(message, process_item_category, bot)


def process_item_category(message: types.Message, bot: TeleBot):
    """Process item category."""
    user_id = message.from_user.id

    if user_id not in admin_states:
        return

    category = message.text.strip().lower()
    if category not in ['men', 'women', 'kids']:
        category = None

    admin_states[user_id]['category'] = category
    admin_states[user_id]['step'] = 'image'

    bot.send_message(message.chat.id, MSG.ADD_ITEM_IMAGE)
    bot.register_next_step_handler(message, process_item_image, bot)


def process_item_image(message: types.Message, bot: TeleBot):
    """Process item image."""
    user_id = message.from_user.id

    if user_id not in admin_states:
        return

    db = get_db_session()

    try:
        state = admin_states[user_id]

        # Create new item
        item = Item(
            sku=state['sku'],
            name=state['name'],
            price=state['price'],
            description=state['description'],
            category=state['category']
        )

        item.set_sizes(state['sizes'])

        # Handle image if provided
        if message.content_type == 'photo':
            # Get the best quality photo
            file_id = message.photo[-1].file_id
            item.set_images([file_id])

        db.add(item)
        db.commit()

        logger.info(f"Admin {user_id} added item: {item.sku}")

        bot.send_message(message.chat.id, MSG.ADD_ITEM_SUCCESS)

        # Clear state
        if user_id in admin_states:
            del admin_states[user_id]

    except Exception as e:
        logger.error(f"Error adding item: {e}")
        bot.send_message(message.chat.id, MSG.ERROR_GENERAL)

    finally:
        db.close()


def start_remove_item(message: types.Message, bot: TeleBot):
    """Start item removal process."""
    if not Config.is_admin(message.from_user.id):
        return

    db = get_db_session()

    try:
        items = db.query(Item).all()

        if not items:
            bot.send_message(message.chat.id, "📭 Каталог порожній.")
            return

        keyboard = create_remove_item_keyboard(items)

        bot.send_message(
            message.chat.id,
            MSG.REMOVE_ITEM_SELECT,
            reply_markup=keyboard
        )

    finally:
        db.close()


def handle_remove_item_selection(call: types.CallbackQuery, bot: TeleBot):
    """Handle item selection for removal."""
    item_id = int(call.data.split(":")[1])

    keyboard = create_yes_no_keyboard("remove_item", str(item_id))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=MSG.REMOVE_ITEM_CONFIRM,
        reply_markup=keyboard
    )

    bot.answer_callback_query(call.id)


def confirm_remove_item(call: types.CallbackQuery, bot: TeleBot):
    """Confirm and remove item."""
    item_id = int(call.data.split(":")[1])

    db = get_db_session()

    try:
        item = db.query(Item).filter(Item.id == item_id).first()

        if item:
            db.delete(item)
            db.commit()

            logger.info(f"Admin {call.from_user.id} removed item: {item.sku}")

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=MSG.REMOVE_ITEM_SUCCESS
            )
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=MSG.ERROR_PRODUCT_NOT_FOUND
            )

    except Exception as e:
        logger.error(f"Error removing item: {e}")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=MSG.ERROR_GENERAL
        )

    finally:
        db.close()

    bot.answer_callback_query(call.id)


def cancel_remove_item(call: types.CallbackQuery, bot: TeleBot):
    """Cancel item removal."""
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=MSG.REMOVE_ITEM_CANCELLED
    )

    bot.answer_callback_query(call.id)


def show_all_orders(message: types.Message, bot: TeleBot):
    """Show all orders (admin)."""
    if not Config.is_admin(message.from_user.id):
        bot.send_message(message.chat.id, MSG.NOT_ADMIN)
        return

    db = get_db_session()

    try:
        # Determine if this is from button or command
        is_from_button = False
        status = None

        # Check if message starts with command
        if message.text.startswith('/'):
            # It's a command, parse arguments
            parts = message.text.split()
            if len(parts) > 1:
                status = parts[1]
        else:
            # It's from a button, check which button
            is_from_button = True
            button_text = message.text.strip()

            # Check if it's the "Перегляд замовлень" button
            if button_text in [MSG.BTN_ADMIN_ORDERS, "Перегляд замовлень", "Перегляд"]:
                # Show all orders without filter
                status = None
            else:
                # Could be some other button, ignore status
                status = None

        logger.info(
            f"Admin {message.from_user.id} viewing orders, status filter: {status}, from button: {is_from_button}")

        # Get orders
        from services.order_service import get_all_orders
        orders = get_all_orders(db, status)

        if not orders:
            bot.send_message(message.chat.id, MSG.ORDERS_EMPTY)
            return

        logger.info(f"Found {len(orders)} orders")

        # Show orders
        orders_shown = 0
        for order in orders:
            if orders_shown >= 10:  # Limit to 10
                break

            try:
                # Create a simple order display
                text = create_order_display_text(order, db)

                keyboard = create_order_actions_keyboard(order.id, order.status)

                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )

                orders_shown += 1

            except Exception as e:
                logger.error(f"Error displaying order {order.id}: {e}")
                continue

        # If there are more orders
        if len(orders) > 10:
            bot.send_message(
                message.chat.id,
                f"📊 Показано 10 з {len(orders)} замовлень.\n"
                f"Використайте /orders <статус> для фільтрації.\n"
                f"Статуси: pending, confirmed, paid, shipped, cancelled"
            )

    except Exception as e:
        logger.error(f"Error in show_all_orders: {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Помилка: {str(e)}")

    finally:
        db.close()


def create_order_display_text(order, db) -> str:
    """Create formatted text for order display."""
    # Get user info
    user = db.query(User).filter(User.id == order.user_id).first()
    user_name = "Без імені"
    if user:
        name_parts = []
        if user.first_name:
            name_parts.append(user.first_name)
        if user.last_name:
            name_parts.append(user.last_name)
        user_name = " ".join(name_parts).strip()
        if not user_name and user.username:
            user_name = f"@{user.username}"

    # Get order items
    from models.schemas import OrderItem, Item
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    items_text_lines = []
    for oi in order_items:
        item = db.query(Item).filter(Item.id == oi.item_id).first()
        if item:
            items_text_lines.append(
                f"• {item.name} (розмір {oi.size}) x {oi.quantity} = {oi.price * oi.quantity:.2f} грн")
        else:
            items_text_lines.append(
                f"• Товар #{oi.item_id} (розмір {oi.size}) x {oi.quantity} = {oi.price * oi.quantity:.2f} грн")

    items_text = "\n".join(items_text_lines)

    # Delivery info
    delivery_text = "Самовивіз (безкоштовно)"
    if order.delivery_method == "delivery":
        delivery_text = f"Доставка ({Config.DELIVERY_PRICE / 100:.2f} грн)"

    # Address
    address = order.address or "Самовивіз"

    # Format the message
    text = f"""📦 **Замовлення #{order.order_number}**

👤 **Клієнт:** {user_name}
📞 **Телефон:** {order.phone or 'Не вказано'}
📍 **Адреса:** {address}

🛍️ **Товари:**
{items_text}

💰 **Сума:** {order.total:.2f} грн
🎟️ **Знижка:** {order.discount:.2f} грн
🚚 **Доставка:** {delivery_text}
📊 **Статус:** {order.status}
⏰ **Створено:** {order.created_at.strftime('%d.%m.%Y %H:%M')}
"""

    return text

def handle_order_status_update(call: types.CallbackQuery, bot: TeleBot):
    """Handle order status update."""
    _, order_id, new_status = call.data.split(":")
    order_id = int(order_id)

    db = get_db_session()

    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if order:
            update_order_status(order, new_status, db)

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ Статус замовлення #{order.order_number} змінено на: {new_status}"
            )
        else:
            bot.answer_callback_query(call.id, MSG.ERROR_ORDER_NOT_FOUND)

    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        bot.answer_callback_query(call.id, MSG.ERROR_GENERAL)

    finally:
        db.close()


def start_add_promo(message: types.Message, bot: TeleBot):
    """Start adding promo code process."""
    if not Config.is_admin(message.from_user.id):
        return

    admin_states[message.from_user.id] = {
        'action': 'add_promo',
        'step': 'code'
    }

    bot.send_message(message.chat.id, MSG.PROMO_ADD_CODE)
    bot.register_next_step_handler(message, process_promo_code, bot)


def process_promo_code(message: types.Message, bot: TeleBot):
    """Process promo code."""
    user_id = message.from_user.id

    if user_id not in admin_states:
        return

    code = message.text.strip().upper()

    # Check if code exists
    db = get_db_session()
    try:
        existing = db.query(PromoCode).filter(PromoCode.code == code).first()
        if existing:
            bot.send_message(message.chat.id, "❌ Промокод з таким кодом вже існує. Введіть інший код:")
            bot.register_next_step_handler(message, process_promo_code, bot)
            return
    finally:
        db.close()

    admin_states[user_id]['code'] = code
    admin_states[user_id]['step'] = 'discount'

    bot.send_message(message.chat.id, MSG.PROMO_ADD_DISCOUNT)
    bot.register_next_step_handler(message, process_promo_discount, bot)


def process_promo_discount(message: types.Message, bot: TeleBot):
    """Process promo discount."""
    user_id = message.from_user.id

    if user_id not in admin_states:
        return

    discount = validate_promo_discount(message.text)

    if not discount:
        bot.send_message(message.chat.id, "❌ Неправильний відсоток знижки. Введіть число від 1 до 100:")
        bot.register_next_step_handler(message, process_promo_discount, bot)
        return

    admin_states[user_id]['discount'] = discount

    # Create promo code
    db = get_db_session()

    try:
        promo = PromoCode(
            code=admin_states[user_id]['code'],
            discount_percent=discount,
            is_active=True
        )

        db.add(promo)
        db.commit()

        logger.info(f"Admin {user_id} added promo code: {promo.code}")

        bot.send_message(message.chat.id, MSG.PROMO_ADD_SUCCESS)

        # Clear state
        if user_id in admin_states:
            del admin_states[user_id]

    except Exception as e:
        logger.error(f"Error adding promo code: {e}")
        bot.send_message(message.chat.id, MSG.ERROR_GENERAL)

    finally:
        db.close()


def register_admin_handlers(bot: TeleBot):
    """Register all admin handlers."""

    @bot.message_handler(commands=['admin'])
    def admin_wrapper(message):
        handle_admin_command(message, bot)

    @bot.message_handler(commands=['add_item'])
    def add_item_wrapper(message):
        start_add_item(message, bot)

    @bot.message_handler(commands=['remove_item'])
    def remove_item_wrapper(message):
        start_remove_item(message, bot)

    @bot.message_handler(commands=['orders', 'orderlist', 'замовлення'])
    def orders_wrapper(message):
        show_all_orders(message, bot)

    @bot.message_handler(commands=['promo_add'])
    def promo_add_wrapper(message):
        start_add_promo(message, bot)

    @bot.message_handler(commands=['export_orders'])
    def export_orders_wrapper(message):
        export_orders_command(message, bot)

    @bot.message_handler(func=lambda m: m.text == MSG.BTN_ADMIN_ADD)
    def admin_add_wrapper(message):
        start_add_item(message, bot)

    @bot.message_handler(func=lambda m: m.text == MSG.BTN_ADMIN_REMOVE)
    def admin_remove_wrapper(message):
        start_remove_item(message, bot)

    @bot.message_handler(func=lambda m: m.text == MSG.BTN_ADMIN_ORDERS)
    def admin_orders_wrapper(message):
        show_all_orders(message, bot)

    @bot.message_handler(func=lambda m: m.text == MSG.BTN_ADMIN_PROMO)
    def admin_promo_wrapper(message):
        start_add_promo(message, bot)

    @bot.message_handler(func=lambda m: m.text == MSG.BTN_BACK)
    def back_wrapper(message):
        from utils.keyboards import create_main_keyboard
        logger.info(f"User {message.from_user.id} pressed back button")

        bot.send_message(
            message.chat.id,
            MSG.START,
            reply_markup=create_main_keyboard()
        )

    @bot.message_handler(commands=['export_orders', 'export', 'експорт'])
    def export_orders_wrapper(message):
        export_orders_command(message, bot)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("remove_item:"))
    def remove_item_selection_wrapper(call):
        handle_remove_item_selection(call, bot)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("remove_item_yes:"))
    def confirm_remove_wrapper(call):
        confirm_remove_item(call, bot)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("remove_item_no:"))
    def cancel_remove_wrapper(call):
        cancel_remove_item(call, bot)

    @bot.callback_query_handler(func=lambda call: call.data == "cancel_remove")
    def cancel_remove_simple_wrapper(call):
        cancel_remove_item(call, bot)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("order_status:"))
    def order_status_wrapper(call):
        handle_order_status_update(call, bot)

def export_orders_command(message: types.Message, bot: TeleBot):
    """Export orders to CSV file."""
    if not Config.is_admin(message.from_user.id):
        bot.send_message(message.chat.id, MSG.NOT_ADMIN)
        return

    db = get_db_session()

    try:
        # Get all orders
        orders = db.query(Order).order_by(Order.created_at.desc()).all()

        if not orders:
            bot.send_message(message.chat.id, "📭 Немає замовлень для експорту.")
            return

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Номер замовлення', 'Дата створення', 'Користувач',
            'Телефон', 'Адреса', 'Спосіб доставки',
            'Сума', 'Знижка', 'Статус', 'Промокод'
        ])

        # Write data
        for order in orders:
            user_name = f"{order.user.first_name or ''} {order.user.last_name or ''}".strip()
            if not user_name:
                user_name = order.user.username or "Без імені"

            writer.writerow([
                order.order_number,
                order.created_at.strftime("%d.%m.%Y %H:%M"),
                user_name,
                order.phone or "",
                order.address or "Самовивіз",
                "Доставка" if order.delivery_method == "delivery" else "Самовивіз",
                f"{order.total:.2f}",
                f"{order.discount:.2f}",
                order.status,
                order.promo_code or ""
            ])

        # Create file and send
        csv_data = output.getvalue().encode('utf-8-sig')  # Excel-friendly encoding

        # Create filename with date
        filename = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        bot.send_document(
            message.chat.id,
            document=(filename, csv_data),
            caption=f"📊 Експорт замовлень\n"
                    f"📈 Всього замовлень: {len(orders)}\n"
                    f"⏰ Експорт створено: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        logger.info(f"Admin {message.from_user.id} exported {len(orders)} orders")

    except Exception as e:
        logger.error(f"Error exporting orders: {e}")
        bot.send_message(message.chat.id, "❌ Помилка при експорті замовлень.")

    finally:
        db.close()