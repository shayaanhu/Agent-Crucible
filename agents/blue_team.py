from __future__ import annotations

from agents.blue_team_detectors import BlueTeamDetector, DetectorSignal, RuleDetector
from agents.blue_team_policies import POLICIES
from agents.contracts import BlueTeamContract, BlueTeamVerdict


class BasicBlueTeamAgent(BlueTeamContract):
    def __init__(self, detectors: list[BlueTeamDetector] | None = None) -> None:
        self._detectors = detectors or [RuleDetector()]

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


def get_blue_team_agent() -> BlueTeamContract:
    return BasicBlueTeamAgent()
