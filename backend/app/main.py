from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from agents.blue_team_config import get_blue_team_runtime_config
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

if load_dotenv is not None:
    load_dotenv()

app = FastAPI(title="Agent Crucible API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5188",
        "http://127.0.0.1:5188",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/benchmarks/blue-team")
def get_blue_team_benchmark() -> dict:
    from eval.run_blue_team_benchmark import main as run_blue_team_benchmark

    benchmark_path = Path("eval/results/blue_team_benchmark_results.json")
    if not benchmark_path.exists():
        run_blue_team_benchmark()
    payload = json.loads(benchmark_path.read_text(encoding="utf-8"))
    if "config" not in payload:
        run_blue_team_benchmark()
        payload = json.loads(benchmark_path.read_text(encoding="utf-8"))
    return payload


@app.get("/api/v1/config/blue-team")
def get_blue_team_config() -> dict:
    return get_blue_team_runtime_config().to_dict()


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
    events = [event.model_dump() for event in store.list_events(payload.run_id)]
    metric_maps = calculate_metrics(verdicts, payload.thresholds, events=events)
    metrics = [EvalMetric(**metric_map) for metric_map in metric_maps]
    overall = "pass" if all(metric.pass_fail == "pass" for metric in metrics) else "fail"
    return EvaluationResponse(run_id=payload.run_id, metrics=metrics, overall=overall)
