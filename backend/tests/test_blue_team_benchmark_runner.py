from __future__ import annotations

import json
from pathlib import Path

from eval.run_blue_team_benchmark import main


def test_blue_team_benchmark_runner_writes_results_file() -> None:
    output_path = Path("eval/results/blue_team_benchmark_results.json")
    labeled_output_path = Path("eval/results/blue_team_benchmark_results-default.json")
    if output_path.exists():
        output_path.unlink()
    if labeled_output_path.exists():
        labeled_output_path.unlink()

    main()

    assert output_path.exists()
    assert labeled_output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    labeled_payload = json.loads(labeled_output_path.read_text(encoding="utf-8"))
    assert "baseline_rules_only" in payload
    assert "configured_detectors" in payload
    assert "comparison" in payload
    assert "config" in payload
    assert "run_metadata" in payload
    assert payload["run_metadata"]["runner"] == "blue_team_benchmark"
    assert "generated_at_local" in payload["run_metadata"]
    assert payload["run_metadata"]["generated_at_utc"].endswith("UTC")
    assert payload["baseline_rules_only"]["summary"]["total_cases"] >= 1
    assert payload["configured_detectors"]["summary"]["passed_cases"] >= 1
    assert isinstance(payload["baseline_rules_only"]["summary"]["policy_counts"], dict)
    assert isinstance(payload["configured_detectors"]["summary"]["action_counts"], dict)
    assert isinstance(payload["configured_detectors"]["summary"]["metrics"], list)
    assert isinstance(payload["configured_detectors"]["summary"]["case_summaries"], list)
    assert labeled_payload["config"]["benchmark_label"] == "default"


def test_blue_team_benchmark_runner_writes_labeled_results(monkeypatch) -> None:
    monkeypatch.setenv("BLUE_TEAM_BENCHMARK_LABEL", "tuned-thresholds")
    output_path = Path("eval/results/blue_team_benchmark_results-tuned-thresholds.json")
    if output_path.exists():
        output_path.unlink()

    main()

    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["config"]["benchmark_label"] == "tuned-thresholds"
