from __future__ import annotations

from agents.blue.blue_team_detectors import DetectorSignal
from agents.blue.blue_team_policies import POLICIES


def policy_evaluation_priority(evaluation: dict[str, object]) -> tuple[int, float]:
    severity_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    policy = POLICIES.get(str(evaluation["policy_id"]), POLICIES["policy.safe.default"])
    return (severity_rank.get(policy["severity"], 0), float(evaluation["aggregated_confidence"]))


def evaluate_policies(
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
        evaluation = evaluate_single_policy(
            policy_id=policy_id,
            signals=signals,
            active_detector_ids=active_detector_ids,
            detector_weights=detector_weights,
        )
        policy_evaluations.append(evaluation)

    policy_evaluations.sort(key=policy_evaluation_priority, reverse=True)
    return policy_evaluations


def evaluate_single_policy(
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
