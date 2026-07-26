import logging
from typing import Any

from src.analysis.market_structure_engine import analyze_multi_timeframe

logger = logging.getLogger(__name__)


class MarketStructureEngine:
    """Concrete adapter implementing StructureAnalyzer.

    Wraps the module-level analyze_multi_timeframe function from the
    local engine copy.
    """

    def analyze(
        self,
        snapshots: dict[str, Any],
        profile_overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze market structure from snapshots.

        Args:
            snapshots: Dictionary of timeframe snapshots
            profile_overrides: Optional profile overrides

        Returns:
            Analysis result dictionary

        Raises:
            ValueError: If engine output is invalid
        """
        logger.info("Analyzing market structure for timeframes: %s", list(snapshots.keys()))

        request = self._build_request(snapshots, profile_overrides)
        result = self._delegate_to_engine(request)
        self._validate(result)

        logger.info("Analysis complete. Confluence: %s", result.get("confluence", {}))
        return result

    def _build_request(
        self, snapshots: dict[str, Any], overrides: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Build engine request from snapshots."""
        request = {
            "analysis_mode": "MULTI_TIMEFRAME",
            "timeframes": ["D1", "H4", "H1"],
            "snapshots": snapshots,
        }
        if overrides:
            request["profile_overrides"] = overrides
        return request

    def _delegate_to_engine(self, request: dict[str, Any]) -> dict[str, Any]:
        """Delegate analysis to the engine."""
        return analyze_multi_timeframe(request)

    def _validate(self, result: dict[str, Any]) -> None:
        """Validate engine output."""
        if "timeframes" not in result:
            raise ValueError("Engine output missing 'timeframes'")
        if "confluence" not in result:
            raise ValueError("Engine output missing 'confluence'")
        if result["confluence"].get("entry_authorized", True) is not False:
            raise ValueError("entry_authorized must be False - advisory only")
