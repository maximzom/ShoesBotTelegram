"""
Rate limiting utilities to prevent abuse.
"""
import time
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter.

    Tracks requests per user and enforces limits.
    """

    def __init__(
            self,
            max_requests: int = 20,
            window_seconds: int = 60,
            ban_duration: int = 300
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
            ban_duration: Ban duration in seconds for violators
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ban_duration = ban_duration

        # Store requests per user: {user_id: [timestamp1, timestamp2, ...]}
        self.requests: Dict[int, List[float]] = defaultdict(list)

        # Store bans: {user_id: ban_until_timestamp}
        self.bans: Dict[int, float] = {}

    def is_allowed(self, user_id: int) -> bool:
        """
        Check if user is allowed to make a request.

        Args:
            user_id: Telegram user ID

        Returns:
            True if allowed, False if rate limited
        """
        current_time = time.time()

        # Check if user is banned
        if user_id in self.bans:
            ban_until = self.bans[user_id]
            if current_time < ban_until:
                logger.warning(f"User {user_id} is banned until {datetime.fromtimestamp(ban_until)}")
                return False
            else:
                # Ban expired
                del self.bans[user_id]

        # Clean old requests
        window_start = current_time - self.window_seconds
        if user_id in self.requests:
            self.requests[user_id] = [
                ts for ts in self.requests[user_id]
                if ts > window_start
            ]

        # Check request count
        request_count = len(self.requests.get(user_id, []))

        if request_count >= self.max_requests:
            # Ban user for exceeding rate limit
            self.bans[user_id] = current_time + self.ban_duration
            logger.warning(f"User {user_id} rate limited. Ban until {datetime.fromtimestamp(self.bans[user_id])}")
            return False

        return True

    def record_request(self, user_id: int) -> None:
        """
        Record a request from user.

        Args:
            user_id: Telegram user ID
        """
        current_time = time.time()
        self.requests[user_id].append(current_time)

        # Keep only requests from current window
        window_start = current_time - self.window_seconds
        self.requests[user_id] = [
            ts for ts in self.requests[user_id]
            if ts > window_start
        ]

    def get_user_stats(self, user_id: int) -> Dict:
        """
        Get rate limiting statistics for user.

        Args:
            user_id: Telegram user ID

        Returns:
            Dictionary with statistics
        """
        current_time = time.time()

        if user_id in self.bans:
            is_banned = current_time < self.bans[user_id]
            ban_until = self.bans[user_id] if is_banned else None
        else:
            is_banned = False
            ban_until = None

        # Count requests in current window
        window_start = current_time - self.window_seconds
        recent_requests = [
            ts for ts in self.requests.get(user_id, [])
            if ts > window_start
        ]

        return {
            'user_id': user_id,
            'is_banned': is_banned,
            'ban_until': ban_until,
            'requests_in_window': len(recent_requests),
            'max_requests': self.max_requests,
            'window_seconds': self.window_seconds
        }

    def clear_old_data(self, older_than_hours: int = 24) -> int:
        """
        Clear old data to prevent memory leaks.

        Args:
            older_than_hours: Clear data older than this

        Returns:
            Number of users cleared
        """
        current_time = time.time()
        cutoff = current_time - (older_than_hours * 3600)

        cleared_users = 0

        # Clear old requests
        for user_id in list(self.requests.keys()):
            self.requests[user_id] = [
                ts for ts in self.requests[user_id]
                if ts > cutoff
            ]

            # Remove user if no recent requests
            if not self.requests[user_id]:
                del self.requests[user_id]
                cleared_users += 1

        # Clear expired bans
        for user_id in list(self.bans.keys()):
            if current_time > self.bans[user_id]:
                del self.bans[user_id]
                cleared_users += 1

        logger.info(f"Cleared data for {cleared_users} users")
        return cleared_users


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit_decorator(func):
    """
    Decorator to apply rate limiting to bot handlers.

    Args:
        func: Function to decorate

    Returns:
        Wrapped function
    """

    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id

        if not rate_limiter.is_allowed(user_id):
            from utils.locales import MSG
            bot = args[0] if args else kwargs.get('bot')
            if bot:
                bot.send_message(message.chat.id, MSG.RATE_LIMIT_EXCEEDED)
            return

        # Record the request
        rate_limiter.record_request(user_id)

        # Call the original function
        return func(message, *args, **kwargs)

    return wrapper


def get_rate_limit_stats(user_id: int) -> Dict:
    """
    Get rate limiting statistics for user.

    Args:
        user_id: Telegram user ID

    Returns:
        Dictionary with statistics
    """
    return rate_limiter.get_user_stats(user_id)