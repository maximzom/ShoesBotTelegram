"""
Localization strings for the bot.
All user-facing messages in Ukrainian.
"""

class Messages:
    """Ukrainian messages for the bot."""
    
    # Start and basic commands
    START = """👟 Вітаємо в магазині "StepRight"!

Я допоможу знайти та замовити взуття. Виберіть одну з опцій нижче."""
    
    HELP = """📖 Доступні команди:

👤 Для користувачів:
/start - Почати роботу з ботом.
/catalog - Переглянути каталог взуття.
/order - Оформити замовлення (Переглянути замовлення).
/info - Інформація про магазин.
/feedback - Залишити відгук.
/help - Показати цю довідку.
/promo - Знижки.

👑 Для адміністраторів:
/admin - Панель адміністратора.
/add_item - Додати новий товар.
/remove_item - Видалити товар.
/orders - Переглянути замовлення.
/promo_add - Додати промокод.
/export_orders - Експортувати замовлення."""
    
    INFO = """ℹ️ Про магазин "StepRight"

🕐 Режим роботи: Пн-Пт 9:00-18:00, Сб 10:00-16:00
📞 Контакт: +380 44 226 2564
📧 Email: info@stepright.ua

🚚 Доставка:
• Самовивіз (безкоштовно)
• Доставка по Україні (100 грн)
• Доставка у межах міста (50 грн)

💳 Оплата:
• Готівкою при отриманні
• Картою онлайн
• Безготівковий розрахунок

✅ Гарантія якості на всі товари
🔄 Можливість обміну протягом 14 днів"""
    
    HELLO = "👋 Вітаю! Як я можу вам допомогти сьогодні?"
    
    # Catalog
    CATALOG_HEADER = """👟 Наш каталог взуття

Оберіть товар, щоб побачити деталі:"""
    
    CATALOG_EMPTY = "😔 На жаль, каталог порожній. Зверніться пізніше."
    
    PRODUCT_DETAILS = """📦 {name}

💰 Ціна: {price} грн
📏 Доступні розміри: {sizes}

📝 Опис:
{description}"""
    
    # Cart and ordering
    SELECT_SIZE = "📏 Оберіть розмір:"
    SELECT_QUANTITY = "🔢 Введіть кількість (число):"
    INVALID_QUANTITY = "❌ Будь ласка, введіть правильне число (1-99)"
    
    SELECT_DELIVERY = """🚚 Оберіть спосіб доставки:

• Самовивіз - безкоштовно
• Доставка - 100 грн"""
    
    ENTER_ADDRESS = "📍 Введіть адресу доставки:"
    ENTER_PHONE = "📞 Введіть номер телефону (формат: +380XXXXXXXXX):"
    INVALID_PHONE = "❌ Неправильний формат телефону. Використайте формат: +380XXXXXXXXX"
    
    ORDER_SUMMARY = """📋 Підсумок замовлення:

{items}

💰 Сума товарів: {subtotal} грн
🚚 Доставка: {delivery} грн
🎟️ Знижка: {discount} грн
━━━━━━━━━━━━━━━━━
💳 Разом: {total} грн

📍 Адреса: {address}
📞 Телефон: {phone}

Підтвердити замовлення?"""
    
    ORDER_CREATED = """✅ Дякуємо! Ваше замовлення #{order_number} прийняте.

Ми зв'яжемося з вами найближчим часом.
Статус: {status}

📊 Відстежити замовлення: /order"""
    
    ORDER_CANCELLED = "❌ Замовлення скасовано."
    
    # Admin notifications
    ADMIN_NEW_ORDER = """🔔 НОВЕ ЗАМОВЛЕННЯ #{order_number}

👤 Користувач: {user_name} (@{username})
🆔 ID: {tg_id}

📦 Товари:
{items}

💰 Сума: {total} грн
🚚 Доставка: {delivery_method}
📍 Адреса: {address}
📞 Телефон: {phone}

⏰ {created_at}"""
    
    # Feedback
    FEEDBACK_PROMPT = "📝 Напишіть ваш відгук або пропозицію:"
    FEEDBACK_THANKS = "✅ Дякуємо за відгук! Ми його отримали і незабаром відповімо."
    
    ADMIN_FEEDBACK = """📨 НОВИЙ ВІДГУК

👤 Від: {user_name} (@{username})
🆔 ID: {tg_id}

💬 Відгук:
{text}

⏰ {created_at}"""
    
    # Admin commands
    ADMIN_MENU = """👑 Панель адміністратора

Виберіть дію:"""
    
    NOT_ADMIN = "⛔ У вас немає прав адміністратора."
    
    ADD_ITEM_NAME = "📝 Введіть назву товару:"
    ADD_ITEM_PRICE = "💰 Введіть ціну (грн):"
    ADD_ITEM_SIZES = "📏 Введіть доступні розміри через кому (наприклад: 38,39,40,41):"
    ADD_ITEM_DESCRIPTION = "📄 Введіть опис товару:"
    ADD_ITEM_IMAGE = "📸 Надішліть фото товару (або /skip щоб пропустити):"
    ADD_ITEM_SUCCESS = "✅ Товар успішно додано до каталогу!"
    ADD_ITEM_CANCELLED = "❌ Додавання товару скасовано."
    
    INVALID_PRICE = "❌ Неправильна ціна. Введіть число (наприклад: 1500 або 1500.50)"
    INVALID_SIZES = "❌ Неправильний формат розмірів. Використайте числа через кому."
    
    REMOVE_ITEM_SELECT = "🗑️ Оберіть товар для видалення:"
    REMOVE_ITEM_CONFIRM = "❓ Ви впевнені, що хочете видалити цей товар?"
    REMOVE_ITEM_SUCCESS = "✅ Товар видалено з каталогу."
    REMOVE_ITEM_CANCELLED = "❌ Видалення скасовано."
    
    ORDERS_LIST = "📊 Список замовлень:"
    ORDERS_EMPTY = "📭 Немає замовлень."
    
    ORDER_DETAILS = """📦 Замовлення #{order_number}

👤 Клієнт: {user_name}
📞 Телефон: {phone}
📍 Адреса: {address}

🛍️ Товари:
{items}

💰 Сума: {total} грн
📊 Статус: {status}
⏰ Створено: {created_at}"""
    
    ORDER_STATUS_UPDATED = "✅ Статус замовлення оновлено: {status}"
    
    # Promo codes
    PROMO_ADD_CODE = "🎟️ Введіть код промокоду:"
    PROMO_ADD_DISCOUNT = "💰 Введіть відсоток знижки (наприклад: 10 для 10%):"
    PROMO_ADD_SUCCESS = "✅ Промокод створено!"
    PROMO_INVALID = "❌ Промокод недійсний або прострочений."
    PROMO_APPLIED = "✅ Промокод застосовано! Знижка: {discount}%"
    
    # Errors
    ERROR_GENERAL = "❌ Сталася помилка. Спробуйте пізніше."
    ERROR_PRODUCT_NOT_FOUND = "❌ Товар не знайдено."
    ERROR_ORDER_NOT_FOUND = "❌ Замовлення не знайдено."
    
    # Buttons
    BTN_CATALOG = "🛍️ Каталог"
    BTN_MY_ORDERS = "📦 Мої замовлення"
    BTN_INFO = "ℹ️ Інфо"
    BTN_CONTACT = "📞 Зв'язок"
    BTN_DETAILS = "🔍 Деталі"
    BTN_ADD_TO_CART = "🛒 Додати в кошик"
    BTN_ORDER = "🛒 Замовити"
    BTN_BACK = "⬅️ Назад"
    BTN_CONFIRM = "✅ Підтвердити"
    BTN_CANCEL = "❌ Скасувати"
    BTN_PICKUP = "🏪 Самовивіз"
    BTN_DELIVERY = "🚚 Доставка"
    
    # Admin buttons
    BTN_ADMIN_ADD = "➕ Додати товар"
    BTN_ADMIN_REMOVE = "🗑️ Видалити товар"
    BTN_ADMIN_ORDERS = "📊 Перегляд замовлень"
    BTN_ADMIN_EXPORT = "📤 Експорт замовлень"
    BTN_ADMIN_PROMO = "🎟️ Промокоди"
    
    BTN_STATUS_CONFIRMED = "✅ Підтвердити"
    BTN_STATUS_SHIPPED = "📦 Відправлено"
    BTN_STATUS_CANCELLED = "❌ Скасувати"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "⏳ Забагато запитів. Спробуйте через хвилину."


# Shortcuts for easier access
MSG = Messages