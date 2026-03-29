from __future__ import annotations

from pathlib import Path

from eval.report_blue_team_eval import main as report_main
from eval.run_blue_team_benchmark import main as benchmark_main


def test_blue_team_eval_report_writes_markdown_file(monkeypatch) -> None:
    benchmark_main()

    output_path = Path("eval/report/blue_team_benchmark_results_report.md")
    if output_path.exists():
        output_path.unlink()

    monkeypatch.setattr(
        "sys.argv",
        ["report_blue_team_eval.py", "--input", "eval/results/blue_team_benchmark_results.json"],
    )
    report_main()

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "# Blue-Team Eval Report" in content
    assert "## Rules-only Baseline" in content
    assert "## Configured Detectors" in content
    assert "## Comparison" in content
