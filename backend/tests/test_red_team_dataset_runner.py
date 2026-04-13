from __future__ import annotations

import json
from pathlib import Path

from agents.red.red_team import get_red_team_agent


def test_dataset_objectives_run() -> None:
    dataset_path = Path("eval/fixtures/red_team_objectives.json")
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    objectives = payload["cases"]
    agent = get_red_team_agent()
    first = objectives[0]
    trace = agent.run_attack(
        scenario=first["scenario"],
        goal=first["goal"],
        max_turns=1,
        provider="mock",
        metadata={
            "strategy_id": first["strategy_id"],
            "objective_goal": first["goal"],
            "objective_success_tokens": first["objective_success_tokens"],
            "objective_block_tokens": first["objective_block_tokens"],
            "objective_tags": first["objective_tags"],
            "objective_category": first["category"],
            "objective_difficulty": first["difficulty"],
        },
    )
    assert trace.metadata.get("objective_goal") == first["goal"]
    assert trace.metadata.get("objective_category") == first["category"]
    assert trace.metadata.get("objective_difficulty") == first["difficulty"]
