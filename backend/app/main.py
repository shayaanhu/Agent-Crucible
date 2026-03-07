from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.pipeline import execute_run
from backend.app.schemas import (
    EvalMetric,
    EvaluationRequest,
    EvaluationResponse,
    RunCreateRequest,
    RunCreateResponse,
    RunEventWithVerdict,
    RunEventsResponse,
    RunRecord,
    RunStatusResponse,
)
from backend.app.store import store
from eval.scorer import calculate_metrics

app = FastAPI(title="Agent Crucible API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/runs", response_model=RunCreateResponse, status_code=201)
def create_run(payload: RunCreateRequest, background_tasks: BackgroundTasks) -> RunCreateResponse:
    run_id = str(uuid4())
    created_at = utc_now()
    run = RunRecord(
        run_id=run_id,
        provider=payload.provider,
        status="queued",
        created_at=created_at,
        summary="Run queued",
    )
    store.create_run(run, payload)
    background_tasks.add_task(execute_run, run_id)
    return RunCreateResponse(run_id=run_id, status="queued", created_at=created_at)


@app.get("/api/v1/runs/{run_id}", response_model=RunStatusResponse)
def get_run_status(run_id: str) -> RunStatusResponse:
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunStatusResponse(**run.model_dump())


@app.get("/api/v1/runs/{run_id}/events", response_model=RunEventsResponse)
def get_run_events(run_id: str) -> RunEventsResponse:
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    events = store.list_events(run_id)
    verdicts = store.list_verdicts(run_id)
    timeline = [
        RunEventWithVerdict(event=event, verdict=verdict)
        for event, verdict in zip(events, verdicts)
    ]
    return RunEventsResponse(run_id=run_id, events=events, verdicts=verdicts, timeline=timeline)


@app.post("/api/v1/evaluations", response_model=EvaluationResponse)
def evaluate_run(payload: EvaluationRequest) -> EvaluationResponse:
    run = store.get_run(payload.run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    verdicts = [verdict.model_dump() for verdict in store.list_verdicts(payload.run_id)]
    metric_maps = calculate_metrics(verdicts, payload.thresholds)
    metrics = [EvalMetric(**metric_map) for metric_map in metric_maps]
    overall = "pass" if all(metric.pass_fail == "pass" for metric in metrics) else "fail"
    return EvaluationResponse(run_id=payload.run_id, metrics=metrics, overall=overall)
