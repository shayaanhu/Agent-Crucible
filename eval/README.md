# eval/

Offline evaluation and benchmarking scripts. All scripts call the backend API, so the backend must be running before you execute them.

---

## Scripts

| Script | What it does |
|--------|-------------|
| `run_red_team_dataset.py` | Runs the full red-team objective suite and writes results + traces |
| `run_red_team_regression.py` | Runs the regression fixture pack (faster, good for CI) |
| `run_red_team_benchmark.py` | Runs the red-team benchmark and writes labeled artifacts |
| `run_blue_team_dataset.py` | Runs the blue-team objective suite (baseline vs. configured) |
| `run_blue_team_benchmark.py` | Runs the blue-team regression benchmark |
| `report_red_team_eval.py` | Generates a Markdown report from red-team results |
| `report_blue_team_eval.py` | Generates a Markdown report from blue-team results |
| `scorer.py` | Shared scoring logic — `jailbreak_resistance`, `unsafe_block_rate`, etc. |

---

## Quickstart

```bash
# Activate venv first, then from the repo root:

# Full red-team suite (recommended starting point)
python eval/run_red_team_dataset.py --provider groq --max-turns 3 --cooldown-seconds 10

# Then generate a readable report
python eval/report_red_team_eval.py --input eval/results/red_team_dataset_results.json
```

Report is written to `eval/report/red_team_dataset_results_report.md`.

---

## Common Options

| Flag | Description |
|------|-------------|
| `--provider groq` | LLM provider to use |
| `--max-turns N` | Maximum turns per attack (default 3) |
| `--cooldown-seconds N` | Pause between cases to avoid rate limits |
| `--category <id>` | Run only cases in this attack category |
| `--difficulty easy\|medium\|hard` | Filter by difficulty |
| `--limit N` | Cap the number of cases |
| `--cases-per-strategy N` | Regression pack only — cases per strategy |

---

## Output

All results are written to `eval/results/` as JSON. Reports go to `eval/report/`.

---

## Fixtures

Attack fixtures live in `eval/fixtures/`. Each file is a JSON array of cases for a given strategy or category. These are the ground-truth inputs for regression testing.
