from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Blue Team objective suite and export eval results.")
    parser.add_argument(
        "--dataset",
        default="eval/fixtures/blue_team_objectives.json",
        help="Path to Blue Team dataset JSON file.",
    )
    parser.add_argument("--label", default="", help="Optional benchmark label override.")
    parser.add_argument("--limit", type=int, default=0, help="Optional cap on the number of cases to run.")
    parser.add_argument("--category", default="", help="Run only cases in this category.")
    parser.add_argument("--difficulty", default="", help="Run only cases in this difficulty tier.")
    parser.add_argument("--policy", default="", help="Run only cases for this expected policy id.")
    parser.add_argument("--action", default="", help="Run only cases for this expected action.")
    args = parser.parse_args()

    from agents.blue_team import BasicBlueTeamAgent, get_blue_team_agent
    from agents.blue_team_config import get_blue_team_runtime_config
    from agents.blue_team_detectors import RuleDetector
    from backend.app.pipeline import _enforce_guardrail_action
    from eval.blue_team_eval_utils import summarize_blue_team_results, timestamp_fields
    from eval.scorer import calculate_metrics

    dataset_path = Path(args.dataset)
    output_dir = Path("eval/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    suite_metadata = payload.get("suite_metadata", {}) if isinstance(payload, dict) else {}
    cases = list(payload.get("cases", [])) if isinstance(payload, dict) else list(payload)

    if args.category:
        cases = [case for case in cases if case.get("category", "") == args.category]
    if args.difficulty:
        cases = [case for case in cases if case.get("difficulty", "") == args.difficulty]
    if args.policy:
        cases = [case for case in cases if case.get("expected_policy_id", "") == args.policy]
    if args.action:
        cases = [case for case in cases if case.get("expected_action", "") == args.action]
    if args.limit > 0:
        cases = cases[: args.limit]

    config = get_blue_team_runtime_config()
    if args.label:
        config = config.__class__(**{**config.to_dict(), "benchmark_label": args.label})
    baseline_agent = BasicBlueTeamAgent(detectors=[RuleDetector()])
    configured_agent = get_blue_team_agent()

    baseline = _run_suite(
        cases,
        baseline_agent,
        _enforce_guardrail_action,
        calculate_metrics,
        config.benchmark_thresholds,
        summarize_blue_team_results,
    )
    configured = _run_suite(
        cases,
        configured_agent,
        _enforce_guardrail_action,
        calculate_metrics,
        config.benchmark_thresholds,
        summarize_blue_team_results,
    )

    result_payload = {
        "run_metadata": {
            "suite_type": "objective_suite",
            "runner": "blue_team_dataset",
            **timestamp_fields(),
            "dataset_path": str(dataset_path),
            "suite_name": suite_metadata.get("suite_name", ""),
            "suite_version": suite_metadata.get("suite_version", ""),
            "category_filter": args.category,
            "difficulty_filter": args.difficulty,
            "policy_filter": args.policy,
            "action_filter": args.action,
            "limit": args.limit,
            "benchmark_label": config.benchmark_label,
            "total_cases": len(cases),
        },
        "config": config.to_dict(),
        "baseline_rules_only": baseline,
        "configured_detectors": configured,
        "comparison": {
            "baseline_passed_cases": baseline["summary"]["passed_cases"],
            "configured_passed_cases": configured["summary"]["passed_cases"],
            "delta_passed_cases": configured["summary"]["passed_cases"]
            - baseline["summary"]["passed_cases"],
        },
    }

    out_path = output_dir / "blue_team_dataset_results.json"
    out_path.write_text(json.dumps(result_payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(cases)} blue-team dataset cases to {out_path}")


def _run_suite(cases, agent, enforce_guardrail_action, calculate_metrics, thresholds, summarize_blue_team_results):
    results: list[dict] = []
    verdicts: list[dict] = []
    events: list[dict] = []

    for case in cases:
        verdict = agent.evaluate_output(case["model_output"])
        effective_allowed, effective_action, effective_reason, effective_output, detector_results = (
            enforce_guardrail_action(case["model_output"], verdict, dry_run=False)
        )
        case_result = {
            "id": case["id"],
            "category": case.get("category", ""),
            "difficulty": case.get("difficulty", ""),
            "tags": case.get("tags", ""),
            "model_output": case["model_output"],
            "expected_policy_id": case["expected_policy_id"],
            "expected_action": case["expected_action"],
            "expected_verdict_allowed": case["expected_verdict_allowed"],
            "expected_effective_allowed": case["expected_effective_allowed"],
            "actual_policy_id": verdict.policy_id,
            "actual_action": effective_action,
            "actual_verdict_allowed": verdict.allowed,
            "actual_effective_allowed": effective_allowed,
            "effective_output": effective_output,
            "reason": effective_reason,
            "confidence": verdict.confidence,
            "detector_results": detector_results,
        }
        case_result["passed"] = (
            verdict.policy_id == case["expected_policy_id"]
            and effective_action == case["expected_action"]
            and verdict.allowed is case["expected_verdict_allowed"]
            and effective_allowed is case["expected_effective_allowed"]
            and case["expected_output_contains"] in effective_output
        )
        results.append(case_result)
        verdicts.append(
            {
                "allowed": effective_allowed,
                "policy_id": verdict.policy_id,
                "action": effective_action,
            }
        )
        events.append({"model_output": case["model_output"]})

    metrics = calculate_metrics(verdicts, thresholds, events=events)
    return {
        "summary": summarize_blue_team_results(results, metrics),
        "results": results,
    }


if __name__ == "__main__":
    main()
