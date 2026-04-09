from __future__ import annotations

from collections import Counter, defaultdict
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


def summarize_red_team_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    total_cases = len(results)
    stop_reason_counts: Counter[str] = Counter()
    final_outcome_counts: Counter[str] = Counter()
    strategy_totals: defaultdict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "cases": 0,
            "successes": 0,
            "blocked": 0,
            "no_success": 0,
            "partial": 0,
            "avg_turns": 0.0,
            "stop_reasons": Counter(),
        }
    )
    tag_totals: defaultdict[str, dict[str, int]] = defaultdict(
        lambda: {"cases": 0, "successes": 0}
    )
    category_totals: defaultdict[str, dict[str, int]] = defaultdict(
        lambda: {"cases": 0, "successes": 0}
    )
    difficulty_totals: defaultdict[str, dict[str, int]] = defaultdict(
        lambda: {"cases": 0, "successes": 0}
    )
    case_summaries: list[dict[str, Any]] = []

    total_turns = 0
    total_success_turns = 0
    success_count = 0
    blocked_count = 0
    partial_count = 0
    no_success_count = 0

    for result in results:
        turns = result.get("turns", [])
        stop_reason = str(result.get("stop_reason", "unknown"))
        strategy_id = str(result.get("strategy_id", "unknown"))
        metadata = result.get("metadata", {}) or {}
        category = str(metadata.get("objective_category", "uncategorized")).strip() or "uncategorized"
        difficulty = str(metadata.get("objective_difficulty", "unspecified")).strip() or "unspecified"

        stop_reason_counts[stop_reason] += 1
        turn_count = len(turns)
        total_turns += turn_count

        final_label = _final_objective_label(result)
        final_outcome_counts[final_label] += 1

        strategy_entry = strategy_totals[strategy_id]
        strategy_entry["cases"] += 1
        strategy_entry["avg_turns"] += turn_count
        strategy_entry["stop_reasons"][stop_reason] += 1

        if final_label == "success":
            success_count += 1
            total_success_turns += turn_count
            strategy_entry["successes"] += 1
        elif final_label == "blocked":
            blocked_count += 1
            strategy_entry["blocked"] += 1
        elif final_label == "partial":
            partial_count += 1
            strategy_entry["partial"] += 1
        else:
            no_success_count += 1
            strategy_entry["no_success"] += 1

        for tag in _split_tags(metadata.get("objective_tags", "")):
            tag_totals[tag]["cases"] += 1
            if final_label == "success":
                tag_totals[tag]["successes"] += 1

        category_totals[category]["cases"] += 1
        difficulty_totals[difficulty]["cases"] += 1
        if final_label == "success":
            category_totals[category]["successes"] += 1
            difficulty_totals[difficulty]["successes"] += 1

        case_summaries.append(
            {
                "id": metadata.get("dataset_id") or metadata.get("fixture_id") or "unknown",
                "goal": metadata.get("goal", ""),
                "scenario": metadata.get("scenario", ""),
                "strategy_id": strategy_id,
                "category": category,
                "difficulty": difficulty,
                "final_outcome": final_label,
                "turns": turn_count,
                "stop_reason": stop_reason,
            }
        )

    per_strategy: dict[str, dict[str, Any]] = {}
    for strategy_id, entry in sorted(strategy_totals.items()):
        cases = entry["cases"]
        per_strategy[strategy_id] = {
            "cases": cases,
            "successes": entry["successes"],
            "blocked": entry["blocked"],
            "no_success": entry["no_success"],
            "partial": entry["partial"],
            "success_rate": round(entry["successes"] / cases, 4) if cases else 0.0,
            "avg_turns": round(entry["avg_turns"] / cases, 2) if cases else 0.0,
            "stop_reasons": dict(entry["stop_reasons"]),
        }

    per_tag: dict[str, dict[str, Any]] = {}
    for tag, entry in sorted(tag_totals.items()):
        cases = entry["cases"]
        per_tag[tag] = {
            "cases": cases,
            "successes": entry["successes"],
            "success_rate": round(entry["successes"] / cases, 4) if cases else 0.0,
        }

    per_category: dict[str, dict[str, Any]] = {}
    for category, entry in sorted(category_totals.items()):
        cases = entry["cases"]
        per_category[category] = {
            "cases": cases,
            "successes": entry["successes"],
            "success_rate": round(entry["successes"] / cases, 4) if cases else 0.0,
        }

    per_difficulty: dict[str, dict[str, Any]] = {}
    for difficulty, entry in sorted(difficulty_totals.items()):
        cases = entry["cases"]
        per_difficulty[difficulty] = {
            "cases": cases,
            "successes": entry["successes"],
            "success_rate": round(entry["successes"] / cases, 4) if cases else 0.0,
        }

    return {
        "total_cases": total_cases,
        "successes": success_count,
        "blocked": blocked_count,
        "no_success": no_success_count,
        "partial": partial_count,
        "success_rate": round(success_count / total_cases, 4) if total_cases else 0.0,
        "average_turns": round(total_turns / total_cases, 2) if total_cases else 0.0,
        "average_turns_for_successes": (
            round(total_success_turns / success_count, 2) if success_count else 0.0
        ),
        "stop_reason_counts": dict(stop_reason_counts),
        "final_outcome_counts": dict(final_outcome_counts),
        "per_strategy": per_strategy,
        "per_tag": per_tag,
        "per_category": per_category,
        "per_difficulty": per_difficulty,
        "case_summaries": case_summaries,
    }


def _final_objective_label(result: dict[str, Any]) -> str:
    turns = result.get("turns", [])
    if result.get("stop_reason") == "success_detected":
        return "success"
    if turns:
        objective = turns[-1].get("objective_scorer") or {}
        label = str(objective.get("label", "")).strip()
        if label:
            return label
        outcome = str(turns[-1].get("outcome", "")).strip()
        if outcome:
            return outcome
    return "no_success"


def _split_tags(raw: str) -> list[str]:
    return [item.strip() for item in str(raw).split(",") if item.strip()]
