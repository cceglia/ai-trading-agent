from __future__ import annotations

import pytest

from src.analysis.market_structure_engine.deterministic_validator import DeterministicValidator
from src.analysis.market_structure_engine.models import (
    BlockerSeverity,
    DeterministicSetupState,
    EntryType,
    ExecutionBlocker,
    ExecutionBlockerCode,
    ExecutionBlockerType,
    ExecutionPolicyState,
    GeometryStatus,
    SetupClassificationStatus,
    SetupLifecycleStatus,
    TradeDirection,
)
from src.analysis.market_structure_engine.utils import stable_id


def _setup(**overrides: object) -> DeterministicSetupState:
    values: dict[str, object] = {
        "setup_classification_status": SetupClassificationStatus.CLASSIFIED,
        "setup_lifecycle_status": SetupLifecycleStatus.TRIGGERED,
        "trade_direction": TradeDirection.BULLISH,
        "geometry_status": GeometryStatus.VALID,
        "current_price": 100.0,
        "entry_price": 101.0,
        "invalidation_price": 99.0,
        "target_price": 105.0,
        "estimated_reward_risk": 2.0,
        "entry_type": EntryType.STOP,
        "invalidation_level_id": stable_id("level", "LOW", "99.0000000000", "s-1"),
        "invalidation_timeframe": "H1",
    }
    values.update(overrides)
    return DeterministicSetupState(**values)


def _selected_level(**overrides: object) -> dict[str, object]:
    level: dict[str, object] = {
        "level_id": stable_id("level", "LOW", "99.0000000000", "s-1"),
        "side": "LOW",
        "price": 99.0,
        "source_swing_ids": ["s-1"],
        "eligible_for_invalidation": True,
        "current_status": "FRESH",
        "freshness": "FRESH",
        "age_bars": 1,
        "break_count": 0,
        "reclaim_count": 0,
        "accepted_beyond_count": 0,
        "accepted_beyond": False,
    }
    level.update(overrides)
    return level


def test_validator_exposes_canonical_long_contract() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        policy=ExecutionPolicyState(trade_direction=TradeDirection.BULLISH),
        action="buy_setup",
    )

    assert result.validation_status == "VALID"
    assert result.direction == "LONG"
    assert result.setup_status == "READY"
    assert result.calculated_rr == 2.0
    assert result.minimum_required_rr == 2.0
    assert result.rr_pass is True
    assert result.entry_authorized is False


def test_validator_rejects_supplied_action_not_allowed_by_policy() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        policy=ExecutionPolicyState(),
        action="buy_setup",
    )

    assert result.validation_status == "INVALID"
    assert "POLICY_ACTION_NOT_ALLOWED" in result.reason_codes


def test_validator_rejects_non_monotonic_full_event_history() -> None:
    structure_analysis = {
        "timeframes": {
            "H1": {
                "source_audit": {"candle_closure_verified": True},
                "events": {
                    "event_history": [
                        {
                            "event_index": 4,
                            "timestamp": "2026-08-07T04:00:00+00:00",
                            "structural_scope": "PRIMARY",
                        },
                        {
                            "event_index": 3,
                            "timestamp": "2026-08-07T03:00:00+00:00",
                            "structural_scope": "PRIMARY",
                        },
                    ]
                },
            }
        }
    }

    result = DeterministicValidator().validate(
        setup=_setup(),
        policy=ExecutionPolicyState(),
        action="buy_setup",
        structure_analysis=structure_analysis,
    )

    assert result.validation_status == "INVALID"
    assert "EVENT_CHRONOLOGY_INVALID" in result.reason_codes


@pytest.mark.parametrize("event_index", [None, 1.5, float("nan"), float("inf"), -1, True])
def test_validator_rejects_malformed_event_indices(event_index: object) -> None:
    event = {
        "timestamp": "2026-08-07T04:00:00+00:00",
        "structural_scope": "PRIMARY",
    }
    if event_index is not None:
        event["event_index"] = event_index

    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {"event_history": [event]},
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "EVENT_CHRONOLOGY_INVALID" in result.reason_codes


def test_validator_rejects_unknown_action_without_policy() -> None:
    result = DeterministicValidator().validate(setup=_setup(), action="cancel_order")

    assert result.validation_status == "INVALID"
    assert "ACTION_INVALID" in result.reason_codes


