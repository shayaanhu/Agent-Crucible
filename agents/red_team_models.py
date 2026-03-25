from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from agents.red_team_objective import Objective


@dataclass
class AttackState:
    scenario: str
    goal: str
    turn_index: int
    max_turns: int
    history: List[dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    strategy_id: str = ""
    last_response: str = ""
    last_outcome: str = ""
    template_index: int = 0
    objective: Objective | None = None
    attacker_provider: str = ""
    attacker_model: str = ""
    objective_scorer_provider: str = ""
    objective_scorer_model: str = ""
    objective_scorer_prompt: str = ""
    blocked_streak: int = 0
    no_success_streak: int = 0
    last_objective_reason: str = ""

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


@dataclass(frozen=True)
class StrategyTemplate:
    template_id: str
    description: str
    prompt_template: str
    attack_tag: str


@dataclass
class AttackUpdate:
    tags: List[str] = field(default_factory=list)
    stop: bool = False
    stop_reason: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
