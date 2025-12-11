"""
Configuration module for Shoe Shop Telegram Bot.
Loads environment variables and provides configuration constants.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Bot configuration class."""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "###")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN must be set in environment variables")
    
    # Admin Users
    ADMIN_IDS_STR: str = os.getenv("ADMIN_IDS", "###")
    ADMIN_IDS: List[int] = [
        int(id.strip()) 
        for id in ADMIN_IDS_STR.split(",") 
        if id.strip().isdigit()
    ]
    
    # Database
    DB_URL: str = os.getenv("DB_URL", "sqlite:///data/shop.db")
    
    # Payment
    PAYMENT_PROVIDER_TOKEN: str = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
    PAYMENT_CURRENCY: str = "UAH"
    DELIVERY_PRICE: int = 10000  # 100.00 UAH in kopiykas
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/bot.log")
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT: int = 5
    
    # Rate Limiting
    RATE_LIMIT_MESSAGES: int = int(os.getenv("RATE_LIMIT_MESSAGES", "20"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Webhook
    USE_WEBHOOK: bool = os.getenv("USE_WEBHOOK", "False").lower() == "true"
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
    
    # Shop Settings
    DEFAULT_LANGUAGE: str = "uk"
    SUPPORTED_LANGUAGES: List[str] = ["uk", "en"]
    
    # Pagination
    ITEMS_PER_PAGE: int = 5
    ORDERS_PER_PAGE: int = 10
    
    # Validation
    MIN_PRICE: float = 0.01
    MAX_PRICE: float = 1000000.0
    PHONE_PATTERN: str = r"^\+?\d{9,15}$"
    AVAILABLE_SIZES: List[str] = [
        "35", "36", "37", "38", "39", "40", 
        "41", "42", "43", "44", "45", "46"
    ]
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in cls.ADMIN_IDS
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        
        if not cls.ADMIN_IDS:
            print("WARNING: No ADMIN_IDS configured. Admin features will be disabled.")
        
        if cls.USE_WEBHOOK and not cls.WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL is required when USE_WEBHOOK is True")
        
        print(f"✓ Configuration loaded successfully")
        print(f"  - Database: {cls.DB_URL}")
        print(f"  - Admins: {len(cls.ADMIN_IDS)} configured")
        print(f"  - Webhook: {'Enabled' if cls.USE_WEBHOOK else 'Disabled (polling)'}")


# Validate config on import
Config.validate()