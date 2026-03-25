from __future__ import annotations

from dataclasses import replace
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _sanitize_label(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return cleaned or "default"


def generate_benchmark(label_override: str | None = None) -> dict:
    from agents.blue_team import BasicBlueTeamAgent, get_blue_team_agent
    from agents.blue_team_config import get_blue_team_runtime_config
    from agents.blue_team_detectors import RuleDetector
    from backend.app.pipeline import _enforce_guardrail_action
    from eval.scorer import calculate_metrics

    fixture_path = Path("backend/tests/fixtures/blue_team/regression_cases.json")
    output_dir = Path("eval/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    cases = json.loads(fixture_path.read_text(encoding="utf-8"))
    config = get_blue_team_runtime_config()
    if label_override:
        config = replace(config, benchmark_label=_sanitize_label(label_override))
    baseline_agent = BasicBlueTeamAgent(detectors=[RuleDetector()])
    configured_agent = get_blue_team_agent()

    baseline = _run_benchmark_suite(
        cases,
        baseline_agent,
        _enforce_guardrail_action,
        calculate_metrics,
        config.benchmark_thresholds,
    )
    configured = _run_benchmark_suite(
        cases,
        configured_agent,
        _enforce_guardrail_action,
        calculate_metrics,
        config.benchmark_thresholds,
    )

    benchmark = {
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

    out_path = output_dir / "blue_team_benchmark_results.json"
    out_path.write_text(json.dumps(benchmark, indent=2), encoding="utf-8")

    labeled_path = output_dir / f"blue_team_benchmark_results-{config.benchmark_label}.json"
    labeled_path.write_text(json.dumps(benchmark, indent=2), encoding="utf-8")
    benchmark["artifacts"] = {
        "canonical_path": str(out_path),
        "labeled_path": str(labeled_path),
    }
    return benchmark


def main() -> None:
    benchmark = generate_benchmark()
    print(f'Wrote blue-team benchmark results to {benchmark["artifacts"]["canonical_path"]}')
    print(f'Wrote labeled blue-team benchmark results to {benchmark["artifacts"]["labeled_path"]}')


def _run_benchmark_suite(cases, agent, enforce_guardrail_action, calculate_metrics, thresholds) -> dict:
    results: list[dict] = []
    verdicts: list[dict] = []
    events: list[dict] = []
    policy_counter: Counter[str] = Counter()
    action_counter: Counter[str] = Counter()
    pass_count = 0

    for case in cases:
        verdict = agent.evaluate_output(case["model_output"])
        effective_allowed, effective_action, effective_reason, effective_output, detector_results = (
            enforce_guardrail_action(case["model_output"], verdict, dry_run=False)
        )

        case_result = {
            "id": case["id"],
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
            "detector_results": detector_results,
        }
        case_result["passed"] = (
            verdict.policy_id == case["expected_policy_id"]
            and effective_action == case["expected_action"]
            and verdict.allowed is case["expected_verdict_allowed"]
            and effective_allowed is case["expected_effective_allowed"]
            and case["expected_output_contains"] in effective_output
        )
        if case_result["passed"]:
            pass_count += 1

        results.append(case_result)
        verdicts.append(
            {
                "allowed": effective_allowed,
                "policy_id": verdict.policy_id,
                "action": effective_action,
            }
        )
        events.append({"model_output": case["model_output"]})
        policy_counter[verdict.policy_id] += 1
        action_counter[effective_action] += 1

    metrics = calculate_metrics(verdicts, thresholds, events=events)
    return {
        "summary": {
            "total_cases": len(results),
            "passed_cases": pass_count,
            "failed_cases": len(results) - pass_count,
            "policy_counts": dict(policy_counter),
            "action_counts": dict(action_counter),
            "metrics": metrics,
        },
        "results": results,
    }


if __name__ == "__main__":
    main()
