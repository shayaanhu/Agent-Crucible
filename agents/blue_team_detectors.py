from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from agents.blue_team_policies import POLICIES, PolicyConfig


@dataclass(frozen=True)
class DetectorSignal:
    detector_id: str
    policy_id: str
    confidence: float
    matched_patterns: list[str]
    flagged: bool


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
            )
        ]
