from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Objective:
    goal: str
    success_tokens: List[str]
    block_tokens: List[str]
    tags: List[str]

    @staticmethod
    def from_metadata(goal: str, metadata: Dict[str, str]) -> "Objective":
        success_tokens = _parse_csv(metadata.get("objective_success_tokens", ""))
        block_tokens = _parse_csv(metadata.get("objective_block_tokens", ""))
        tags = _parse_csv(metadata.get("objective_tags", ""))
        objective_goal = metadata.get("objective_goal", goal)
        return Objective(
            goal=objective_goal,
            success_tokens=success_tokens,
            block_tokens=block_tokens,
            tags=tags,
        )


def _parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]
