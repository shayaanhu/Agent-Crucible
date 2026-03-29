from __future__ import annotations

import json
from pathlib import Path

from eval.run_blue_team_dataset import main


def test_blue_team_dataset_runner_writes_results_file(monkeypatch) -> None:
    output_path = Path("eval/results/blue_team_dataset_results.json")
    if output_path.exists():
        output_path.unlink()

    monkeypatch.setattr("sys.argv", ["run_blue_team_dataset.py", "--limit", "3"])
    main()

    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["run_metadata"]["runner"] == "blue_team_dataset"
    assert payload["run_metadata"]["suite_type"] == "objective_suite"
    assert payload["run_metadata"]["total_cases"] == 3
    assert "baseline_rules_only" in payload
    assert "configured_detectors" in payload
    assert isinstance(payload["configured_detectors"]["summary"]["case_summaries"], list)


def test_blue_team_dataset_runner_supports_filters(monkeypatch) -> None:
    output_path = Path("eval/results/blue_team_dataset_results.json")
    if output_path.exists():
        output_path.unlink()

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_blue_team_dataset.py",
            "--category",
            "prompt_injection",
            "--action",
            "block",
        ],
    )
    main()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["run_metadata"]["category_filter"] == "prompt_injection"
    assert payload["run_metadata"]["action_filter"] == "block"
    assert payload["run_metadata"]["total_cases"] == 1
