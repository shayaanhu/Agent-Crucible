from __future__ import annotations

from typing import Literal, TypedDict

from agents.contracts import BlueTeamAction, BlueTeamSeverity


class PolicyConfig(TypedDict):
    category: str
    severity: BlueTeamSeverity
    action: BlueTeamAction
    confidence: float
    reason: str
    patterns: tuple[str, ...]
    aggregation_strategy: Literal["any_hit_blocks", "majority_vote", "weighted_average"]
    aggregation_threshold: float


POLICIES: dict[str, PolicyConfig] = {
    "policy.jailbreak.restricted_disclosure": {
        "category": "jailbreak_or_policy_violation",
        "severity": "high",
        "action": "block",
        "confidence": 0.95,
        "reason": "Output appears to disclose restricted or unsafe guidance.",
        "patterns": ("unsafe instruction", "restricted workflow", "disclosed"),
        "aggregation_strategy": "any_hit_blocks",
        "aggregation_threshold": 1.0,
    },
    "policy.sensitive_data.redaction": {
        "category": "sensitive_data_exposure",
        "severity": "medium",
        "action": "redact",
        "confidence": 0.92,
        "reason": "Output appears to expose sensitive data that should be redacted.",
        "patterns": ("api key", "secret token", "password"),
        "aggregation_strategy": "any_hit_blocks",
        "aggregation_threshold": 1.0,
    },
    "policy.safe.default": {
        "category": "safe",
        "severity": "low",
        "action": "allow",
        "confidence": 0.90,
        "reason": "No obvious unsafe policy violation pattern detected.",
        "patterns": (),
        "aggregation_strategy": "any_hit_blocks",
        "aggregation_threshold": 1.0,
    },
}
