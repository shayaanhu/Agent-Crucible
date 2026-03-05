# Backend

FastAPI service for run orchestration and evaluation APIs.

Implemented endpoints:
1. `POST /api/v1/runs`
2. `GET /api/v1/runs/{run_id}`
3. `GET /api/v1/runs/{run_id}/events`
4. `POST /api/v1/evaluations`

Run locally:
1. `pip install -r backend/requirements.txt`
2. `python -m uvicorn backend.app.main:app --reload`
