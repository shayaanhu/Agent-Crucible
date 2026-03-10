from __future__ import annotations

import os

from agents.blue_team_detectors import (
    BlueTeamDetector,
    DetectorSignal,
    LlamaGuardDetector,
    NeMoGuardrailsDetector,
    RuleDetector,
)
from agents.blue_team_policies import POLICIES
from agents.contracts import BlueTeamContract, BlueTeamVerdict


class BasicBlueTeamAgent(BlueTeamContract):
    def __init__(self, detectors: list[BlueTeamDetector] | None = None) -> None:
        self._detectors = detectors or _build_default_detectors()

    def evaluate_output(self, model_output: str) -> BlueTeamVerdict:
        detector_signals: list[DetectorSignal] = []
        detector_results: dict[str, dict] = {}

        for detector in self._detectors:
            signals = detector.detect(model_output)
            detector_signals.extend(signals)
            detector_results[detector.detector_id] = {
                "matched_patterns": [
                    pattern
                    for signal in signals
                    if signal.flagged
                    for pattern in signal.matched_patterns
                ],
                "signals": [
                    {
                        "policy_id": signal.policy_id,
                        "confidence": signal.confidence,
                        "matched_patterns": signal.matched_patterns,
                        "flagged": signal.flagged,
                        "metadata": signal.metadata,
                    }
                    for signal in signals
                ],
            }

        unsafe_signals = [signal for signal in detector_signals if signal.flagged]
        if unsafe_signals:
            selected = max(unsafe_signals, key=_unsafe_priority)
            unsafe = POLICIES[selected.policy_id]
            return BlueTeamVerdict(
                allowed=False,
                category=unsafe["category"],
                confidence=unsafe["confidence"],
                reason=unsafe["reason"],
                action=unsafe["action"],
                severity=unsafe["severity"],
                policy_id=selected.policy_id,
                detector_results=detector_results,
            )

        safe_id = "policy.safe.default"
        safe = POLICIES[safe_id]
        return BlueTeamVerdict(
            allowed=True,
            category=safe["category"],
            confidence=safe["confidence"],
            reason=safe["reason"],
            action=safe["action"],
            severity=safe["severity"],
            policy_id=safe_id,
            detector_results=detector_results,
        )


def _unsafe_priority(signal: DetectorSignal) -> tuple[int, float]:
    severity_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    policy = POLICIES.get(signal.policy_id, POLICIES["policy.safe.default"])
    return (severity_rank.get(policy["severity"], 0), signal.confidence)


def _env_flag(name: str) -> bool:
    return os.getenv(name, "0").strip().lower() in {"1", "true", "yes", "on"}


def _build_default_detectors() -> list[BlueTeamDetector]:
    detectors: list[BlueTeamDetector] = [RuleDetector()]
    if _env_flag("BLUE_TEAM_ENABLE_LLAMA_GUARD"):
        detectors.append(LlamaGuardDetector())
    if _env_flag("BLUE_TEAM_ENABLE_NEMO_GUARDRAILS"):
        detectors.append(NeMoGuardrailsDetector())
    return detectors


def get_blue_team_agent() -> BlueTeamContract:
    return BasicBlueTeamAgent()
