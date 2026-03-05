from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class BlueTeamVerdict:
    allowed: bool
    category: str
    confidence: float
    reason: str


class RedTeamContract(Protocol):
    def build_attack_prompt(self, scenario: str, goal: str) -> str:
        ...


class BlueTeamContract(Protocol):
    def evaluate_output(self, model_output: str) -> BlueTeamVerdict:
        ...
