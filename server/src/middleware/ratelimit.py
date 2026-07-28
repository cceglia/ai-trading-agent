"""Sliding-window rate limiter — in-memory, pure Python."""

from __future__ import annotations

import time


class SlidingWindowRateLimiter:
    """In-memory sliding-window rate limiter.

    Tracks request timestamps per client key (e.g. IP address).
    Expired entries are trimmed lazily on each call to ``is_allowed``.
    """

    def __init__(self, max_requests: int = 20, window_seconds: int = 60) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = {}

    def is_allowed(self, client_key: str) -> bool:
        """Return ``True`` if the client may proceed, ``False`` if rate-limited."""
        now = time.monotonic()
        window_start = now - self._window_seconds

        # Get or create bucket
        timestamps = self._buckets.get(client_key)
        if timestamps is None:
            self._buckets[client_key] = [now]
            return True

        # Trim expired timestamps (lazy cleanup)
        valid: list[float] = []
        for ts in timestamps:
            if ts > window_start:
                valid.append(ts)
        timestamps[:] = valid

        if len(timestamps) >= self._max_requests:
            return False

        timestamps.append(now)
        return True

    def cleanup(self) -> None:
        """Remove all expired buckets to free memory."""
        now = time.monotonic()
        window_start = now - self._window_seconds
        expired_keys = [
            key
            for key, timestamps in self._buckets.items()
            if not timestamps or max(timestamps) < window_start
        ]
        for key in expired_keys:
            del self._buckets[key]
