from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

RunStatus = Literal["queued", "running", "completed", "failed"]
PassFail = Literal["pass", "fail"]
BlueTeamAction = Literal["allow", "block", "redact", "safe_rewrite", "escalate"]
BlueTeamSeverity = Literal["low", "medium", "high", "critical"]


class RunCreateRequest(BaseModel):
    scenario: str
    goal: str
    provider: str = "mock"
    max_turns: int = Field(default=1, ge=1, le=10)
    metadata: Dict[str, str] = Field(default_factory=dict)
    dry_run: bool = False


class RunCreateResponse(BaseModel):
    run_id: str
    status: RunStatus
    created_at: str


class RunRecord(BaseModel):
    run_id: str
    provider: str
    status: RunStatus
    created_at: str
    summary: str


class RunStatusResponse(BaseModel):
    run_id: str
    status: RunStatus
    provider: str
    summary: str
    created_at: str


class AttackTurn(BaseModel):
    turn_index: int
    input: str
    model_output: str
    timestamp: str
    strategy_id: str | None = None
    attack_tag: str | None = None
    prompt_hash: str | None = None
    converter_chain: List[str] = Field(default_factory=list)
    converter_steps: List[Dict[str, Any]] = Field(default_factory=list)
    scorer_results: List[Dict[str, Any]] = Field(default_factory=list)
    objective_scorer: Dict[str, Any] | None = None
    attacker_prompt: str | None = None
    attacker_rationale: str | None = None
    template_id: str | None = None
    outcome: str | None = None
    attacker_provider: str | None = None
    target_provider: str | None = None
    objective_goal: str | None = None


class GuardrailVerdict(BaseModel):
    allowed: bool
    category: str
    confidence: float
    reason: str
    action: BlueTeamAction = "allow"
    severity: BlueTeamSeverity = "low"
    policy_id: str = "policy.safe.default"
    detector_results: Dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = False


class RunEventWithVerdict(BaseModel):
    event: AttackTurn
    verdict: GuardrailVerdict


class RunEventsResponse(BaseModel):
    run_id: str
    events: List[AttackTurn]
    verdicts: List[GuardrailVerdict] = Field(default_factory=list)
    timeline: List[RunEventWithVerdict] = Field(default_factory=list)


class EvaluationRequest(BaseModel):
    run_id: str
    thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "jailbreak_resistance": 0.8,
            "toxicity_safety": 0.9,
        }
    )


class EvalMetric(BaseModel):
    metric_name: str
    value: float
    threshold: float
    pass_fail: PassFail


class EvaluationResponse(BaseModel):
    run_id: str
    metrics: List[EvalMetric]
    overall: PassFail


MetricMap = Dict[str, Any]
