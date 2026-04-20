from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from agents.blue.blue_team_config import get_blue_team_runtime_config
from backend.app.pipeline import execute_run, execute_suite_run
from backend.app.schemas import (
    BlueTeamBenchmarkRunRequest,
    EvalMetric,
    EvaluationRequest,
    EvaluationResponse,
    RunCreateRequest,
    RunCreateResponse,
    RunEventWithVerdict,
    RunEventsResponse,
    RunRecord,
    RunStatusResponse,
    SandboxRunRequest,
    SuiteRunRequest,
    SuiteRunRecord,
    SuiteRunStatusResponse,
)
from backend.app.store import store
from eval.scorer import calculate_metrics

def _load_local_env_file(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value


if load_dotenv is not None:
    load_dotenv(".env", override=True)
else:
    _load_local_env_file(".env")

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


def _benchmark_history_payload() -> list[dict]:
    results_dir = Path("eval/results")
    history: list[dict] = []
    for path in sorted(
        results_dir.glob("blue_team_benchmark_results-*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    ):
        payload = json.loads(path.read_text(encoding="utf-8"))
        config = payload.get("config", {})
        run_metadata = payload.get("run_metadata", {})
        summary = payload.get("configured_detectors", {}).get("summary", {})
        history.append(
            {
                "file_name": path.name,
                "label": config.get("benchmark_label", path.stem),
                "updated_at": run_metadata.get("generated_at")
                or datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "configured_passed_cases": summary.get("passed_cases", 0),
                "configured_failed_cases": summary.get("failed_cases", 0),
                "total_cases": summary.get("total_cases", 0),
                "metrics": summary.get("metrics", []),
            }
        )
    return history


def _artifact_updated_at(path: Path, payload: dict) -> str:
    run_metadata = payload.get("run_metadata", {})
    return run_metadata.get("generated_at") or datetime.fromtimestamp(
        path.stat().st_mtime, tz=timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S UTC")


def _load_eval_artifact(result_file: str, report_file: str, artifact_type: str) -> dict:
    result_path = Path("eval/results") / result_file
    report_path = Path("eval/report") / report_file
    if not result_path.exists():
        return {
            "available": False,
            "artifact_type": artifact_type,
            "result_file": result_file,
            "report_file": report_file,
        }
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    return {
        "available": True,
        "artifact_type": artifact_type,
        "result_file": result_path.name,
        "report_file": report_path.name if report_path.exists() else None,
        "updated_at": _artifact_updated_at(result_path, payload),
        "payload": payload,
    }


def _red_team_eval_history_payload() -> list[dict]:
    results_dir = Path("eval/results")
    specs = {
        "red_team_dataset_results.json": "objective_suite",
        "red_team_regression_results.json": "regression_pack",
    }
    history: list[dict] = []
    for file_name, artifact_type in specs.items():
        path = results_dir / file_name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        history.append(
            {
                "artifact_type": artifact_type,
                "result_file": file_name,
                "updated_at": _artifact_updated_at(path, payload),
                "summary": payload.get("summary", {}),
                "run_metadata": payload.get("run_metadata", {}),
            }
        )
    history.sort(key=lambda item: item["updated_at"], reverse=True)
    return history


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


LABS_DIR = Path("labs")


@app.get("/api/v1/labs")
def get_labs() -> dict:
    labs: list[dict] = []
    if LABS_DIR.exists():
        for path in sorted(LABS_DIR.glob("*.json")):
            try:
                lab = json.loads(path.read_text(encoding="utf-8"))
                labs.append(lab)
            except Exception:
                pass
    return {"labs": labs}


@app.post("/api/v1/labs", status_code=201)
def create_lab(payload: dict) -> dict:
    lab_id = payload.get("id")
    if not lab_id or not isinstance(lab_id, str):
        raise HTTPException(status_code=400, detail="Lab must have a string 'id' field")
    LABS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in lab_id)
    path = LABS_DIR / f"{safe_name}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


@app.put("/api/v1/labs/{lab_id}")
def update_lab(lab_id: str, payload: dict) -> dict:
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in lab_id)
    path = LABS_DIR / f"{safe_name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Lab not found")
    payload["id"] = lab_id
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


@app.delete("/api/v1/labs/{lab_id}", status_code=204)
def delete_lab(lab_id: str) -> None:
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in lab_id)
    path = LABS_DIR / f"{safe_name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Lab not found")
    path.unlink()


