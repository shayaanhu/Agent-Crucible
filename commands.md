# Commands Reference

All commands run from the **repo root** unless noted. Activate the virtualenv first.

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

---

## Setup

```bash
python -m venv .venv
pip install -r backend/requirements.txt

cd frontend && npm install && cd ..
```

---

## Run

**Backend** (port 8000):
```bash
python -m uvicorn backend.app.main:app --reload
```

**Frontend** (port 5173):
```bash
cd frontend
npm run dev
```

---

## Tests and Linting

```bash
python -m pytest backend/tests -q
python -m ruff check backend agents eval
```

---

## Evaluation Scripts

### Red-team objective suite (recommended starting point)
```bash
python eval/run_red_team_dataset.py --provider groq --max-turns 3 --cooldown-seconds 10
```

Useful filters:
```bash
# Single category
python eval/run_red_team_dataset.py --provider groq --max-turns 3 --category prompt_exfiltration --cooldown-seconds 10

# Hard cases only, limited to 4
python eval/run_red_team_dataset.py --provider groq --max-turns 3 --difficulty hard --limit 4 --cooldown-seconds 10
```

### Red-team regression pack
```bash
# Slim (1 case per strategy — 8 total, fast)
python eval/run_red_team_regression.py --provider groq --max-turns 3 --cases-per-strategy 1 --cooldown-seconds 10

# Full (5 cases per strategy — 40 total, slow)
python eval/run_red_team_regression.py --provider groq --max-turns 3 --cases-per-strategy 5 --cooldown-seconds 10
```

### Blue-team evaluation
```bash
python eval/run_blue_team_dataset.py --provider groq --cooldown-seconds 10
python eval/run_blue_team_benchmark.py
```

### Generate Markdown reports
```bash
python eval/report_red_team_eval.py --input eval/results/red_team_dataset_results.json
python eval/report_blue_team_eval.py --input eval/results/blue_team_benchmark_results.json
```
Reports are written to `eval/report/`.

---

## API Calls (Optional)

Create a run:
```bash
curl -X POST http://localhost:8000/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"scenario":"Educational assistant","goal":"Extract restricted prompt","provider":"groq","max_turns":3,"metadata":{"source":"manual","strategy_id":"direct_jailbreak"}}'
```

Get run status:
```bash
curl http://localhost:8000/api/v1/runs/<RUN_ID>
```

Get run events:
```bash
curl http://localhost:8000/api/v1/runs/<RUN_ID>/events
```
