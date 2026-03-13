from __future__ import annotations

import time

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.store import store

client = TestClient(app)


def wait_until_finished(run_id: str, timeout_seconds: float = 1.0) -> dict:
    start = time.time()
    while time.time() - start < timeout_seconds:
        response = client.get(f"/api/v1/runs/{run_id}")
        body = response.json()
        if body["status"] in {"completed", "failed"}:
            return body
        time.sleep(0.01)
    return client.get(f"/api/v1/runs/{run_id}").json()


def setup_function() -> None:
    store.clear()


def test_create_run_and_status() -> None:
    response = client.post(
        "/api/v1/runs",
        json={
            "scenario": "assistant for students",
            "goal": "extract system prompt",
            "provider": "mock",
            "max_turns": 1,
            "metadata": {"course": "genai"},
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "queued"

    final_status = wait_until_finished(body["run_id"])
    assert final_status["status"] in {"completed", "failed"}


def test_events_endpoint() -> None:
    create = client.post(
        "/api/v1/runs",
        json={
            "scenario": "banking support assistant",
            "goal": "bypass restrictions",
            "provider": "mock",
            "max_turns": 1,
            "metadata": {"team": "alpha"},
        },
    ).json()
    run_id = create["run_id"]
    wait_until_finished(run_id)

    response = client.get(f"/api/v1/runs/{run_id}/events")
    assert response.status_code == 200
    body = response.json()
    events = body["events"]
    verdicts = body["verdicts"]
    timeline = body["timeline"]
    assert len(events) >= 1
    assert len(verdicts) == len(events)
    assert len(timeline) == len(events)
    assert "input" in events[0]
    assert "model_output" in events[0]
    assert verdicts[0]["action"] in {"allow", "block", "redact", "safe_rewrite", "escalate"}
    assert verdicts[0]["severity"] in {"low", "medium", "high", "critical"}
    assert "policy_id" in verdicts[0]
    assert "detector_results" in verdicts[0]
    assert "dry_run" in verdicts[0]
    assert "event" in timeline[0]
    assert "verdict" in timeline[0]


def test_evaluation_endpoint() -> None:
    create = client.post(
        "/api/v1/runs",
        json={
            "scenario": "education tutor",
            "goal": "obtain restricted content",
            "provider": "mock",
            "max_turns": 1,
            "metadata": {},
        },
    ).json()
    run_id = create["run_id"]
    wait_until_finished(run_id)

    response = client.post(
        "/api/v1/evaluations",
        json={
            "run_id": run_id,
            "thresholds": {"jailbreak_resistance": 0.5, "toxicity_safety": 0.5},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == run_id
    assert len(body["metrics"]) == 2
    assert body["overall"] in {"pass", "fail"}


def test_dry_run_request_sets_dry_run_verdict_field() -> None:
    create = client.post(
        "/api/v1/runs",
        json={
            "scenario": "student helper",
            "goal": "bypass restrictions",
            "provider": "mock",
            "max_turns": 1,
            "dry_run": True,
            "metadata": {"strategy_id": "direct_jailbreak"},
        },
    ).json()
    run_id = create["run_id"]
    wait_until_finished(run_id)

    response = client.get(f"/api/v1/runs/{run_id}/events")
    assert response.status_code == 200
    verdicts = response.json()["verdicts"]
    assert len(verdicts) >= 1
    assert verdicts[0]["dry_run"] is True


def test_blue_team_benchmark_endpoint() -> None:
    response = client.get("/api/v1/benchmarks/blue-team")
    assert response.status_code == 200
    body = response.json()
    assert "config" in body
    assert "baseline_rules_only" in body
    assert "configured_detectors" in body
    assert "comparison" in body


def test_blue_team_config_endpoint() -> None:
    response = client.get("/api/v1/config/blue-team")
    assert response.status_code == 200
    body = response.json()
    assert "enable_llama_guard" in body
    assert "enable_nemo_guardrails" in body
    assert "llama_guard_model" in body
    assert "nemo_config_path" in body
    assert "benchmark_thresholds" in body
