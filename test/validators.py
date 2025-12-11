"""
Unit tests for validation utilities.
Run with: pytest tests/test_validators.py -v
"""
import pytest
from utils.validators import (
    validate_phone,
    validate_price,
    validate_sizes,
    validate_quantity,
    validate_promo_discount,
    sanitize_text,
    mask_phone,
    validate_sku
)


class TestPhoneValidation:
    """Test phone number validation."""
    
    def test_valid_phone_with_plus(self):
        assert validate_phone("+380501234567") == True
    
    def test_valid_phone_long(self):
        assert validate_phone("+380501234567890") == True
    
    def test_valid_phone_short(self):
        assert validate_phone("+380501234") == True
    
    def test_invalid_phone_too_short(self):
        assert validate_phone("+38050123") == False
    
    def test_invalid_phone_letters(self):
        assert validate_phone("+38050ABC4567") == False
    
    def test_invalid_phone_spaces(self):
        assert validate_phone("+380 50 123 4567") == False
    
    def test_invalid_phone_empty(self):
        assert validate_phone("") == False


class TestPriceValidation:
    """Test price validation."""
    
    def test_valid_integer_price(self):
        assert validate_price("1500") == 1500.0
    
    def test_valid_float_price(self):
        assert validate_price("1500.50") == 1500.5
    
    def test_valid_price_with_comma(self):
        assert validate_price("1500,50") == 1500.5
    
    def test_valid_min_price(self):
        assert validate_price("0.01") == 0.01
    
    def test_invalid_zero_price(self):
        assert validate_price("0") is None
    
    def test_invalid_negative_price(self):
        assert validate_price("-100") is None
    
    def test_invalid_too_high_price(self):
        assert validate_price("10000000") is None
    
    def test_invalid_text_price(self):
        assert validate_price("abc") is None
    
    def test_invalid_empty_price(self):
        assert validate_price("") is None


class TestSizesValidation:
    """Test shoe sizes validation."""
    
    def test_valid_sizes_simple(self):
        result = validate_sizes("38,39,40")
        assert result == ["38", "39", "40"]
    
    def test_valid_sizes_with_spaces(self):
        result = validate_sizes("38, 39, 40, 41")
        assert result == ["38", "39", "40", "41"]
    
    def test_valid_large_sizes(self):
        result = validate_sizes("44,45,46")
        assert result == ["44", "45", "46"]
    
    def test_invalid_sizes_out_of_range(self):
        result = validate_sizes("20,30,50")
        assert result is None
    
    def test_invalid_sizes_mixed(self):
        result = validate_sizes("38,39,99")  # 99 is invalid
        assert result is None
    
    def test_invalid_sizes_text(self):
        result = validate_sizes("small,medium,large")
        assert result is None
    
    def test_invalid_empty_sizes(self):
        result = validate_sizes("")
        assert result is None


class TestQuantityValidation:
    """Test quantity validation."""
    
    def test_valid_quantity_one(self):
        assert validate_quantity("1") == 1
    
    def test_valid_quantity_ten(self):
        assert validate_quantity("10") == 10
    
    def test_valid_quantity_max(self):
        assert validate_quantity("99") == 99
    
    def test_invalid_quantity_zero(self):
        assert validate_quantity("0") is None
    
    def test_invalid_quantity_negative(self):
        assert validate_quantity("-5") is None
    
    def test_invalid_quantity_too_high(self):
        assert validate_quantity("100") is None
    
    def test_invalid_quantity_text(self):
        assert validate_quantity("five") is None
    
    def test_invalid_quantity_float(self):
        assert validate_quantity("5.5") is None


class TestPromoDiscountValidation:
    """Test promo code discount validation."""
    
    def test_valid_discount_ten(self):
        assert validate_promo_discount("10") == 10.0
    
    def test_valid_discount_fifty(self):
        assert validate_promo_discount("50") == 50.0
    
    def test_valid_discount_float(self):
        assert validate_promo_discount("15.5") == 15.5
    
    def test_valid_discount_with_comma(self):
        assert validate_promo_discount("15,5") == 15.5
    
    def test_invalid_discount_zero(self):
        assert validate_promo_discount("0") is None
    
    def test_invalid_discount_negative(self):
        assert validate_promo_discount("-10") is None
    
    def test_invalid_discount_over_hundred(self):
        assert validate_promo_discount("101") is None
    
    def test_invalid_discount_text(self):
        assert validate_promo_discount("ten") is None


class TestSanitizeText:
    """Test text sanitization."""
    
    def test_sanitize_normal_text(self):
        result = sanitize_text("Hello world")
        assert result == "Hello world"
    
    def test_sanitize_multiple_spaces(self):
        result = sanitize_text("Hello    world")
        assert result == "Hello world"
    
    def test_sanitize_newlines(self):
        result = sanitize_text("Hello\n\nworld")
        assert result == "Hello world"
    
    def test_sanitize_tabs(self):
        result = sanitize_text("Hello\t\tworld")
        assert result == "Hello world"
    
    def test_sanitize_long_text(self):
        long_text = "a" * 2000
        result = sanitize_text(long_text, max_length=100)
        assert len(result) <= 103  # 100 + "..."
        assert result.endswith("...")
    
    def test_sanitize_empty(self):
        result = sanitize_text("")
        assert result == ""
    
    def test_sanitize_none(self):
        result = sanitize_text(None)
        assert result == ""


class TestMaskPhone:
    """Test phone number masking for privacy."""
    
    def test_mask_phone_standard(self):
        result = mask_phone("+380501234567")
        assert result == "+38****4567"
    
    def test_mask_phone_long(self):
        result = mask_phone("+380501234567890")
        assert result == "+38****7890"
    
    def test_mask_phone_short(self):
        result = mask_phone("12345")
        assert result == "***"
    
    def test_mask_phone_very_short(self):
        result = mask_phone("123")
        assert result == "***"


class TestSKUValidation:
    """Test SKU validation."""
    
    def test_valid_sku_simple(self):
        assert validate_sku("SHOE-001") == True
    
    def test_valid_sku_long(self):
        assert validate_sku("WOMENS-RUNNING-SHOE-2024-001") == True
    
    def test_valid_sku_numbers(self):
        assert validate_sku("12345") == True
    
    def test_valid_sku_underscore(self):
        assert validate_sku("SHOE_001") == True
    
    def test_invalid_sku_too_short(self):
        assert validate_sku("AB") == False
    
    def test_invalid_sku_spaces(self):
        assert validate_sku("SHOE 001") == False
    
    def test_invalid_sku_special_chars(self):
        assert validate_sku("SHOE@001") == False
    
    def test_invalid_sku_cyrillic(self):
        assert validate_sku("ВЗУТТЯ-001") == False


# Run with: pytest tests/test_validators.py -v --cov=utils.validators
if __name__ == "__main__":
    pytest.main([__file__, "-v"])