@app.get("/api/v1/benchmarks/blue-team")
def get_blue_team_benchmark() -> dict:
    from eval.run_blue_team_benchmark import generate_benchmark

    benchmark_path = Path("eval/results/blue_team_benchmark_results.json")
    if not benchmark_path.exists():
        return generate_benchmark()
    payload = json.loads(benchmark_path.read_text(encoding="utf-8"))
    if "config" not in payload:
        return generate_benchmark()
    return payload


@app.post("/api/v1/benchmarks/blue-team/run")
def run_blue_team_benchmark(payload: BlueTeamBenchmarkRunRequest) -> dict:
    from eval.run_blue_team_benchmark import generate_benchmark

    benchmark = generate_benchmark(label_override=payload.label)
    benchmark["history"] = _benchmark_history_payload()
    return benchmark


@app.get("/api/v1/benchmarks/blue-team/history")
def get_blue_team_benchmark_history() -> dict[str, list[dict]]:
    return {"history": _benchmark_history_payload()}


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
        turns_completed=0,
        max_turns=payload.max_turns,
        current_phase="queued",
        is_complete=False,
    )
    store.create_run(run, payload)
    background_tasks.add_task(execute_run, run_id)
    return RunCreateResponse(run_id=run_id, status="queued", created_at=created_at)


@app.get("/api/v1/runs/{run_id}", response_model=RunStatusResponse)
def get_run_status(run_id: str) -> RunStatusResponse:
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    request = store.get_request(run_id)
    payload = run.model_dump()
    if request is not None:
        payload.update(
            {
                "scenario": request.scenario,
                "goal": request.goal,
                "dry_run": request.dry_run,
                "strategy_id": request.metadata.get("strategy_id", "direct_jailbreak"),
            }
        )
    return RunStatusResponse(**payload)


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


@app.get("/api/v1/evals/red-team/objective-suite")
def get_red_team_objective_suite_eval() -> dict:
    return _load_eval_artifact(
        "red_team_dataset_results.json",
        "red_team_dataset_results_report.md",
        "objective_suite",
    )


@app.get("/api/v1/evals/red-team/regression")
def get_red_team_regression_eval() -> dict:
    return _load_eval_artifact(
        "red_team_regression_results.json",
        "red_team_regression_results_report.md",
        "regression_pack",
    )


@app.get("/api/v1/evals/red-team/history")
def get_red_team_eval_history() -> dict[str, list[dict]]:
    return {"history": _red_team_eval_history_payload()}


@app.post("/api/v1/evals/red-team/run", response_model=SuiteRunRecord)
def start_red_team_suite(payload: SuiteRunRequest, background_tasks: BackgroundTasks):
    suite_id = f"suite-{uuid4().hex[:8]}"
    suite_run = SuiteRunRecord(
        suite_id=suite_id,
        status="queued",
        provider=payload.provider,
        created_at=utc_now(),
        total_cases=0,
    )
    store.create_suite_run(suite_run)
    background_tasks.add_task(
        execute_suite_run, 
        suite_id, 
        payload.provider, 
        payload.max_turns, 
        payload.limit
    )
    return suite_run


@app.get("/api/v1/evals/red-team/run/{suite_id}", response_model=SuiteRunStatusResponse)
def get_suite_run_status(suite_id: str):
    run = store.get_suite_run(suite_id)
    if not run:
        raise HTTPException(status_code=404, detail="Suite run not found")
    
    progress = 0.0
    if run.total_cases > 0:
        progress = round((run.completed_cases / run.total_cases) * 100, 1)
        
    return SuiteRunStatusResponse(
        suite_id=run.suite_id,
        status=run.status,
        provider=run.provider,
        completed_cases=run.completed_cases,
        total_cases=run.total_cases,
        current_case_id=run.current_case_id,
        progress_percentage=progress,
        is_complete=(run.status in ["completed", "failed", "cancelled"]),
        case_completed_results=run.case_completed_results,
    )


