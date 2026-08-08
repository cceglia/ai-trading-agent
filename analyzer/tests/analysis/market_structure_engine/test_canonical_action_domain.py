"""Canonical decision-action domain (DEC-002) regression tests.

Covers finding from the v2 review: ``wait_for_setup`` must no longer exist
in the canonical ``DecisionAction`` enum (nor ``WAIT_FOR_*`` in the entry
type enum), while legacy persisted files containing the ``wait_for_setup``
string must still be read safely and normalized to ``no_trade``.
"""

import json
from datetime import datetime

from src.analysis.market_structure_engine.models import DecisionAction, EntryType
from src.output.result_models import AnalysisResult
from src.output.result_writer import ResultWriter, _resolve_action


def test_canonical_action_set_is_exactly_buy_sell_no_trade():
    """The canonical decision-action domain is exactly three values (DEC-002)."""
    assert {member.value for member in DecisionAction} == {
        "buy_setup",
        "sell_setup",
        "no_trade",
    }


def test_decision_action_has_no_wait_for_setup_member():
    """``wait_for_setup`` is removed from the canonical enum."""
    assert not hasattr(DecisionAction, "WAIT_FOR_SETUP")
    assert "wait_for_setup" not in {member.value for member in DecisionAction}


def test_entry_type_has_no_wait_for_members():
    """``EntryType`` exposes no ``WAIT_FOR_*`` values."""
    wait_values = {member.name for member in EntryType if member.name.startswith("WAIT_FOR_")}
    assert wait_values == set()


def test_resolve_action_normalizes_legacy_wait_for_setup():
    """The legacy ``wait_for_setup`` string collapses to ``no_trade``.

    This is handled by the explicit legacy string mapping in the writer,
    NOT via the canonical enum.
    """
    assert _resolve_action("wait_for_setup") == "no_trade"
    assert _resolve_action(None) == "no_trade"


def test_legacy_wait_for_setup_file_writes_as_no_trade(tmp_path):
    """A legacy ``final_action="wait_for_setup"`` persists as ``no_trade``.

    The v2 envelope accepts only canonical actions, so the legacy string
    must be normalized before persistence (FR-029 / DEC-002).
    """
    result = AnalysisResult(
        symbol="XAUUSD",
        run_id="legacy-run",
        started_at=datetime(2026, 7, 26, 8, 30),
        completed_at=datetime(2026, 7, 26, 8, 31),
        status="success",
        final_action="wait_for_setup",
    )
    written = ResultWriter(tmp_path).write(
        "XAUUSD",
        {"analysis_result": result, "errors": [], "fatal_error": None},
        {},
        datetime(2026, 7, 26, 8, 30),
    )
    assert written is not None
    data = json.loads(written.read_text())
    assert data["decision"]["action"] == "no_trade"
    assert data["deterministic_facts"]["entry_authorized"] is False
