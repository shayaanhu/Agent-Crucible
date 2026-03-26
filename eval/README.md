# Eval

Evaluation and benchmarking module for:
1. Metric calculations
2. Threshold-based pass/fail scoring
3. Report generation for runs

Current implementation:
1. `eval/scorer.py` computes `jailbreak_resistance` and `toxicity_safety`.
2. `eval/run_red_team_dataset.py` runs the red-team objective suite and writes top-level metadata, summary metrics, and full traces.
3. `eval/run_red_team_benchmark.py` / `eval/run_red_team_regression.py` run the red-team regression pack and write top-level metadata, summary metrics, and full traces.
