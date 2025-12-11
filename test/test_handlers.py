"""
Integration tests for bot handlers using mocks.
Run with: pytest tests/test_handlers.py -v
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from telebot import types

from handlers.start import handle_start, get_or_create_user, handle_hello
from handlers.catalog import show_catalog
from services.order_service import calculate_order_total
from config import Config


class TestStartHandlers:
    """Test start command handlers."""

    def test_get_or_create_user_new(self):
        """Test creating new user."""
        # Create mock user attributes
        mock_from_user = Mock()
        mock_from_user.id = 123456
        mock_from_user.username = "test_user"
        mock_from_user.first_name = "Test"
        mock_from_user.last_name = "User"

        # Mock message
        mock_message = Mock(spec=types.Message)
        mock_message.from_user = mock_from_user

        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_db.close = Mock()

        with patch('handlers.start.get_db_session', return_value=mock_db):
            user = get_or_create_user(mock_message)

            # Verify user was created
            assert mock_db.add.called
            assert mock_db.commit.called
            assert user is not None

    def test_get_or_create_user_existing(self):
        """Test getting existing user."""
        # Mock user
        mock_user = Mock()
        mock_user.tg_id = 123456
        mock_user.username = "old_username"
        mock_user.first_name = "Old"
        mock_user.last_name = "Name"

        # Create mock user attributes for message
        mock_from_user = Mock()
        mock_from_user.id = 123456
        mock_from_user.username = "new_username"
        mock_from_user.first_name = "New"
        mock_from_user.last_name = "Name"

        # Mock message
        mock_message = Mock(spec=types.Message)
        mock_message.from_user = mock_from_user

        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.commit = Mock()
        mock_db.close = Mock()

        with patch('handlers.start.get_db_session', return_value=mock_db):
            user = get_or_create_user(mock_message)

            # Verify user was updated
            assert mock_user.username == "new_username"
            assert mock_user.first_name == "New"
            assert mock_user.last_name == "Name"
            assert mock_db.commit.called

    def test_handle_start(self):
        """Test /start command handler."""
        # Create mock chat
        mock_chat = Mock()
        mock_chat.id = 123456

        # Create mock user
        mock_from_user = Mock()
        mock_from_user.id = 123456

        # Mock message
        mock_message = Mock(spec=types.Message)
        mock_message.chat = mock_chat
        mock_message.from_user = mock_from_user

        # Mock bot
        mock_bot = Mock()
        mock_bot.send_message = Mock()

        # Mock get_or_create_user
        mock_user = Mock()
        mock_user.tg_id = 123456

        with patch('handlers.start.get_or_create_user', return_value=mock_user):
            handle_start(mock_message, mock_bot)

            # Verify bot sent message
            mock_bot.send_message.assert_called_once()

    def test_handle_hello(self):
        """Test /hello command handler."""
        # Create mock chat
        mock_chat = Mock()
        mock_chat.id = 123456

        # Create mock user
        mock_from_user = Mock()
        mock_from_user.id = 123456

        # Mock message
        mock_message = Mock(spec=types.Message)
        mock_message.chat = mock_chat
        mock_message.from_user = mock_from_user  # Добавлено!

        # Mock bot
        mock_bot = Mock()
        mock_bot.send_message = Mock()

        handle_hello(mock_message, mock_bot)

        # Verify bot sent hello message
        mock_bot.send_message.assert_called_once_with(123456, "👋 Вітаю! Як я можу вам допомогти сьогодні?")


class TestCatalogHandlers:
    """Test catalog handlers."""

    def test_show_catalog_with_items(self):
        """Test showing catalog with items."""
        # Create mock chat
        mock_chat = Mock()
        mock_chat.id = 123456

        # Create mock user
        mock_from_user = Mock()
        mock_from_user.id = 123456

        # Mock message
        mock_message = Mock(spec=types.Message)
        mock_message.chat = mock_chat
        mock_message.from_user = mock_from_user

        # Mock bot
        mock_bot = Mock()
        mock_bot.send_message = Mock()

        # Mock database items
        mock_item1 = Mock()
        mock_item1.id = 1
        mock_item1.name = "Nike Air Max"
        mock_item1.price = 2499.0

        mock_item2 = Mock()
        mock_item2.id = 2
        mock_item2.name = "Adidas Ultraboost"
        mock_item2.price = 3299.0

        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.all.return_value = [mock_item1, mock_item2]
        mock_db.close = Mock()

        # Mock config
        with patch('handlers.catalog.Config') as mock_config:
            mock_config.ITEMS_PER_PAGE = 5

            with patch('handlers.catalog.get_db_session', return_value=mock_db):
                show_catalog(mock_message, mock_bot)

                # Verify bot sent message with inline keyboard
                mock_bot.send_message.assert_called_once()

                call_args = mock_bot.send_message.call_args
                assert call_args[0][0] == 123456

    def test_show_catalog_empty(self):
        """Test showing empty catalog."""
        # Create mock chat
        mock_chat = Mock()
        mock_chat.id = 123456

        # Mock message
        mock_message = Mock(spec=types.Message)
        mock_message.chat = mock_chat

        # Mock bot
        mock_bot = Mock()
        mock_bot.send_message = Mock()

        # Mock empty database
        mock_db = Mock()
        mock_db.query.return_value.all.return_value = []
        mock_db.close = Mock()

        with patch('handlers.catalog.get_db_session', return_value=mock_db):
            show_catalog(mock_message, mock_bot)

            # Verify bot sent empty catalog message
            mock_bot.send_message.assert_called_once()


class TestConfig:
    """Test configuration."""

    def test_admin_check(self):
        """Test admin user verification."""
        # Test admin user
        Config.ADMIN_IDS = [123456, 789012]

        assert Config.is_admin(123456) == True
        assert Config.is_admin(789012) == True

        # Test non-admin user
        assert Config.is_admin(999999) == False


# Run with: pytest tests/test_handlers.py -v --cov=handlers
if __name__ == "__main__":
    pytest.main([__file__, "-v"])