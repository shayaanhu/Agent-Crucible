from __future__ import annotations

from agents.blue_team_config import get_blue_team_runtime_config
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

        policy_evaluations = _evaluate_policies(
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
            selected = max(triggered_policies, key=_policy_evaluation_priority)
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


def _policy_evaluation_priority(evaluation: dict[str, object]) -> tuple[int, float]:
    severity_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    policy = POLICIES.get(str(evaluation["policy_id"]), POLICIES["policy.safe.default"])
    return (severity_rank.get(policy["severity"], 0), float(evaluation["aggregated_confidence"]))


def _evaluate_policies(
    *,
    detector_signals: list[DetectorSignal],
    active_detector_ids: list[str],
    detector_weights: dict[str, float],
) -> list[dict[str, object]]:
    unsafe_signals = [signal for signal in detector_signals if signal.flagged]
    grouped_signals: dict[str, list[DetectorSignal]] = {}
    for signal in unsafe_signals:
        grouped_signals.setdefault(signal.policy_id, []).append(signal)

    policy_evaluations: list[dict[str, object]] = []
    for policy_id, signals in grouped_signals.items():
        policy = POLICIES.get(policy_id)
        if policy is None:
            continue
        evaluation = _evaluate_single_policy(
            policy_id=policy_id,
            signals=signals,
            active_detector_ids=active_detector_ids,
            detector_weights=detector_weights,
        )
        policy_evaluations.append(evaluation)

    policy_evaluations.sort(key=_policy_evaluation_priority, reverse=True)
    return policy_evaluations


def _evaluate_single_policy(
    *,
    policy_id: str,
    signals: list[DetectorSignal],
    active_detector_ids: list[str],
    detector_weights: dict[str, float],
) -> dict[str, object]:
    policy = POLICIES[policy_id]
    supporting_detectors = sorted({signal.detector_id for signal in signals})
    supporting_count = len(supporting_detectors)
    active_count = max(len(active_detector_ids), 1)
    max_signal_confidence = max(signal.confidence for signal in signals)

    strategy = policy["aggregation_strategy"]
    threshold = policy["aggregation_threshold"]
    triggered = False
    aggregated_confidence = max_signal_confidence

    if strategy == "majority_vote":
        vote_ratio = supporting_count / active_count
        aggregated_confidence = max(max_signal_confidence, vote_ratio)
        triggered = vote_ratio > threshold
    elif strategy == "weighted_average":
        total_weight = sum(detector_weights.get(detector_id, 1.0) for detector_id in active_detector_ids)
        supporting_weight = sum(
            detector_weights.get(detector_id, 1.0) for detector_id in supporting_detectors
        )
        weighted_score = supporting_weight / total_weight if total_weight else 0.0
        aggregated_confidence = max(max_signal_confidence, weighted_score)
        triggered = weighted_score >= threshold
    else:
        triggered = supporting_count >= 1

    return {
        "policy_id": policy_id,
        "aggregation_strategy": strategy,
        "aggregation_threshold": threshold,
        "aggregated_confidence": round(aggregated_confidence, 4),
        "supporting_detectors": supporting_detectors,
        "supporting_count": supporting_count,
        "active_detector_count": active_count,
        "triggered": triggered,
    }


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