@pytest.mark.parametrize(
    ("level_update", "setup_update", "reason_code"),
    [
        ({"side": "HIGH"}, {}, "INVALIDATION_LEVEL_DIRECTION_MISMATCH"),
        ({}, {"invalidation_timeframe": "H4"}, "INVALIDATION_LEVEL_TIMEFRAME_MISMATCH"),
        ({"level_id": "not-canonical"}, {}, "INVALIDATION_LEVEL_IDENTITY_INVALID"),
    ],
)
def test_validator_requires_directional_timeframe_canonical_invalidation_level(
    level_update: dict[str, object],
    setup_update: dict[str, object],
    reason_code: str,
) -> None:
    result = DeterministicValidator().validate(
        setup=_setup(**setup_update),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {"event_history": []},
                    "levels": {
                        "support_levels": [_selected_level(**level_update)],
                        "resistance_levels": [],
                    },
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert reason_code in result.reason_codes


def test_validator_rejects_invalid_latest_material_event_projection() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {
                        "event_history": [
                            {
                                "event_index": 1,
                                "timestamp": "2026-08-07T04:00:00+00:00",
                                "structural_scope": "PRIMARY",
                            }
                        ],
                        "latest_material_event": {
                            "event_index": 0,
                            "timestamp": "not-a-timestamp",
                            "structural_scope": "PRIMARY",
                        },
                    },
                    "levels": {"support_levels": [_selected_level()], "resistance_levels": []},
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "INVALID_TIMESTAMP" in result.reason_codes


def test_validator_rejects_non_chronological_latest_material_event_projection() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {
                        "event_history": [
                            {
                                "event_index": 1,
                                "timestamp": "2026-08-07T04:00:00+00:00",
                                "structural_scope": "PRIMARY",
                            }
                        ],
                        "latest_material_event": {
                            "event_index": 0,
                            "timestamp": "2026-08-07T03:00:00+00:00",
                            "structural_scope": "PRIMARY",
                        },
                    },
                    "levels": {"support_levels": [_selected_level()], "resistance_levels": []},
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "EVENT_PROJECTION_CHRONOLOGY_INVALID" in result.reason_codes


def test_validator_rejects_lifecycle_counter_status_contradiction() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {"event_history": []},
                    "levels": {
                        "support_levels": [
                            _selected_level(reclaim_count=1, current_status="FRESH")
                        ],
                        "resistance_levels": [],
                    },
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "INVALIDATION_LEVEL_CONTRADICTION" in result.reason_codes


@pytest.mark.parametrize(
    "event_update",
    [
        {"broken_level": None},
        {"confirming_close": None},
        {"broken_level": "100.0", "confirming_close": 101.0},
    ],
)
def test_validator_rejects_incomplete_or_malformed_bos_evidence(
    event_update: dict[str, object],
) -> None:
    event = {
        "event_index": 1,
        "event_type": "BULLISH_BOS",
        "structural_scope": "PRIMARY",
        "timestamp": "2026-08-07T04:00:00+00:00",
        "broken_level": 100.0,
        "confirming_close": 101.0,
    }
    event.update(event_update)
    for field, value in event_update.items():
        if value is None:
            event.pop(field)

    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "technical_context": {"atr_14": 1.0},
                    "calculation_metadata": {"profile": {"bos_close_buffer_atr": 0.1}},
                    "events": {"event_history": [event]},
                    "levels": {"support_levels": [_selected_level()], "resistance_levels": []},
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert any(
        code in result.reason_codes
        for code in ("BREAKOUT_EVIDENCE_INCOMPLETE", "MALFORMED_BREAKOUT_NUMERIC")
    )


def test_validator_returns_structured_invalid_for_huge_breakout_integer() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "technical_context": {"atr_14": 1.0},
                    "calculation_metadata": {"profile": {"bos_close_buffer_atr": 0.1}},
                    "events": {
                        "event_history": [
                            {
                                "event_index": 1,
                                "event_type": "BULLISH_BOS",
                                "structural_scope": "PRIMARY",
                                "timestamp": "2026-08-07T04:00:00+00:00",
                                "broken_level": 10**10000,
                                "confirming_close": 101.0,
                            }
                        ]
                    },
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "MALFORMED_BREAKOUT_NUMERIC" in result.reason_codes


def test_validator_rejects_latest_projection_with_inconsistent_event_index() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {
                        "event_history": [
                            {
                                "event_index": 4,
                                "timestamp": "2026-08-07T04:00:00+00:00",
                                "structural_scope": "PRIMARY",
                            }
                        ],
                        "latest_material_event": {
                            "event_index": 5,
                            "timestamp": "2026-08-07T04:00:00+00:00",
                            "structural_scope": "PRIMARY",
                        },
                    },
                    "levels": {"support_levels": [_selected_level()], "resistance_levels": []},
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "EVENT_PROJECTION_CHRONOLOGY_INVALID" in result.reason_codes


@pytest.mark.parametrize(
    "projection_name",
    ["latest_material_event", "latest_primary_event", "latest_internal_event"],
)
def test_validator_rejects_latest_event_projection_content_drift(
    projection_name: str,
) -> None:
    canonical_events = [
        {
            "event_id": "event-1",
            "event_index": 1,
            "event_type": "BULLISH_BOS",
            "direction": "BULLISH",
            "structural_scope": "PRIMARY",
            "timestamp": "2026-08-07T04:00:00+00:00",
        },
        {
            "event_id": "event-2",
            "event_index": 2,
            "event_type": "BEARISH_CHOCH",
            "direction": "BEARISH",
            "structural_scope": "INTERNAL",
            "timestamp": "2026-08-07T05:00:00+00:00",
        },
    ]
    projection = canonical_events[-1 if projection_name != "latest_primary_event" else 0].copy()
    projection["event_type"] = "BULLISH_CHOCH"

    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {
                        "event_history": canonical_events,
                        projection_name: projection,
                    },
                    "levels": {"support_levels": [_selected_level()], "resistance_levels": []},
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "EVENT_PROJECTION_CONTENT_INVALID" in result.reason_codes


def test_validator_rejects_scope_history_projection_content_drift() -> None:
    canonical_event = {
        "event_id": "event-1",
        "event_index": 1,
        "event_type": "BULLISH_BOS",
        "direction": "BULLISH",
        "structural_scope": "PRIMARY",
        "timestamp": "2026-08-07T04:00:00+00:00",
    }
    drifted_event = {**canonical_event, "event_type": "BULLISH_CHOCH"}

    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {
                        "event_history": [canonical_event],
                        "primary_events": [drifted_event],
                    },
                    "levels": {"support_levels": [_selected_level()], "resistance_levels": []},
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "EVENT_PROJECTION_CONTENT_INVALID" in result.reason_codes


def test_validator_accepts_independently_bounded_mixed_scope_histories() -> None:
    complete_history = [
        {
            "event_id": f"event-{index}",
            "event_index": index,
            "event_type": "STRUCTURAL_BREAK",
            "direction": "BULLISH",
            "structural_scope": "PRIMARY" if index % 2 else "INTERNAL",
            "timestamp": f"2026-08-{7 + index // 24:02d}T{index % 24:02d}:00:00+00:00",
        }
        for index in range(51)
    ]
    primary_events = [event for event in complete_history if event["structural_scope"] == "PRIMARY"]
    internal_events = [
        event for event in complete_history if event["structural_scope"] == "INTERNAL"
    ]

    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {
                        "event_history": complete_history[-50:],
                        "primary_events": primary_events,
                        "internal_events": internal_events,
                    },
                    "levels": {
                        "support_levels": [_selected_level(touch_count=1)],
                        "resistance_levels": [],
                    },
                }
            }
        },
    )

    assert result.validation_status == "VALID"


