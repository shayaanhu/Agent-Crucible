from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.red.red_team import get_red_team_agent


def test_strategy_registry_has_eight_strategies() -> None:
    agent = get_red_team_agent()
    strategy_ids = agent.list_strategies()
    assert len(strategy_ids) == 8
    assert "direct_jailbreak" in strategy_ids
    assert "multi_step_escalation" in strategy_ids


def test_unknown_strategy_fails() -> None:
    agent = get_red_team_agent()
    with pytest.raises(ValueError):
        agent.run_attack(
            scenario="test",
            goal="test",
            max_turns=2,
            provider="mock",
            metadata={"strategy_id": "not_a_strategy"},
        )


def test_multi_turn_respects_max_turns() -> None:
    agent = get_red_team_agent()
    trace = agent.run_attack(
        scenario="help desk bot",
        goal="extract restricted instructions",
        max_turns=2,
        provider="mock",
        metadata={"strategy_id": "multi_step_escalation"},
    )
    assert 1 <= len(trace.turns) <= 2
    assert trace.stop_reason in {"max_turns_reached", "success_detected"}
    assert trace.turns[0].converter_chain
    assert trace.turns[0].scorer_results


def test_fixture_regression_files_are_runnable() -> None:
    agent = get_red_team_agent()
    fixture_dir = Path("eval/fixtures/red_team")
    fixture_files = sorted(fixture_dir.glob("*.json"))
    assert len(fixture_files) == 8
    for fixture_file in fixture_files:
        strategy_id = fixture_file.stem
        cases = json.loads(fixture_file.read_text(encoding="utf-8"))
        assert len(cases) >= 5
        first = cases[0]
        trace = agent.run_attack(
            scenario=first["scenario"],
            goal=first["goal"],
            max_turns=2,
            provider="mock",
            metadata={"strategy_id": strategy_id},
        )
        assert len(trace.turns) >= 1
        strategy_sequence = trace.metadata.get("strategy_sequence", "")
        assert strategy_id in strategy_sequence.split(",")
        assert trace.turns[0].converter_chain
        assert trace.turns[0].scorer_results
