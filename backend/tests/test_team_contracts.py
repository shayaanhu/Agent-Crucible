from __future__ import annotations

from agents.blue_team import get_blue_team_agent
from agents.mock_provider import get_provider
from agents.red_team import get_red_team_agent


def test_red_blue_provider_contract_integration() -> None:
    red = get_red_team_agent()
    blue = get_blue_team_agent()
    provider = get_provider("mock")

    prompt = red.build_attack_prompt("student assistant", "bypass restrictions")
    output = provider.send_prompt(prompt, {"max_turns": 1})
    verdict = blue.evaluate_output(output)

    assert isinstance(prompt, str) and len(prompt) > 0
    assert isinstance(output, str) and len(output) > 0
    assert isinstance(verdict.allowed, bool)
    assert isinstance(verdict.category, str)
    assert 0.0 <= verdict.confidence <= 1.0
    assert isinstance(verdict.reason, str) and len(verdict.reason) > 0
