"""
Keyboard generators for the bot.
"""
from telebot import types
from typing import List, Optional
from utils.locales import MSG


def create_main_keyboard() -> types.ReplyKeyboardMarkup:
    """Create main menu reply keyboard."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    keyboard.add(
        types.KeyboardButton(MSG.BTN_CATALOG),
        types.KeyboardButton(MSG.BTN_MY_ORDERS)
    )
    keyboard.add(
        types.KeyboardButton(MSG.BTN_INFO),
        types.KeyboardButton(MSG.BTN_CONTACT)
    )
    
    return keyboard


def create_admin_keyboard() -> types.ReplyKeyboardMarkup:
    """Create admin menu reply keyboard."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    keyboard.add(
        types.KeyboardButton(MSG.BTN_ADMIN_ADD),
        types.KeyboardButton(MSG.BTN_ADMIN_REMOVE)
    )
    keyboard.add(
        types.KeyboardButton(MSG.BTN_ADMIN_ORDERS),
        types.KeyboardButton(MSG.BTN_ADMIN_EXPORT)
    )
    keyboard.add(
        types.KeyboardButton(MSG.BTN_ADMIN_PROMO)
    )
    keyboard.add(
        types.KeyboardButton(MSG.BTN_BACK)
    )
    
    return keyboard


def create_catalog_keyboard(items: List, page: int = 0, items_per_page: int = 5) -> types.InlineKeyboardMarkup:
    """
    Create inline keyboard for catalog with pagination.
    
    Args:
        items: List of Item objects
        page: Current page number
        items_per_page: Items per page
        
    Returns:
        Inline keyboard markup
    """
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_items = items[start_idx:end_idx]
    
    # Add item buttons
    for item in page_items:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{item.name} - {item.price} грн",
                callback_data=f"item:{item.id}"
            )
        )
    
    # Add pagination buttons
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(
            types.InlineKeyboardButton(
                text="⬅️ Попередня",
                callback_data=f"catalog_page:{page-1}"
            )
        )
    
    if end_idx < len(items):
        nav_buttons.append(
            types.InlineKeyboardButton(
                text="Наступна ➡️",
                callback_data=f"catalog_page:{page+1}"
            )
        )
    
    if nav_buttons:
        keyboard.row(*nav_buttons)
    
    return keyboard


def create_product_keyboard(item_id: int) -> types.InlineKeyboardMarkup:
    """Create inline keyboard for product details."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton(
            text=MSG.BTN_ORDER,
            callback_data=f"order:{item_id}"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            text=MSG.BTN_BACK,
            callback_data="back_to_catalog"
        )
    )
    
    return keyboard


def create_size_keyboard(sizes: List[str], item_id: int) -> types.InlineKeyboardMarkup:
    """Create inline keyboard for size selection."""
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    
    buttons = [
        types.InlineKeyboardButton(
            text=size,
            callback_data=f"size:{item_id}:{size}"
        )
        for size in sizes
    ]
    
    # Add buttons in rows of 4
    for i in range(0, len(buttons), 4):
        keyboard.row(*buttons[i:i+4])
    
    keyboard.add(
        types.InlineKeyboardButton(
            text=MSG.BTN_CANCEL,
            callback_data="cancel_order"
        )
    )
    
    return keyboard


def create_delivery_keyboard() -> types.InlineKeyboardMarkup:
    """Create inline keyboard for delivery method selection."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton(
            text=MSG.BTN_PICKUP,
            callback_data="delivery:pickup"
        ),
        types.InlineKeyboardButton(
            text=MSG.BTN_DELIVERY,
            callback_data="delivery:delivery"
        )
    )
    
    return keyboard


def create_confirmation_keyboard() -> types.InlineKeyboardMarkup:
    """Create inline keyboard for order confirmation."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton(
            text=MSG.BTN_CONFIRM,
            callback_data="confirm_order"
        ),
        types.InlineKeyboardButton(
            text=MSG.BTN_CANCEL,
            callback_data="cancel_order"
        )
    )
    
    return keyboard


def create_order_actions_keyboard(order_id: int, current_status: str) -> types.InlineKeyboardMarkup:
    """Create inline keyboard for order management (admin)."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if current_status == "pending":
        keyboard.add(
            types.InlineKeyboardButton(
                text=MSG.BTN_STATUS_CONFIRMED,
                callback_data=f"order_status:{order_id}:confirmed"
            ),
            types.InlineKeyboardButton(
                text=MSG.BTN_STATUS_CANCELLED,
                callback_data=f"order_status:{order_id}:cancelled"
            )
        )
    
    elif current_status == "confirmed":
        keyboard.add(
            types.InlineKeyboardButton(
                text=MSG.BTN_STATUS_SHIPPED,
                callback_data=f"order_status:{order_id}:shipped"
            ),
            types.InlineKeyboardButton(
                text=MSG.BTN_STATUS_CANCELLED,
                callback_data=f"order_status:{order_id}:cancelled"
            )
        )
    
    return keyboard


def create_remove_item_keyboard(items: List) -> types.InlineKeyboardMarkup:
    """Create inline keyboard for item removal (admin)."""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    for item in items:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"🗑️ {item.name}",
                callback_data=f"remove_item:{item.id}"
            )
        )
    
    keyboard.add(
        types.InlineKeyboardButton(
            text=MSG.BTN_CANCEL,
            callback_data="cancel_remove"
        )
    )
    
    return keyboard


def create_yes_no_keyboard(action: str, data: str) -> types.InlineKeyboardMarkup:
    """Create generic yes/no confirmation keyboard."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton(
            text="✅ Так",
            callback_data=f"{action}_yes:{data}"
        ),
        types.InlineKeyboardButton(
            text="❌ Ні",
            callback_data=f"{action}_no:{data}"
        )
    )
    
    return keyboard