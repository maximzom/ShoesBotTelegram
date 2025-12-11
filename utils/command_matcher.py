"""
Enhanced command matching with synonyms and fuzzy matching.
"""
import re
from typing import Dict, List, Optional, Tuple

# Dictionary of command synonyms and aliases
COMMAND_SYNONYMS = {
    # Catalog commands
    '🛍️ Каталог': [
        'каталог', 'catalog', 'каталог', 'katalog', 'товари', 'товары',
        'products', 'shop', 'магазин', 'взуття', 'обувь', 'обувки',
        'перегляд', 'просмотр', 'дивитися', 'смотреть'
    ],

    # My orders
    '📦 Мої замовлення': [
        'мої замовлення', 'мои заказы', 'my orders', 'замовлення',
        'заказы', 'orders', 'мої покупки', 'мои покупки', 'история',
        'історія', 'покупки', 'куплені', 'купленные'
    ],

    # Info
    'ℹ️ Інфо': [
        'інфо', 'инфо', 'info', 'информация', 'інформація', 'about',
        'про нас', 'о нас', 'контакти', 'контакты', 'контакт',
        'магазин', 'shop info', 'доставка', 'оплата', 'гарантія'
    ],

    # Contact/Feedback
    '📞 Зв\'язок': [
        'зв\'язок', 'связь', 'contact', 'контакт', 'feedback',
        'відгук', 'отзыв', 'пропозиція', 'предложение', 'питання',
        'вопрос', 'підтримка', 'поддержка', 'help'
    ],

    # Order/Add to cart
    '🛒 Замовити': [
        'замовити', 'заказать', 'order', 'buy', 'купити', 'купить',
        'додати в кошик', 'добавить в корзину', 'add to cart',
        'придбати', 'приобрести', 'оформити', 'оформить'
    ],

    # Back
    '⬅️ Назад': [
        'назад', 'back', 'повернутися', 'вернуться', 'return',
        'головна', 'главная', 'меню', 'menu', 'start'
    ],

    # Confirm
    '✅ Підтвердити': [
        'підтвердити', 'подтвердить', 'confirm', 'так', 'да', 'yes',
        'ок', 'ok', 'готово', 'готово', 'згоден', 'согласен'
    ],

    # Cancel
    '❌ Скасувати': [
        'скасувати', 'отменить', 'cancel', 'ні', 'нет', 'no',
        'відмінити', 'отменить', 'стоп', 'stop', 'вийти', 'выйти'
    ],

    # Delivery methods
    '🚚 Доставка': [
        'доставка', 'delivery', 'доставка кур\'єром', 'доставка курьером',
        'привезти', 'привезти', 'додому', 'домой', 'на адресу', 'по адресу'
    ],

    '🏪 Самовивіз': [
        'самовивіз', 'самовывоз', 'pickup', 'забрати', 'забрать',
        'в магазині', 'в магазине', 'особисто', 'лично', 'самостоятельно'
    ],

    # Admin commands
    '➕ Додати товар': [
        'додати товар', 'добавить товар', 'add item', 'новый товар',
        'новий товар', 'create product', 'створити товар'
    ],

    '🗑️ Видалити товар': [
        'видалити товар', 'удалить товар', 'remove item', 'delete product',
        'видалення товару', 'удаление товара'
    ],

    '📊 Перегляд замовлень': [
        'перегляд замовлень', 'просмотр заказов', 'view orders',
        'всі замовлення', 'все заказы', 'список замовлень'
    ],

    '📤 Експорт замовлень': [
        'експорт замовлень', 'экспорт заказов', 'export orders',
        'вигрузити замовлення', 'выгрузить заказы', 'скачати замовлення'
    ],

    '🎟️ Промокоди': [
        'промокоди', 'промокоды', 'promo codes', 'промо коди',
        'знижки', 'скидки', 'discounts', 'акції', 'акции'
    ],
}


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    if not text:
        return ""

    # Remove emojis and extra spaces
    text = re.sub(r'[^\w\s]', '', text)
    text = text.strip().lower()

    # Common Russian/Ukrainian character normalization
    replacements = {
        'ё': 'е', 'ї': 'и', 'і': 'и', 'є': 'е',
        'ґ': 'г', 'ы': 'и', 'э': 'е'
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def find_matching_command(user_text: str) -> Optional[Tuple[str, str]]:
    """
    Find matching command for user text.

    Returns:
        Tuple of (canonical_command, matched_variant) or None
    """
    user_text_lower = user_text.strip().lower()
    normalized_user = normalize_text(user_text)

    # First, try exact match with canonical commands
    for canonical, synonyms in COMMAND_SYNONYMS.items():
        # Remove emoji from canonical for comparison
        canonical_clean = re.sub(r'[^\w\s]', '', canonical).strip().lower()

        if user_text_lower == canonical_clean:
            return canonical, canonical

    # Try synonyms
    for canonical, synonyms in COMMAND_SYNONYMS.items():
        for synonym in synonyms:
            synonym_lower = synonym.lower()

            # Exact match with synonym
            if user_text_lower == synonym_lower:
                return canonical, synonym

            # Partial match (contains)
            if synonym_lower in user_text_lower and len(synonym_lower) > 3:
                return canonical, synonym

            # Normalized comparison
            if normalize_text(synonym) in normalized_user and len(synonym) > 3:
                return canonical, synonym

    # Try fuzzy matching for common phrases
    fuzzy_patterns = {
        r'(каталог|товар|магазин|обув)': '🛍️ Каталог',
        r'(замовленн|заказ|купл|покуп)': '📦 Мої замовлення',
        r'(инфо|информ|about|про\s*нас)': 'ℹ️ Інфо',
        r'(зв[ья]зок|контакт|отзыв|вопрос)': '📞 Зв\'язок',
        r'(доставк|привез|кур[ье]р)': '🚚 Доставка',
        r'(самовывоз|забрать|магазин\s*забрать)': '🏪 Самовивіз',
    }

    for pattern, command in fuzzy_patterns.items():
        if re.search(pattern, normalized_user, re.IGNORECASE):
            return command, user_text

    return None


def is_command_match(user_text: str, target_command: str) -> bool:
    """Check if user text matches a specific command."""
    match = find_matching_command(user_text)
    return match is not None and match[0] == target_command


# Create reverse mapping for quick access
def get_command_variants(command: str) -> List[str]:
    """Get all variants (including canonical) for a command."""
    variants = [command]
    if command in COMMAND_SYNONYMS:
        variants.extend(COMMAND_SYNONYMS[command])
    return variants