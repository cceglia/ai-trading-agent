import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None  # type: ignore
    BeautifulSoup = None  # type: ignore
    logger.warning("requests/bs4 not installed; ForexFactory scraping unavailable")


class ForexFactoryCalendar:
    """Economic calendar provider via ForexFactory scraping."""

    BASE_URL = "https://www.forexfactory.com/calendar"

    def __init__(self, cache_hours: int = 4):
        """Initialize calendar provider.

        Args:
            cache_hours: Hours to cache events before refresh
        """
        self.cache_hours = cache_hours
        self._cache: list[dict[str, Any]] = []
        self._cache_time: datetime | None = None

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch upcoming economic calendar events.

        Returns:
            List of event dictionaries with:
            - time: ISO timestamp
            - currency: Currency code (e.g., "USD")
            - impact: "high", "medium", "low"
            - title: Event name
        """
        if self._is_cache_valid():
            logger.debug("Returning cached events (%d events)", len(self._cache))
            return self._cache

        try:
            events = self._scrape_calendar()
            self._cache = events
            self._cache_time = datetime.now()
            logger.info("Fetched %d calendar events", len(events))
            return events
        except Exception as e:
            logger.warning("Calendar scrape failed: %s, using cache", e)
            return self._cache

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache_time is None:
            return False
        return (datetime.now() - self._cache_time) < timedelta(hours=self.cache_hours)

    def _scrape_calendar(self) -> list[dict[str, Any]]:
        """Scrape ForexFactory calendar page."""
        if requests is None or BeautifulSoup is None:
            logger.error("requests/bs4 not installed; cannot scrape")
            return []

        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        response = requests.get(self.BASE_URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        events: list[dict[str, Any]] = []

        rows = soup.select("tr.calendar__row")
        for row in rows:
            event = self._parse_row(row)
            if event:
                events.append(event)

        return events

    def _parse_row(self, row: Any) -> dict[str, Any] | None:
        """Parse a single calendar row into an event dict."""
        time_el = row.select_one("td.calendar__time span")
        currency_el = row.select_one("td.calendar__currency")
        impact_el = row.select_one("td.calendar__impact span")
        title_el = row.select_one("td.calendar__event span")

        if not (time_el and currency_el and title_el):
            return None

        raw_time = time_el.get_text(strip=True)
        time_str = self._parse_time(raw_time)

        impact_text = ""
        if impact_el:
            impact_text = impact_el.get("title", "").lower()
        impact = self._normalize_impact(impact_text)

        return {
            "time": time_str,
            "currency": currency_el.get_text(strip=True).upper(),
            "impact": impact,
            "title": title_el.get_text(strip=True),
        }

    @staticmethod
    def _parse_time(raw_time: str) -> str:
        """Convert raw time text to ISO timestamp (best-effort).

        ForexFactory time cells use formats like ``7:00am`` / ``12:30pm``.
        Anything else (``All Day``, ``Day 1``, ``Tentative``, …) is
        returned unchanged.  Uses the stdlib parser so the analyzer has no
        undeclared runtime dependency on ``dateutil``.
        """
        cleaned = raw_time.strip().replace(" ", "")
        for fmt in ("%I:%M%p", "%I%p", "%H:%M"):
            try:
                return datetime.strptime(cleaned, fmt).isoformat()
            except ValueError:
                continue
        return raw_time

    @staticmethod
    def _normalize_impact(raw: str) -> str:
        """Map raw impact text to standard impact level."""
        raw = raw.lower()
        if "high" in raw:
            return "high"
        if "medium" in raw or "moderate" in raw:
            return "medium"
        return "low"
