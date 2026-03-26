from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a readable Markdown report for a red-team eval artifact.")
    parser.add_argument(
        "--input",
        default="eval/results/red_team_dataset_results.json",
        help="Path to a red-team eval result JSON file.",
    )
    parser.add_argument(
        "--show-cases",
        type=int,
        default=10,
        help="How many case summaries to print.",
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
    summary = payload.get("summary", {})
    results = payload.get("results", [])

    output_path = Path(args.output) if args.output else _default_output_path(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_build_report(run_metadata, summary, results, show_cases=args.show_cases), encoding="utf-8")
    print(f"Wrote red-team eval report to {output_path}")


def _build_report(
    run_metadata: dict,
    summary: dict,
    results: list[dict],
    show_cases: int = 10,
) -> str:
    lines: list[str] = []
    lines.append("# Red-Team Eval Report")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Suite Type | {run_metadata.get('suite_type', 'unknown')} |")
    lines.append(f"| Runner | {run_metadata.get('runner', 'unknown')} |")
    lines.append(f"| Generated At | {run_metadata.get('generated_at', 'unknown')} |")
    lines.append(f"| Provider | {run_metadata.get('provider', 'unknown')} |")
    lines.append(f"| Attacker | {run_metadata.get('attacker_provider', 'unknown')} |")
    lines.append(f"| Max Turns | {run_metadata.get('max_turns', 'unknown')} |")
    lines.append(f"| Total Results | {run_metadata.get('total_results', len(results))} |")

    if run_metadata.get("suite_name"):
        lines.append(f"| Suite Name | {run_metadata.get('suite_name')} |")
    if run_metadata.get("suite_version"):
        lines.append(f"| Suite Version | {run_metadata.get('suite_version')} |")
    if run_metadata.get("category_filter"):
        lines.append(f"| Category Filter | {run_metadata.get('category_filter')} |")
    if run_metadata.get("difficulty_filter"):
        lines.append(f"| Difficulty | {run_metadata.get('difficulty_filter')} |")
    if run_metadata.get("strategy_filter"):
        lines.append(f"| Strategy Filter | {run_metadata.get('strategy_filter')} |")

    lines.append("")
    lines.append("## Core Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Success Rate | {_pct(summary.get('success_rate', 0.0))} |")
    lines.append(f"| Successes | {summary.get('successes', 0)} |")
    lines.append(f"| Blocked | {summary.get('blocked', 0)} |")
    lines.append(f"| No Success | {summary.get('no_success', 0)} |")
    lines.append(f"| Partial | {summary.get('partial', 0)} |")
    lines.append(f"| Average Turns | {summary.get('average_turns', 0.0)} |")
    lines.append(f"| Average Turns (Successes) | {summary.get('average_turns_for_successes', 0.0)} |")

    _append_dict_section(lines, "Stop Reasons", summary.get("stop_reason_counts", {}))
    _append_breakdown(lines, "Per Strategy", summary.get("per_strategy", {}))
    _append_breakdown(lines, "Per Category", summary.get("per_category", {}))
    _append_breakdown(lines, "Per Difficulty", summary.get("per_difficulty", {}))
    _append_breakdown(lines, "Per Tag", summary.get("per_tag", {}))

    case_summaries = summary.get("case_summaries", [])
    if case_summaries:
        lines.append("")
        lines.append("## Case Summaries")
        lines.append("")
        lines.append("| ID | Strategy | Category | Difficulty | Outcome | Turns | Stop Reason |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        limit = max(show_cases, 0)
        for case in case_summaries[:limit]:
            lines.append(
                f"| {case.get('id', 'unknown')} | "
                f"{case.get('strategy_id', 'unknown')} | "
                f"{case.get('category', 'uncategorized')} | "
                f"{case.get('difficulty', 'unspecified')} | "
                f"{case.get('final_outcome', 'unknown')} | "
                f"{case.get('turns', 0)} | "
                f"{case.get('stop_reason', 'unknown')} |"
            )
        remaining = len(case_summaries) - limit
        if remaining > 0:
            lines.append("")
            lines.append(f"_... {remaining} more case summaries omitted_")

    return "\n".join(lines)


def _append_dict_section(lines: list[str], title: str, values: dict) -> None:
    if not values:
        return
    lines.append("")
    lines.append(f"## {title}")
    lines.append("")
    lines.append("| Key | Value |")
    lines.append("| --- | --- |")
    for key, value in values.items():
        lines.append(f"| {key} | {value} |")


def _append_breakdown(lines: list[str], title: str, values: dict) -> None:
    if not values:
        return
    lines.append("")
    lines.append(f"## {title}")
    lines.append("")
    lines.append("| Name | Cases | Successes | Success Rate | Details |")
    lines.append("| --- | --- | --- | --- | --- |")
    for key, entry in values.items():
        cases = entry.get("cases", 0)
        successes = entry.get("successes", 0)
        success_rate = _pct(entry.get("success_rate", 0.0))
        extra = []
        if "avg_turns" in entry:
            extra.append(f"avg_turns={entry.get('avg_turns', 0.0)}")
        if "blocked" in entry:
            extra.append(f"blocked={entry.get('blocked', 0)}")
        if "no_success" in entry:
            extra.append(f"no_success={entry.get('no_success', 0)}")
        if "partial" in entry:
            extra.append(f"partial={entry.get('partial', 0)}")
        extra_text = ", ".join(extra) if extra else "-"
        lines.append(f"| {key} | {cases} | {successes} | {success_rate} | {extra_text} |")


def _pct(value: float) -> str:
    return f"{float(value) * 100:.2f}%"


def _default_output_path(input_path: Path) -> Path:
    return Path("eval/report") / f"{input_path.stem}_report.md"


if __name__ == "__main__":
    main()
