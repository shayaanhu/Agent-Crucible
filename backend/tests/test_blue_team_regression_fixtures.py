from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.blue.blue_team import get_blue_team_agent
from backend.app.pipeline import _enforce_guardrail_action


def _load_cases() -> list[dict]:
    fixture_path = Path("backend/tests/fixtures/blue_team/regression_cases.json")
    return json.loads(fixture_path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_blue_team_regression_cases(case: dict) -> None:
    agent = get_blue_team_agent()
    verdict = agent.evaluate_output(case["model_output"])

    assert verdict.policy_id == case["expected_policy_id"]
    assert verdict.action == case["expected_action"]
    assert verdict.allowed is case["expected_verdict_allowed"]

    effective_allowed, effective_action, _, effective_output, detector_results = (
        _enforce_guardrail_action(case["model_output"], verdict, dry_run=False)
    )

    assert effective_allowed is case["expected_effective_allowed"]
    assert effective_action == case["expected_action"]
    assert case["expected_output_contains"] in effective_output
    assert isinstance(detector_results, dict)
    assert "rule_detector" in detector_results
