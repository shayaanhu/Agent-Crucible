from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Protocol

BlueTeamAction = Literal["allow", "block", "redact", "safe_rewrite", "escalate"]
BlueTeamSeverity = Literal["low", "medium", "high", "critical"]


@dataclass(frozen=True)
class BlueTeamVerdict:
    allowed: bool
    category: str
    confidence: float
    reason: str
    action: BlueTeamAction = "allow"
    severity: BlueTeamSeverity = "low"
    policy_id: str = "policy.safe.default"
    detector_results: Dict[str, Any] = field(default_factory=dict)
    dry_run: bool = False


@dataclass(frozen=True)
class RedTeamTurn:
    turn_index: int
    prompt: str
    response: str
    strategy_id: str
    attack_tag: str
    prompt_hash: str
    converter_chain: List[str]
    converter_steps: List[Dict[str, Any]]
    scorer_results: List[Dict[str, Any]]
    objective_scorer: Dict[str, Any] | None
    attacker_prompt: str
    attacker_rationale: str
    template_id: str
    outcome: str
    attacker_provider: str
    target_provider: str
    objective_goal: str


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

    def stream_attack(
        self,
        scenario: str,
        goal: str,
        max_turns: int,
        provider: str,
        metadata: Dict[str, str] | None = None,
        on_turn=None,
        on_progress=None,
    ) -> RedTeamRunTrace:
        ...


class BlueTeamContract(Protocol):
    def evaluate_output(self, model_output: str) -> BlueTeamVerdict:
        ...
