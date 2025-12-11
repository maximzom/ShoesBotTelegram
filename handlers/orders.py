"""
Handlers for order creation and management.
"""
import logging
from telebot import TeleBot, types

from models.db import get_db_session
from models.schemas import User, Item, Cart, CartItem
from utils.locales import MSG
from utils.keyboards import (
    create_size_keyboard,
    create_delivery_keyboard,
    create_confirmation_keyboard
)
from services.order_service import create_order, get_user_orders, get_order_summary_dict
from utils.validators import validate_phone, validate_quantity
from config import Config

logger = logging.getLogger(__name__)

# User state storage for multi-step flows
user_states = {}


def start_order_flow(call: types.CallbackQuery, bot: TeleBot):
    """Start order creation for a product."""
    item_id = int(call.data.split(":")[1])
    db = get_db_session()

    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        user = db.query(User).filter(User.tg_id == call.from_user.id).first()

        if not item or not user:
            bot.answer_callback_query(call.id, MSG.ERROR_PRODUCT_NOT_FOUND)
            return

        # Store initial state
        user_states[call.from_user.id] = {
            'item_id': item_id,
            'step': 'select_size'
        }

        # Show size selection
        sizes = item.get_sizes()

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{MSG.SELECT_SIZE}\n\n{item.name} - {item.price:.2f} грн",
            reply_markup=create_size_keyboard(sizes, item_id)
        )

        bot.answer_callback_query(call.id)

    finally:
        db.close()


def handle_size_selection(call: types.CallbackQuery, bot: TeleBot):
    """Handle size selection and ask for quantity."""
    _, item_id, size = call.data.split(":")
    item_id = int(item_id)

    db = get_db_session()

    try:
        item = db.query(Item).filter(Item.id == item_id).first()

        if not item:
            bot.answer_callback_query(call.id, MSG.ERROR_PRODUCT_NOT_FOUND)
            return

        # Update user state
        if call.from_user.id not in user_states:
            user_states[call.from_user.id] = {}

        user_states[call.from_user.id].update({
            'item_id': item_id,
            'size': size,
            'step': 'select_quantity',
            'price': item.price
        })

        # Ask for quantity
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=MSG.SELECT_QUANTITY
        )

        # Register next step handler
        bot.register_next_step_handler(msg, process_quantity, bot)

        bot.answer_callback_query(call.id)

    finally:
        db.close()


def process_quantity(message: types.Message, bot: TeleBot):
    """Process quantity input."""
    user_id = message.from_user.id

    if user_id not in user_states:
        bot.send_message(message.chat.id, MSG.ERROR_GENERAL)
        return

    quantity = validate_quantity(message.text)

    if not quantity:
        msg = bot.send_message(message.chat.id, MSG.INVALID_QUANTITY)
        bot.register_next_step_handler(msg, process_quantity, bot)
        return

    # Update state
    user_states[user_id]['quantity'] = quantity
    user_states[user_id]['step'] = 'select_delivery'

    # Ask for delivery method
    bot.send_message(
        message.chat.id,
        MSG.SELECT_DELIVERY,
        reply_markup=create_delivery_keyboard()
    )


def handle_delivery_selection(call: types.CallbackQuery, bot: TeleBot):
    """Handle delivery method selection."""
    delivery_method = call.data.split(":")[1]
    user_id = call.from_user.id

    if user_id not in user_states:
        bot.answer_callback_query(call.id, MSG.ERROR_GENERAL)
        return

    user_states[user_id]['delivery_method'] = delivery_method
    user_states[user_id]['step'] = 'enter_phone'

    if delivery_method == "delivery":
        user_states[user_id]['step'] = 'enter_address'
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=MSG.ENTER_ADDRESS
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=MSG.ENTER_PHONE
        )

    bot.answer_callback_query(call.id)

    if delivery_method == "delivery":
        bot.register_next_step_handler(call.message, process_address, bot)
    else:
        bot.register_next_step_handler(call.message, process_phone, bot)


def process_address(message: types.Message, bot: TeleBot):
    """Process delivery address."""
    user_id = message.from_user.id

    if user_id not in user_states:
        bot.send_message(message.chat.id, MSG.ERROR_GENERAL)
        return

    user_states[user_id]['address'] = message.text.strip()
    user_states[user_id]['step'] = 'enter_phone'

    bot.send_message(message.chat.id, MSG.ENTER_PHONE)
    bot.register_next_step_handler(message, process_phone, bot)


def process_phone(message: types.Message, bot: TeleBot):
    """Process phone number."""
    user_id = message.from_user.id

    if user_id not in user_states:
        bot.send_message(message.chat.id, MSG.ERROR_GENERAL)
        return

    phone = message.text.strip()

    if not validate_phone(phone):
        msg = bot.send_message(message.chat.id, MSG.INVALID_PHONE)
        bot.register_next_step_handler(msg, process_phone, bot)
        return

    user_states[user_id]['phone'] = phone
    user_states[user_id]['step'] = 'confirm_order'

    # Show order summary
    show_order_summary(user_id, message.chat.id, bot)


