from __future__ import annotations

from agents.blue.blue_team import get_blue_team_agent
from agents.red.red_team import get_red_team_agent


def test_red_blue_contract_integration() -> None:
    red = get_red_team_agent()
    blue = get_blue_team_agent()
    trace = red.run_attack(
        scenario="student assistant",
        goal="bypass restrictions",
        max_turns=3,
        provider="mock",
        metadata={"strategy_id": "direct_jailbreak"},
    )
    assert len(trace.turns) >= 1
    verdict = blue.evaluate_output(trace.turns[0].response)

    assert isinstance(trace.turns[0].prompt, str) and len(trace.turns[0].prompt) > 0
    assert isinstance(trace.turns[0].response, str) and len(trace.turns[0].response) > 0
    assert isinstance(verdict.allowed, bool)
    assert isinstance(verdict.category, str)
    assert 0.0 <= verdict.confidence <= 1.0
    assert isinstance(verdict.reason, str) and len(verdict.reason) > 0
    assert verdict.action in {"allow", "block", "redact", "safe_rewrite", "escalate"}
    assert verdict.severity in {"low", "medium", "high", "critical"}
    assert isinstance(verdict.policy_id, str) and len(verdict.policy_id) > 0
    assert isinstance(verdict.detector_results, dict)

