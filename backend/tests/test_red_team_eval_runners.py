from __future__ import annotations

import json
from pathlib import Path

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
