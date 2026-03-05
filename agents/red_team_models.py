from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AttackState:
    scenario: str
    goal: str
    turn_index: int
    max_turns: int
    history: List[dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    strategy_id: str = ""

    def to_prompt_context(self) -> str:
        if not self.history:
            return "No prior turns."
        lines: List[str] = []
        for item in self.history:
            lines.append(
                f"Turn {item['turn_index']} prompt: {item['prompt']}\n"
                f"Turn {item['turn_index']} response: {item['response']}"
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class StrategyMetadata:
    strategy_id: str
    description: str
    risk_tags: List[str]


@dataclass
class AttackUpdate:
    tags: List[str] = field(default_factory=list)
    stop: bool = False
    stop_reason: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
