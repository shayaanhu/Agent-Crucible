from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a readable Markdown report for a blue-team eval artifact.")
    parser.add_argument(
        "--input",
        default="eval/results/blue_team_benchmark_results.json",
        help="Path to a blue-team eval result JSON file.",
    )
    parser.add_argument(
        "--show-cases",
        type=int,
        default=10,
        help="How many case summaries to print per suite.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output Markdown path. Defaults to eval/report/<input-stem>_report.md",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    run_metadata = payload.get("run_metadata", {})
    config = payload.get("config", {})
    baseline = payload.get("baseline_rules_only", {})
    configured = payload.get("configured_detectors", {})
    comparison = payload.get("comparison", {})

    output_path = Path(args.output) if args.output else _default_output_path(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        _build_report(
            run_metadata,
            config,
            baseline,
            configured,
            comparison,
            show_cases=args.show_cases,
        ),
        encoding="utf-8",
    )
    print(f"Wrote blue-team eval report to {output_path}")


def _build_report(
    run_metadata: dict,
    config: dict,
    baseline: dict,
    configured: dict,
    comparison: dict,
    show_cases: int = 10,
) -> str:
    lines: list[str] = []
    lines.append("# Blue-Team Eval Report")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Runner | {run_metadata.get('runner', 'unknown')} |")
    lines.append(f"| Generated At | {run_metadata.get('generated_at', 'unknown')} |")
    lines.append(f"| Benchmark Label | {run_metadata.get('benchmark_label', config.get('benchmark_label', 'unknown'))} |")
    lines.append(f"| Fixture Path | {run_metadata.get('fixture_path', 'unknown')} |")
    lines.append("")

    lines.append("## Config")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| LlamaGuard Enabled | {config.get('enable_llama_guard', False)} |")
    lines.append(f"| NeMo Enabled | {config.get('enable_nemo_guardrails', False)} |")
    lines.append(f"| Policy Config Path | {config.get('policy_config_path', 'unknown')} |")
    lines.append(f"| Benchmark Label | {config.get('benchmark_label', 'unknown')} |")
    lines.append("")

    _append_suite(lines, "Rules-only Baseline", baseline, show_cases)
    _append_suite(lines, "Configured Detectors", configured, show_cases)

    lines.append("")
    lines.append("## Comparison")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Baseline Passed Cases | {comparison.get('baseline_passed_cases', 0)} |")
    lines.append(f"| Configured Passed Cases | {comparison.get('configured_passed_cases', 0)} |")
    lines.append(f"| Delta Passed Cases | {comparison.get('delta_passed_cases', 0)} |")
    return "\n".join(lines)


def _append_suite(lines: list[str], title: str, suite: dict, show_cases: int) -> None:
    summary = suite.get("summary", {})
    case_summaries = summary.get("case_summaries", [])
    lines.append("")
    lines.append(f"## {title}")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Total Cases | {summary.get('total_cases', 0)} |")
    lines.append(f"| Passed Cases | {summary.get('passed_cases', 0)} |")
    lines.append(f"| Failed Cases | {summary.get('failed_cases', 0)} |")
    lines.append(f"| Pass Rate | {_pct(summary.get('pass_rate', 0.0))} |")
    lines.append(f"| Allowed Cases | {summary.get('allowed_cases', 0)} |")
    lines.append(f"| Blocked Cases | {summary.get('blocked_cases', 0)} |")
    lines.append(f"| Escalation Cases | {summary.get('escalation_cases', 0)} |")
    lines.append(f"| Rewritten Cases | {summary.get('rewritten_cases', 0)} |")
    lines.append(f"| Redacted Cases | {summary.get('redacted_cases', 0)} |")
    lines.append(f"| Average Confidence | {summary.get('average_confidence', 0.0)} |")

    _append_dict_section(lines, "Policy Counts", summary.get("policy_counts", {}))
    _append_dict_section(lines, "Action Counts", summary.get("action_counts", {}))
    _append_metric_section(lines, "Metrics", summary.get("metrics", []))

    if case_summaries:
        lines.append("")
        lines.append("### Case Summaries")
        lines.append("")
        lines.append("| ID | Expected Policy | Actual Policy | Action | Allowed | Passed |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        limit = max(show_cases, 0)
        for case in case_summaries[:limit]:
            lines.append(
                f"| {case.get('id', 'unknown')} | "
                f"{case.get('expected_policy_id', 'unknown')} | "
                f"{case.get('actual_policy_id', 'unknown')} | "
                f"{case.get('actual_action', 'unknown')} | "
                f"{case.get('actual_effective_allowed', False)} | "
                f"{case.get('passed', False)} |"
            )
        remaining = len(case_summaries) - limit
        if remaining > 0:
            lines.append("")
            lines.append(f"_... {remaining} more case summaries omitted_")


def _append_dict_section(lines: list[str], title: str, values: dict) -> None:
    if not values:
        return
    lines.append("")
    lines.append(f"### {title}")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("| --- | --- |")
    for key, value in values.items():
        lines.append(f"| {key} | {value} |")


def _append_metric_section(lines: list[str], title: str, metrics: list[dict]) -> None:
    if not metrics:
        return
    lines.append("")
    lines.append(f"### {title}")
    lines.append("")
    lines.append("| Metric | Value | Threshold | Pass/Fail |")
    lines.append("| --- | --- | --- | --- |")
    for metric in metrics:
        lines.append(
            f"| {metric.get('metric_name', 'unknown')} | "
            f"{metric.get('value', 0.0)} | "
            f"{metric.get('threshold', 0.0)} | "
            f"{metric.get('pass_fail', 'unknown')} |"
        )


def _pct(value: float) -> str:
    return f"{float(value) * 100:.2f}%"


def _default_output_path(input_path: Path) -> Path:
    return Path("eval/report") / f"{input_path.stem}_report.md"


if __name__ == "__main__":
    main()