@pytest.mark.parametrize(
    "counter_update",
    [
        {"break_count": 1.5},
        {"reclaim_count": -1},
        {"accepted_beyond_count": 1},
    ],
)
def test_validator_rejects_invalid_level_lifecycle_counters(
    counter_update: dict[str, object],
) -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {"event_history": []},
                    "levels": {
                        "support_levels": [_selected_level(**counter_update)],
                        "resistance_levels": [],
                    },
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert any(
        code in result.reason_codes
        for code in ("INVALIDATION_LEVEL_LIFECYCLE_INVALID", "INVALIDATION_LEVEL_CONTRADICTION")
    )


def test_validator_rejects_action_direction_and_geometry() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(target_price=98.0),
        policy=ExecutionPolicyState(),
        action="sell_setup",
    )

    assert result.validation_status == "INVALID"
    assert "ACTION_DIRECTION_MISMATCH" in result.reason_codes
    assert result.rr_pass is False


def test_ready_setup_with_blocker_is_invalid() -> None:
    blocker = ExecutionBlocker(
        blocker_type=ExecutionBlockerType.GEOMETRY,
        code=ExecutionBlockerCode.GEOMETRY_INVALID,
        reason="bad geometry",
        severity=BlockerSeverity.INVALIDATES_GRADE,
    )
    result = DeterministicValidator().validate(
        setup=_setup(),
        policy=ExecutionPolicyState(execution_blockers=(blocker,)),
    )

    assert result.validation_status == "INVALID"
    assert "READY_HAS_BLOCKERS" in result.reason_codes


