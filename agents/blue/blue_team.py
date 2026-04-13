from __future__ import annotations

from agents.blue.blue_team_aggregation import evaluate_policies, policy_evaluation_priority
from agents.blue.blue_team_config import get_blue_team_runtime_config
from agents.blue.blue_team_detectors import (
    BlueTeamDetector,
    DetectorSignal,
    LlamaGuardDetector,
    NeMoGuardrailsDetector,
    RuleDetector,
)
from agents.blue.blue_team_policies import POLICIES
from agents.contracts import BlueTeamContract, BlueTeamVerdict


class BasicBlueTeamAgent(BlueTeamContract):
    def __init__(self, detectors: list[BlueTeamDetector] | None = None) -> None:
        self._detectors = detectors or _build_default_detectors()
        self._runtime_config = get_blue_team_runtime_config()

    def evaluate_output(self, model_output: str) -> BlueTeamVerdict:
        detector_signals: list[DetectorSignal] = []
        detector_results: dict[str, dict] = {}
        active_detector_ids = [detector.detector_id for detector in self._detectors]

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

        policy_evaluations = evaluate_policies(
            detector_signals=detector_signals,
            active_detector_ids=active_detector_ids,
            detector_weights=self._runtime_config.detector_weights,
        )
        detector_results["_aggregation"] = {
            "active_detectors": active_detector_ids,
            "policy_evaluations": policy_evaluations,
        }

        triggered_policies = [
            evaluation for evaluation in policy_evaluations if evaluation["triggered"] is True
        ]
        if triggered_policies:
            selected = max(triggered_policies, key=policy_evaluation_priority)
            unsafe = POLICIES[selected["policy_id"]]
            detector_results["_decision"] = {
                "outcome": "unsafe",
                "selected_policy_id": selected["policy_id"],
                "category": unsafe["category"],
                "action": unsafe["action"],
                "severity": unsafe["severity"],
                "aggregation_strategy": selected["aggregation_strategy"],
                "aggregated_confidence": selected["aggregated_confidence"],
                "supporting_detectors": selected["supporting_detectors"],
                "rationale": (
                    f'{unsafe["reason"]} Triggered via {selected["aggregation_strategy"]} '
                    f"with support from {', '.join(selected['supporting_detectors']) or 'no detectors'}."
                ),
            }
            return BlueTeamVerdict(
                allowed=False,
                category=unsafe["category"],
                confidence=float(selected["aggregated_confidence"]),
                reason=f'{unsafe["reason"]} Aggregation: {selected["aggregation_strategy"]}.',
                action=unsafe["action"],
                severity=unsafe["severity"],
                policy_id=selected["policy_id"],
                detector_results=detector_results,
            )

        safe_id = "policy.safe.default"
        safe = POLICIES[safe_id]
        detector_results["_decision"] = {
            "outcome": "safe",
            "selected_policy_id": safe_id,
            "category": safe["category"],
            "action": safe["action"],
            "severity": safe["severity"],
            "aggregation_strategy": "no_policy_triggered",
            "aggregated_confidence": safe["confidence"],
            "supporting_detectors": [],
            "rationale": (
                "No unsafe policy reached its trigger threshold across the active detector set."
            ),
        }
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

def _build_default_detectors() -> list[BlueTeamDetector]:
    config = get_blue_team_runtime_config()
    detectors: list[BlueTeamDetector] = [RuleDetector()]
    if config.enable_llama_guard:
        detectors.append(LlamaGuardDetector())
    if config.enable_nemo_guardrails:
        detectors.append(NeMoGuardrailsDetector())
    return detectors


def get_blue_team_agent() -> BlueTeamContract:
    return BasicBlueTeamAgent()
