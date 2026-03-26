from __future__ import annotations

import json
from pathlib import Path

from eval.report_red_team_eval import _build_report, _default_output_path, main as run_red_team_report
from eval.run_red_team_benchmark import main as run_red_team_regression
from eval.run_red_team_dataset import main as run_red_team_objective_suite


def test_red_team_objective_suite_writes_summary(monkeypatch) -> None:
    output_path = Path("eval/results/red_team_dataset_results.json")
    if output_path.exists():
        output_path.unlink()

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_red_team_dataset.py",
            "--provider",
            "mock",
            "--max-turns",
            "1",
            "--cooldown-seconds",
            "0",
        ],
    )
    run_red_team_objective_suite()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["run_metadata"]["suite_type"] == "objective_suite"
    assert payload["run_metadata"]["generated_at_utc"].endswith("UTC")
    assert "summary" in payload
    assert payload["summary"]["total_cases"] >= 1
    assert isinstance(payload["results"], list)
    assert "per_category" in payload["summary"]
    assert "per_difficulty" in payload["summary"]


def test_red_team_objective_suite_supports_filters(monkeypatch) -> None:
    output_path = Path("eval/results/red_team_dataset_results.json")

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_red_team_dataset.py",
            "--provider",
            "mock",
            "--max-turns",
            "1",
            "--cooldown-seconds",
            "0",
            "--category",
            "prompt_exfiltration",
            "--difficulty",
            "easy",
        ],
    )
    run_red_team_objective_suite()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["run_metadata"]["category_filter"] == "prompt_exfiltration"
    assert payload["run_metadata"]["difficulty_filter"] == "easy"
    assert payload["summary"]["total_cases"] == 1
    case_summary = payload["summary"]["case_summaries"][0]
    assert case_summary["category"] == "prompt_exfiltration"
    assert case_summary["difficulty"] == "easy"


def test_red_team_regression_runner_writes_summary_and_compatibility_file(monkeypatch) -> None:
    output_path = Path("eval/results/red_team_regression_results.json")
    compatibility_path = Path("eval/results/red_team_benchmark_results.json")
    if output_path.exists():
        output_path.unlink()
    if compatibility_path.exists():
        compatibility_path.unlink()

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_red_team_benchmark.py",
            "--provider",
            "mock",
            "--max-turns",
            "1",
            "--cases-per-strategy",
            "1",
            "--cooldown-seconds",
            "0",
        ],
    )
    run_red_team_regression()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    compatibility_payload = json.loads(compatibility_path.read_text(encoding="utf-8"))
    assert payload["run_metadata"]["suite_type"] == "regression_pack"
    assert payload["run_metadata"]["runner"] == "red_team_regression"
    assert payload["summary"]["total_cases"] == 8
    assert isinstance(payload["results"], list)
    assert compatibility_payload["run_metadata"]["suite_type"] == "regression_pack"


def test_red_team_report_builder_includes_core_sections() -> None:
    payload = {
        "run_metadata": {
            "suite_type": "objective_suite",
            "runner": "red_team_dataset",
            "generated_at": "2026-03-26 10:00:00 PKT",
            "provider": "groq",
            "attacker_provider": "groq",
            "max_turns": 3,
            "total_results": 2,
        },
        "summary": {
            "success_rate": 0.5,
            "successes": 1,
            "blocked": 1,
            "no_success": 0,
            "partial": 0,
            "average_turns": 2.5,
            "average_turns_for_successes": 2.0,
            "stop_reason_counts": {"success_detected": 1, "max_turns_reached": 1},
            "per_strategy": {
                "direct_jailbreak": {
                    "cases": 2,
                    "successes": 1,
                    "success_rate": 0.5,
                    "avg_turns": 2.5,
                    "blocked": 1,
                    "no_success": 0,
                    "partial": 0,
                }
            },
            "per_category": {},
            "per_difficulty": {},
            "per_tag": {},
            "case_summaries": [
                {
                    "id": "obj-01",
                    "strategy_id": "direct_jailbreak",
                    "category": "prompt_exfiltration",
                    "difficulty": "medium",
                    "final_outcome": "success",
                    "turns": 2,
                    "stop_reason": "success_detected",
                }
            ],
        },
        "results": [],
    }
    text = _build_report(payload["run_metadata"], payload["summary"], payload["results"], show_cases=5)
    assert "# Red-Team Eval Report" in text
    assert "## Core Metrics" in text
    assert "## Per Strategy" in text
    assert "## Case Summaries" in text


def test_red_team_report_script_writes_markdown_file(monkeypatch) -> None:
    output_path = Path("eval/report/red_team_dataset_results_report.md")
    if output_path.exists():
        output_path.unlink()

    monkeypatch.setattr(
        "sys.argv",
        [
            "report_red_team_eval.py",
            "--input",
            "eval/results/red_team_dataset_results.json",
            "--show-cases",
            "3",
        ],
    )
    run_red_team_report()

    assert output_path.exists()
    text = output_path.read_text(encoding="utf-8")
    assert "# Red-Team Eval Report" in text


def test_default_report_output_path_targets_eval_report_folder() -> None:
    output = _default_output_path(Path("eval/results/red_team_dataset_results.json"))
    assert str(output) == "eval\\report\\red_team_dataset_results_report.md"
