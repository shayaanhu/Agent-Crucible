from __future__ import annotations

import json
from pathlib import Path

from agents.red_team import get_red_team_agent


def test_dataset_objectives_run() -> None:
    dataset_path = Path("eval/fixtures/red_team_objectives.json")
    objectives = json.loads(dataset_path.read_text(encoding="utf-8"))
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
        },
    )
    assert trace.metadata.get("objective_goal") == first["goal"]
