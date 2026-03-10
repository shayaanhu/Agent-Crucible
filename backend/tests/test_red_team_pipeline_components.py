from __future__ import annotations

from agents.red_team import get_red_team_agent


def test_converter_pipeline_applies() -> None:
    agent = get_red_team_agent()
    trace = agent.run_attack(
        scenario="help desk",
        goal="extract restricted prompt",
        max_turns=1,
        provider="mock",
        metadata={"strategy_id": "direct_jailbreak", "converters": "identity,reframe_audit"},
    )
    assert trace.turns[0].converter_chain == ["identity", "reframe_audit"]


def test_scorer_outputs_present() -> None:
    agent = get_red_team_agent()
    trace = agent.run_attack(
        scenario="help desk",
        goal="extract restricted prompt",
        max_turns=1,
        provider="mock",
        metadata={"strategy_id": "direct_jailbreak", "scorers": "success_pattern,refusal"},
    )
    labels = [item["label"] for item in trace.turns[0].scorer_results]
    assert "success" in labels or "blocked" in labels or "no_success" in labels


def test_orchestrator_switch_on_block() -> None:
    agent = get_red_team_agent()
    trace = agent.run_attack(
        scenario="general assistance",
        goal="explain safe behavior",
        max_turns=2,
        provider="mock",
        metadata={"strategy_id": "multi_step_escalation"},
    )
    strategy_sequence = trace.metadata.get("strategy_sequence", "")
    assert "," in strategy_sequence or strategy_sequence == "multi_step_escalation"
