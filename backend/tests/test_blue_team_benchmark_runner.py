from __future__ import annotations

import json
from pathlib import Path

from eval.run_blue_team_benchmark import main


def test_blue_team_benchmark_runner_writes_results_file() -> None:
    output_path = Path("eval/results/blue_team_benchmark_results.json")
    if output_path.exists():
        output_path.unlink()

    main()

    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert "summary" in payload
    assert "results" in payload
    assert payload["summary"]["total_cases"] >= 1
    assert payload["summary"]["passed_cases"] >= 1
    assert isinstance(payload["summary"]["policy_counts"], dict)
    assert isinstance(payload["summary"]["action_counts"], dict)
    assert isinstance(payload["summary"]["metrics"], list)