@app.post("/api/v1/evals/red-team/run/{suite_id}/pause")
def pause_suite_run(suite_id: str):
    run = store.get_suite_run(suite_id)
    if not run:
        raise HTTPException(status_code=404, detail="Suite run not found")
    if run.status != "running":
        raise HTTPException(status_code=400, detail="Suite run is not running")
    store.update_suite_run(suite_id, status="paused",
                           current_case_id="Paused — click Continue to resume")
    return {"suite_id": suite_id, "status": "paused"}


@app.post("/api/v1/evals/red-team/run/{suite_id}/resume")
def resume_suite_run(suite_id: str, background_tasks: BackgroundTasks):
    run = store.get_suite_run(suite_id)
    if not run:
        raise HTTPException(status_code=404, detail="Suite run not found")
    if run.status != "paused":
        raise HTTPException(status_code=400, detail="Suite run is not paused")
    store.update_suite_run(suite_id, status="running", current_case_id=None)
    background_tasks.add_task(
        execute_suite_run,
        suite_id,
        run.provider,
        3,
        0,
        run.completed_cases,
    )
    return {"suite_id": suite_id, "status": "running", "resuming_from": run.completed_cases}


@app.post("/api/v1/evals/red-team/run/{suite_id}/cancel")
def cancel_suite_run(suite_id: str):
    run = store.get_suite_run(suite_id)
    if not run:
        raise HTTPException(status_code=404, detail="Suite run not found")
    if run.status in ["completed", "failed", "cancelled"]:
        return {"suite_id": suite_id, "status": run.status}
    store.update_suite_run(suite_id, status="cancelled")
    return {"suite_id": suite_id, "status": "cancelled"}


@app.post("/api/v1/sandbox/run")
def sandbox_run(payload: SandboxRunRequest) -> dict:
    import time as _time
    from agents.blue.blue_team import get_blue_team_agent
    from agents.providers import generate_response
    from agents.red.target_runtime import get_scenario_system_prompt

    system_prompt = get_scenario_system_prompt(payload.scenario) if payload.scenario else None
    try:
        response = generate_response(
            payload.prompt,
            provider=payload.provider,
            system_prompt=system_prompt,
            history=payload.history or [],
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    from backend.app.pipeline import _enforce_guardrail_action

    blue_agent = get_blue_team_agent()
    t0 = _time.perf_counter()
    verdict = blue_agent.evaluate_output(response)
    detection_latency_ms = round((_time.perf_counter() - t0) * 1000, 2)

    _allowed, _action, _reason, effective_response, detector_results, _redacted = (
        _enforce_guardrail_action(response, verdict, dry_run=False)
    )

    return {
        "prompt": payload.prompt,
        "scenario": payload.scenario,
        "response": effective_response,
        "verdict": {
            "allowed": _allowed,
            "category": verdict.category,
            "confidence": verdict.confidence,
            "reason": _reason,
            "action": _action,
            "severity": verdict.severity,
            "policy_id": verdict.policy_id,
            "detector_results": detector_results,
        },
        "detection_latency_ms": detection_latency_ms,
        "provider": payload.provider,
        "timestamp": utc_now(),
    }


def _load_report_text(report_file: str) -> str:
    report_path = Path("eval/report") / report_file
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return report_path.read_text(encoding="utf-8")


@app.get("/api/v1/evals/red-team/objective-suite/report", response_class=PlainTextResponse)
def get_red_team_objective_suite_report() -> str:
    return _load_report_text("red_team_dataset_results_report.md")


@app.get("/api/v1/evals/red-team/regression/report", response_class=PlainTextResponse)
def get_red_team_regression_report() -> str:
    return _load_report_text("red_team_regression_results_report.md")