def test_validator_returns_structured_invalid_for_mixed_timestamp_timezone() -> None:
    structure_analysis = {
        "timeframes": {
            "H1": {
                "source_audit": {"candle_closure_verified": True},
                "events": {
                    "event_history": [
                        {"timestamp": "2026-08-07T04:00:00", "structural_scope": "PRIMARY"},
                        {
                            "timestamp": "2026-08-07T05:00:00+00:00",
                            "structural_scope": "PRIMARY",
                        },
                    ]
                },
            }
        }
    }

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis=structure_analysis
    )

    assert result.validation_status == "INVALID"
    assert "INVALID_TIMESTAMP" in result.reason_codes


@pytest.mark.parametrize(
    "history_path",
    [
        ("events", "all_canonical_events"),
        ("events", "primary_events"),
        ("events", "internal_events"),
        ("events", "failed_breakouts"),
        ("liquidity", "event_history"),
    ],
)
def test_validator_rejects_malformed_secondary_history_timestamps(
    history_path: tuple[str, str],
) -> None:
    category, history_name = history_path
    raw: dict[str, object] = {
        "source_audit": {"candle_closure_verified": True},
        "events": {"event_history": []},
        "liquidity": {"event_history": []},
    }
    raw[category] = {history_name: [{"timestamp": "not-a-timestamp"}]}
    structure_analysis = {"timeframes": {"H1": raw}}

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis=structure_analysis
    )

    assert result.validation_status == "INVALID"
    assert "INVALID_TIMESTAMP" in result.reason_codes


@pytest.mark.parametrize(
    "raw_update",
    [
        {"events": []},
        {"events": {"primary_events": {"timestamp": "2026-08-07T04:00:00+00:00"}}},
        {"liquidity": []},
        {"liquidity": {"event_history": {"event_index": 1}}},
        {"liquidity": {"pools": {"event_history": []}}},
    ],
)
def test_validator_returns_structured_invalid_for_malformed_evidence_shapes(
    raw_update: dict[str, object],
) -> None:
    raw: dict[str, object] = {
        "source_audit": {"candle_closure_verified": True},
        "events": {"event_history": []},
        "liquidity": {"event_history": [], "pools": []},
    }
    raw.update(raw_update)

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis={"timeframes": {"H1": raw}}
    )

    assert result.validation_status == "INVALID"
    assert "MALFORMED_EVIDENCE_SHAPE" in result.reason_codes


def test_validator_returns_structured_invalid_for_malformed_history_item() -> None:
    structure_analysis = {
        "timeframes": {
            "H1": {
                "source_audit": {"candle_closure_verified": True},
                "events": {"event_history": ["not-an-event"]},
            }
        }
    }

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis=structure_analysis
    )

    assert result.validation_status == "INVALID"
    assert "MALFORMED_EVIDENCE_SHAPE" in result.reason_codes


@pytest.mark.parametrize(
    "field_update",
    [
        {"source_audit": ["not-an-audit"]},
        {"technical_context": ["not-technical-context"]},
        {"calculation_metadata": ["not-calculation-metadata"]},
        {"calculation_metadata": {"profile": ["not-a-profile"]}},
    ],
)
def test_validator_returns_structured_invalid_for_malformed_context_containers(
    field_update: dict[str, object],
) -> None:
    raw: dict[str, object] = {
        "source_audit": {"candle_closure_verified": True},
        "events": {"event_history": []},
        "technical_context": {"atr_14": 1.0},
        "calculation_metadata": {"profile": {"bos_close_buffer_atr": 0.0}},
    }
    raw.update(field_update)

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis={"timeframes": {"H1": raw}}
    )

    assert result.validation_status == "INVALID"
    assert "MALFORMED_EVIDENCE_SHAPE" in result.reason_codes


def test_ready_setup_requires_matching_lifecycle_level_evidence() -> None:
    structure_analysis = {
        "timeframes": {
            "H1": {
                "source_audit": {"candle_closure_verified": True},
                "events": {"event_history": []},
                "levels": {"support_levels": [], "resistance_levels": []},
            }
        }
    }

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis=structure_analysis
    )

    assert result.validation_status == "INVALID"
    assert "INVALIDATION_LEVEL_EVIDENCE_MISSING" in result.reason_codes


