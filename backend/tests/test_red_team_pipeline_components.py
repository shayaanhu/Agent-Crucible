from __future__ import annotations

from agents.red_team import (
    _build_attacker_feedback,
    _response_echoes_wrapped_payload,
    _select_converters,
    get_red_team_agent,
)
from agents.red_team_models import AttackState


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
    assert len(trace.turns[0].converter_steps) == 2


def test_scorer_outputs_present() -> None:
    agent = get_red_team_agent()
    trace = agent.run_attack(
        scenario="help desk",
        goal="extract restricted prompt",
        max_turns=1,
        provider="mock",
        metadata={"strategy_id": "direct_jailbreak", "scorers": "objective_llm,success_pattern,refusal"},
    )
    labels = [item["label"] for item in trace.turns[0].scorer_results]
    assert "success" in labels or "blocked" in labels or "no_success" in labels
    assert trace.turns[0].objective_scorer is not None


def test_orchestrator_stays_on_strategy() -> None:
    agent = get_red_team_agent()
    trace = agent.run_attack(
        scenario="general assistance",
        goal="explain safe behavior",
        max_turns=2,
        provider="mock",
        metadata={"strategy_id": "multi_step_escalation"},
    )
    strategy_sequence = trace.metadata.get("strategy_sequence", "")
    assert strategy_sequence == "multi_step_escalation"


def test_adaptive_converter_selection_prefers_plain_language_after_decode_echo() -> None:
    state = AttackState(
        scenario="test",
        goal="test",
        turn_index=2,
        max_turns=3,
        last_outcome="blocked",
        last_response='Decoded JSON: {"format": "red_team"}',
        blocked_streak=1,
    )
    converters = _select_converters(
        state,
        ["identity", "paraphrase_llm"],
        ["format_wrapper", "encode_wrapper"],
        ["translate_llm"],
    )
    assert converters == ["identity", "paraphrase_llm", "reframe_audit", "translate_llm"]


def test_feedback_mentions_wrapper_failure() -> None:
    state = AttackState(
        scenario="test",
        goal="test",
        turn_index=2,
        max_turns=3,
        history=[{"turn_index": 1}],
        last_outcome="blocked",
        last_response='Decoded JSON: {"format": "red_team"}',
        blocked_streak=1,
        no_success_streak=1,
        last_objective_reason="The target decoded the payload and refused.",
    )
    feedback = _build_attacker_feedback(state)
    assert "decoded or echoed the wrapped payload" in feedback


def test_response_echo_detection_handles_json_echo() -> None:
    assert _response_echoes_wrapped_payload('Decoded JSON:\n```json\n{"format": "red_team"}\n```')
