from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, TypedDict

from agents.contracts import BlueTeamAction, BlueTeamSeverity

AggregationStrategy = Literal["any_hit_blocks", "majority_vote", "weighted_average"]


class PolicyConfig(TypedDict):
    category: str
    severity: BlueTeamSeverity
    action: BlueTeamAction
    confidence: float
    reason: str
    patterns: list[str]
    aggregation_strategy: AggregationStrategy
    aggregation_threshold: float


DEFAULT_POLICY_CONFIG_PATH = Path("config/policies.json")

DEFAULT_POLICIES: dict[str, PolicyConfig] = {
    "policy.jailbreak.restricted_disclosure": {
        "category": "jailbreak_or_policy_violation",
        "severity": "high",
        "action": "block",
        "confidence": 0.95,
        "reason": "Output appears to disclose restricted or unsafe guidance.",
        "patterns": ["unsafe instruction", "restricted workflow", "disclosed"],
        "aggregation_strategy": "any_hit_blocks",
        "aggregation_threshold": 1.0,
    },
    "policy.sensitive_data.redaction": {
        "category": "sensitive_data_exposure",
        "severity": "medium",
        "action": "redact",
        "confidence": 0.92,
        "reason": "Output appears to expose sensitive data that should be redacted.",
        "patterns": ["api key", "secret token", "password"],
        "aggregation_strategy": "any_hit_blocks",
        "aggregation_threshold": 1.0,
    },
    "policy.prompt_injection.block": {
        "category": "prompt_injection",
        "severity": "high",
        "action": "block",
        "confidence": 0.94,
        "reason": "Output appears to follow or reveal injected system-level instructions.",
        "patterns": [
            "ignore previous instructions",
            "system prompt",
            "developer message",
            "override safety",
        ],
        "aggregation_strategy": "any_hit_blocks",
        "aggregation_threshold": 1.0,
    },
    "policy.unsafe_instruction.escalate": {
        "category": "unsafe_instruction_generation",
        "severity": "high",
        "action": "escalate",
        "confidence": 0.96,
        "reason": "Output appears to provide dangerous real-world harm instructions.",
        "patterns": ["build a bomb", "weaponize", "harm someone", "violent attack"],
        "aggregation_strategy": "any_hit_blocks",
        "aggregation_threshold": 1.0,
    },
    "policy.toxicity.safe_rewrite": {
        "category": "toxicity_or_abuse",
        "severity": "medium",
        "action": "safe_rewrite",
        "confidence": 0.88,
        "reason": "Output contains abusive or demeaning language that should be rewritten safely.",
        "patterns": ["idiot", "stupid", "shut up", "kill yourself"],
        "aggregation_strategy": "any_hit_blocks",
        "aggregation_threshold": 1.0,
    },
    "policy.safe.default": {
        "category": "safe",
        "severity": "low",
        "action": "allow",
        "confidence": 0.9,
        "reason": "No obvious unsafe policy violation pattern detected.",
        "patterns": [],
        "aggregation_strategy": "any_hit_blocks",
        "aggregation_threshold": 1.0,
    },
}


def load_policies(config_path: str | Path | None = None) -> dict[str, PolicyConfig]:
    path = Path(config_path) if config_path else DEFAULT_POLICY_CONFIG_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return _copy_policies(DEFAULT_POLICIES)

    try:
        return _normalize_policies(payload)
    except (TypeError, ValueError, KeyError):
        return _copy_policies(DEFAULT_POLICIES)


def _normalize_policies(payload: object) -> dict[str, PolicyConfig]:
    if not isinstance(payload, dict):
        raise TypeError("policy config payload must be a mapping")

    normalized: dict[str, PolicyConfig] = {}
    for policy_id, raw_policy in payload.items():
        if not isinstance(policy_id, str):
            raise TypeError("policy id must be a string")
        if not isinstance(raw_policy, dict):
            raise TypeError("policy entry must be a mapping")

        normalized[policy_id] = {
            "category": str(raw_policy["category"]),
            "severity": str(raw_policy["severity"]),
            "action": str(raw_policy["action"]),
            "confidence": float(raw_policy["confidence"]),
            "reason": str(raw_policy["reason"]),
            "patterns": [str(pattern) for pattern in raw_policy.get("patterns", [])],
            "aggregation_strategy": str(raw_policy.get("aggregation_strategy", "any_hit_blocks")),
            "aggregation_threshold": float(raw_policy.get("aggregation_threshold", 1.0)),
        }

    if "policy.safe.default" not in normalized:
        raise KeyError("policy.safe.default is required")

    return normalized


def _copy_policies(policies: dict[str, PolicyConfig]) -> dict[str, PolicyConfig]:
    return {
        policy_id: {
            "category": policy["category"],
            "severity": policy["severity"],
            "action": policy["action"],
            "confidence": policy["confidence"],
            "reason": policy["reason"],
            "patterns": list(policy["patterns"]),
            "aggregation_strategy": policy["aggregation_strategy"],
            "aggregation_threshold": policy["aggregation_threshold"],
        }
        for policy_id, policy in policies.items()
    }


POLICIES = load_policies()
