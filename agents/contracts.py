from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


@dataclass(frozen=True)
class BlueTeamVerdict:
    allowed: bool
    category: str
    confidence: float
    reason: str


@dataclass(frozen=True)
class RedTeamTurn:
    turn_index: int
    prompt: str
    response: str
    strategy_id: str
    attack_tag: str
    prompt_hash: str


@dataclass(frozen=True)
class RedTeamRunTrace:
    strategy_id: str
    turns: List[RedTeamTurn]
    stop_reason: str
    risk_tags: List[str]
    metadata: Dict[str, Any]


class RedTeamContract(Protocol):
    def build_attack_prompt(self, scenario: str, goal: str) -> str:
        ...

    def list_strategies(self) -> list[str]:
        ...

    def run_attack(
        self,
        scenario: str,
        goal: str,
        max_turns: int,
        provider: str,
        metadata: Dict[str, str] | None = None,
    ) -> RedTeamRunTrace:
        ...


class BlueTeamContract(Protocol):
    def evaluate_output(self, model_output: str) -> BlueTeamVerdict:
        ...