def show_order_summary(user_id: int, chat_id: int, bot: TeleBot):
    """Show order summary for confirmation."""
    state = user_states.get(user_id)

    if not state:
        bot.send_message(chat_id, MSG.ERROR_GENERAL)
        return

    db = get_db_session()

    try:
        item = db.query(Item).filter(Item.id == state['item_id']).first()

        if not item:
            bot.send_message(chat_id, MSG.ERROR_PRODUCT_NOT_FOUND)
            return

        # Prepare items list for calculation
        items_data = [{
            'item_id': state['item_id'],
            'size': state['size'],
            'quantity': state['quantity'],
            'price': state['price']
        }]

        # Import here to avoid circular import
        from services.order_service import calculate_order_total

        totals = calculate_order_total(
            items_data,
            state.get('delivery_method', 'pickup'),
            None,  # promo code
            db
        )

        # Format items text
        items_text = f"• {item.name} (розмір {state['size']}) x {state['quantity']} = {totals['subtotal']:.2f} грн"

        # Delivery text
        delivery_text = "Самовивіз (безкоштовно)"
        if state.get('delivery_method') == "delivery":
            delivery_text = f"Доставка ({totals['delivery']:.2f} грн)"

        summary = MSG.ORDER_SUMMARY.format(
            items=items_text,
            subtotal=totals['subtotal'],
            delivery=totals['delivery'],
            discount=totals['discount'],
            total=totals['total'],
            address=state.get('address', "Самовивіз"),
            phone=state.get('phone', 'Не вказано')
        )

        bot.send_message(
            chat_id,
            summary,
            reply_markup=create_confirmation_keyboard()
        )

    finally:
        db.close()


def handle_order_confirmation(call: types.CallbackQuery, bot: TeleBot):
    """Handle order confirmation."""
    user_id = call.from_user.id
    state = user_states.get(user_id)

    if not state:
        bot.answer_callback_query(call.id, MSG.ERROR_GENERAL)
        return

    db = get_db_session()

    try:
        user = db.query(User).filter(User.tg_id == user_id).first()

        if not user:
            bot.answer_callback_query(call.id, MSG.ERROR_GENERAL)
            return

        # Prepare items data
        items_data = [{
            'item_id': state['item_id'],
            'size': state['size'],
            'quantity': state['quantity'],
            'price': state['price']
        }]

        # Create order
        order = create_order(
            user=user,
            items_data=items_data,
            delivery_method=state.get('delivery_method', 'pickup'),
            address=state.get('address'),
            phone=state.get('phone'),
            promo_code=None,
            db=db
        )

        # Notify admins
        notify_admins(order, user, bot)

        # Send confirmation to user
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=MSG.ORDER_CREATED.format(
                order_number=order.order_number,
                status=order.status
            )
        )

        # Clear user state
        if user_id in user_states:
            del user_states[user_id]

        bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        bot.answer_callback_query(call.id, MSG.ERROR_GENERAL)

    finally:
        db.close()


def handle_order_cancellation(call: types.CallbackQuery, bot: TeleBot):
    """Handle order cancellation."""
    user_id = call.from_user.id

    # Clear user state
    if user_id in user_states:
        del user_states[user_id]

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=MSG.ORDER_CANCELLED
    )

    bot.answer_callback_query(call.id)


def show_my_orders(message: types.Message, bot: TeleBot):
    """Show user's orders."""
    db = get_db_session()

    try:
        user = db.query(User).filter(User.tg_id == message.from_user.id).first()

        if not user:
            bot.send_message(message.chat.id, "Будь ласка, спочатку виконайте /start")
            return

        orders = get_user_orders(user, db)

        if not orders:
            bot.send_message(message.chat.id, "📭 У вас ще немає замовлень.")
            return

        for order in orders:
            summary = get_order_summary_dict(order)

            text = f"""📦 Замовлення #{summary['order_number']}

🛍️ Товари:
{summary['items']}

💰 Сума: {summary['total']:.2f} грн
📊 Статус: {summary['status']}
⏰ Створено: {summary['created_at']}
📍 {summary['delivery_method']}"""

            bot.send_message(
                message.chat.id,
                text
            )

    except Exception as e:
        logger.error(f"Error showing orders: {e}")
        bot.send_message(message.chat.id, "❌ Помилка при отриманні замовлень.")

    finally:
        db.close()



def notify_admins(order, user, bot: TeleBot):
    """Notify admins about new order."""
    summary = get_order_summary_dict(order)

    text = MSG.ADMIN_NEW_ORDER.format(
        order_number=order.order_number,
        user_name=f"{user.first_name or ''} {user.last_name or ''}".strip(),
        username=user.username or "немає",
        tg_id=user.tg_id,
        items=summary['items'],
        total=order.total,
        delivery_method="Доставка" if order.delivery_method == "delivery" else "Самовивіз",
        address=order.address or "Самовивіз",
        phone=order.phone,
        created_at=order.created_at.strftime("%d.%m.%Y %H:%M")
    )

    for admin_id in Config.ADMIN_IDS:
        try:
            bot.send_message(admin_id, text)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


def register_order_handlers(bot: TeleBot):
    """Register all order-related handlers."""

    @bot.callback_query_handler(func=lambda call: call.data.startswith("order:"))
    def start_order_wrapper(call):
        start_order_flow(call, bot)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("size:"))
    def size_selection_wrapper(call):
        handle_size_selection(call, bot)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("delivery:"))
    def delivery_selection_wrapper(call):
        handle_delivery_selection(call, bot)

    @bot.callback_query_handler(func=lambda call: call.data == "confirm_order")
    def confirm_order_wrapper(call):
        handle_order_confirmation(call, bot)

    @bot.callback_query_handler(func=lambda call: call.data == "cancel_order")
    def cancel_order_wrapper(call):
        handle_order_cancellation(call, bot)

    @bot.message_handler(commands=['order'])
    def order_command_wrapper(message):
        # For now, redirect to my orders
        show_my_orders(message, bot)