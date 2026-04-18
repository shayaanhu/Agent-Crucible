# backend/

FastAPI service that orchestrates red-team runs, invokes the blue-team guardrail pipeline, and exposes results through a REST API.

---

## Running

From the repo root (with venv active):

```bash
python -m uvicorn backend.app.main:app --reload
```

- Base URL: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

---

## Structure

```
backend/
├── app/
│   ├── main.py       API routes and app setup
│   ├── pipeline.py   Run execution logic — calls red-team agent, then blue-team guardrails
│   ├── schemas.py    Pydantic request/response models
│   └── store.py      In-memory run and event store
├── tests/            Pytest test suite
├── data/             Static fixtures used by tests
└── requirements.txt  Python dependencies
```

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/runs` | Start a new red-team run |
| `GET` | `/api/v1/runs/{run_id}` | Get run status and summary |
| `GET` | `/api/v1/runs/{run_id}/events` | Get per-turn events with verdicts |
| `POST` | `/api/v1/sandbox/run` | Single-shot sandbox prompt |
| `POST` | `/api/v1/suite/run` | Start the full attack suite |
| `GET` | `/api/v1/suite/{run_id}` | Get suite progress and results |
| `POST` | `/api/v1/evaluations` | Score a completed run |

---

## Tests

```bash
python -m pytest backend/tests -q
```
