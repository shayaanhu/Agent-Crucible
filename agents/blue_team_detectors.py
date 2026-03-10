from __future__ import annotations

from dataclasses import dataclass, field
from importlib.util import find_spec
from typing import Protocol

from agents.blue_team_policies import POLICIES, PolicyConfig


@dataclass(frozen=True)
class DetectorSignal:
    detector_id: str
    policy_id: str
    confidence: float
    matched_patterns: list[str]
    flagged: bool
    metadata: dict[str, str] = field(default_factory=dict)


class BlueTeamDetector(Protocol):
    detector_id: str

    def detect(self, model_output: str) -> list[DetectorSignal]:
        ...


class RuleDetector:
    detector_id = "rule_detector"

    def __init__(self, policies: dict[str, PolicyConfig] | None = None) -> None:
        self._policies = policies or POLICIES

    def detect(self, model_output: str) -> list[DetectorSignal]:
        lowered = model_output.lower()
        signals: list[DetectorSignal] = []

        for policy_id, policy in self._policies.items():
            if policy_id == "policy.safe.default":
                continue
            if not policy["patterns"]:
                continue
            matches = [pattern for pattern in policy["patterns"] if pattern in lowered]
            if not matches:
                continue
            signals.append(
                DetectorSignal(
                    detector_id=self.detector_id,
                    policy_id=policy_id,
                    confidence=policy["confidence"],
                    matched_patterns=matches,
                    flagged=True,
                )
            )

        if signals:
            return signals

        safe_policy = self._policies["policy.safe.default"]
        return [
            DetectorSignal(
                detector_id=self.detector_id,
                policy_id="policy.safe.default",
                confidence=safe_policy["confidence"],
                matched_patterns=[],
                flagged=False,
                metadata={"source": "rules"},
            )
        ]


class LlamaGuardDetector:
    detector_id = "llamaguard_detector"

    def detect(self, model_output: str) -> list[DetectorSignal]:
        if find_spec("llama_guard") is None:
            safe_policy = POLICIES["policy.safe.default"]
            return [
                DetectorSignal(
                    detector_id=self.detector_id,
                    policy_id="policy.safe.default",
                    confidence=safe_policy["confidence"],
                    matched_patterns=[],
                    flagged=False,
                    metadata={
                        "source": "llamaguard",
                        "status": "unavailable",
                        "reason": "llamaguard dependency not installed",
                    },
                )
            ]

        _ = model_output
        safe_policy = POLICIES["policy.safe.default"]
        return [
            DetectorSignal(
                detector_id=self.detector_id,
                policy_id="policy.safe.default",
                confidence=safe_policy["confidence"],
                matched_patterns=[],
                flagged=False,
                metadata={"source": "llamaguard", "status": "stubbed"},
            )
        ]


class NeMoGuardrailsDetector:
    detector_id = "nemo_guardrails_detector"

    def detect(self, model_output: str) -> list[DetectorSignal]:
        if find_spec("nemoguardrails") is None:
            safe_policy = POLICIES["policy.safe.default"]
            return [
                DetectorSignal(
                    detector_id=self.detector_id,
                    policy_id="policy.safe.default",
                    confidence=safe_policy["confidence"],
                    matched_patterns=[],
                    flagged=False,
                    metadata={
                        "source": "nemo_guardrails",
                        "status": "unavailable",
                        "reason": "nemoguardrails dependency not installed",
                    },
                )
            ]

        _ = model_output
        safe_policy = POLICIES["policy.safe.default"]
        return [
            DetectorSignal(
                detector_id=self.detector_id,
                policy_id="policy.safe.default",
                confidence=safe_policy["confidence"],
                matched_patterns=[],
                flagged=False,
                metadata={"source": "nemo_guardrails", "status": "stubbed"},
            )
        ]
