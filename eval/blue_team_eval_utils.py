from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any


def timestamp_fields() -> dict[str, str]:
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone()
    return {
        "generated_at": now_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "generated_at_local": now_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "generated_at_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


def summarize_blue_team_results(results: list[dict[str, Any]], metrics: list[dict[str, Any]]) -> dict[str, Any]:
    total_cases = len(results)
    passed_cases = sum(1 for result in results if result.get("passed") is True)
    failed_cases = total_cases - passed_cases

    policy_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    blocked_cases = 0
    allowed_cases = 0
    escalation_cases = 0
    rewritten_cases = 0
    redacted_cases = 0
    average_confidence = 0.0
    case_summaries: list[dict[str, Any]] = []

    for result in results:
        policy_id = str(result.get("actual_policy_id", "policy.unknown"))
        action = str(result.get("actual_action", "allow"))
        actual_effective_allowed = bool(result.get("actual_effective_allowed", False))
        confidence = float(result.get("confidence", 0.0))

        policy_counts[policy_id] += 1
        action_counts[action] += 1
        average_confidence += confidence

        if actual_effective_allowed:
            allowed_cases += 1
        else:
            blocked_cases += 1
        if action == "escalate":
            escalation_cases += 1
        if action == "safe_rewrite":
            rewritten_cases += 1
        if action == "redact":
            redacted_cases += 1

        case_summaries.append(
            {
                "id": result.get("id", "unknown"),
                "expected_policy_id": result.get("expected_policy_id", "unknown"),
                "actual_policy_id": policy_id,
                "actual_action": action,
                "passed": bool(result.get("passed", False)),
                "actual_effective_allowed": actual_effective_allowed,
            }
        )

    average_confidence = round(average_confidence / total_cases, 4) if total_cases else 0.0

    return {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": failed_cases,
        "pass_rate": round(passed_cases / total_cases, 4) if total_cases else 0.0,
        "allowed_cases": allowed_cases,
        "blocked_cases": blocked_cases,
        "escalation_cases": escalation_cases,
        "rewritten_cases": rewritten_cases,
        "redacted_cases": redacted_cases,
        "average_confidence": average_confidence,
        "policy_counts": dict(policy_counts),
        "action_counts": dict(action_counts),
        "metrics": metrics,
        "case_summaries": case_summaries,
    }