@pytest.mark.parametrize(
    "history_name",
    ["primary_events", "internal_events", "all_canonical_events", "failed_breakouts"],
)
def test_validator_rejects_scope_loss_in_every_event_history_projection(
    history_name: str,
) -> None:
    structure_analysis = {
        "timeframes": {
            "H1": {
                "source_audit": {"candle_closure_verified": True},
                "events": {
                    "event_history": [],
                    history_name: [{"event_index": 1, "timestamp": "2026-08-07T01:00:00+00:00"}],
                },
            }
        }
    }

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis=structure_analysis
    )

    assert result.validation_status == "INVALID"
    assert "EVENT_SCOPE_LOST" in result.reason_codes


@pytest.mark.parametrize(
    "liquidity_update",
    [
        {"scope": None},
        {"scope": "UNKNOWN"},
    ],
)
def test_validator_rejects_missing_or_unknown_liquidity_event_scope(
    liquidity_update: dict[str, object],
) -> None:
    event = {
        "event_index": 1,
        "timestamp": "2026-08-07T01:00:00+00:00",
        "event_type": "SWEPT",
        "scope": "EXTERNAL",
    }
    event.update(liquidity_update)

    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {"event_history": []},
                    "liquidity": {"event_history": [event]},
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "LIQUIDITY_SCOPE_LOST" in result.reason_codes


def test_validator_rejects_scope_loss_in_liquidity_pool_history() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {"event_history": []},
                    "liquidity": {
                        "event_history": [],
                        "pools": [{"event_history": [{"event_index": 1}]}],
                    },
                }
            }
        },
    )

    assert result.validation_status == "INVALID"
    assert "LIQUIDITY_SCOPE_LOST" in result.reason_codes


def test_validator_requires_explicit_eligibility_for_selected_level() -> None:
    structure_analysis = {
        "timeframes": {
            "H1": {
                "source_audit": {"candle_closure_verified": True},
                "events": {"event_history": []},
                "levels": {
                    "support_levels": [
                        {
                            "price": 99.0,
                            "current_status": "FRESH",
                            "freshness": "FRESH",
                            "age_bars": 1,
                            "break_count": 0,
                            "reclaim_count": 0,
                            "accepted_beyond": False,
                        }
                    ],
                    "resistance_levels": [],
                },
            }
        }
    }

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis=structure_analysis
    )

    assert result.validation_status == "INVALID"
    assert "INVALIDATION_LEVEL_INELIGIBLE" in result.reason_codes


def test_validator_requires_complete_lifecycle_evidence_for_selected_level() -> None:
    structure_analysis = {
        "timeframes": {
            "H1": {
                "source_audit": {"candle_closure_verified": True},
                "events": {"event_history": []},
                "levels": {
                    "support_levels": [
                        {
                            "price": 99.0,
                            "eligible_for_invalidation": True,
                            "current_status": "FRESH",
                            "freshness": "FRESH",
                            "age_bars": 1,
                            "break_count": 0,
                            "accepted_beyond": False,
                        }
                    ],
                    "resistance_levels": [],
                },
            }
        }
    }

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis=structure_analysis
    )

    assert result.validation_status == "INVALID"
    assert "INVALIDATION_LEVEL_EVIDENCE_INCOMPLETE" in result.reason_codes


@pytest.mark.parametrize(
    "level_fields",
    [
        {"current_status": "STALE", "age_bars": 1},
        {"current_status": "FRESH", "age_bars": 101},
        {"current_status": "FRESH", "accepted_beyond": True},
    ],
)
def test_validator_rejects_contradictory_eligible_levels(
    level_fields: dict[str, object],
) -> None:
    level = {"price": 99.0, "eligible_for_invalidation": True, **level_fields}
    structure_analysis = {
        "timeframes": {
            "H1": {
                "source_audit": {"candle_closure_verified": True},
                "events": {"event_history": []},
                "levels": {"support_levels": [level], "resistance_levels": []},
            }
        }
    }

    result = DeterministicValidator().validate(
        setup=_setup(), structure_analysis=structure_analysis
    )

    assert result.validation_status == "INVALID"
    assert "INVALIDATION_LEVEL_CONTRADICTION" in result.reason_codes
