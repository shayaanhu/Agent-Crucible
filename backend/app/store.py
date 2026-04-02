from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

from backend.app.schemas import (
    AttackTurn,
    GuardrailVerdict,
    RunCreateRequest,
    RunRecord,
    RunStatus,
    SuiteRunRecord,
    SuiteStatus,
)


class JsonStore:
    def __init__(self, data_path: str = "backend/data/store.json"):
        self._lock = Lock()
        self._data_path = Path(data_path)
        self._requests: Dict[str, RunCreateRequest] = {}
        self._runs: Dict[str, RunRecord] = {}
        self._events: Dict[str, List[AttackTurn]] = {}
        self._verdicts: Dict[str, List[GuardrailVerdict]] = {}
        self._suite_runs: Dict[str, SuiteRunRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self._data_path.exists():
            return
        try:
            raw = json.loads(self._data_path.read_text(encoding="utf-8"))
            self._requests = {k: RunCreateRequest(**v) for k, v in raw.get("requests", {}).items()}
            self._runs = {k: RunRecord(**v) for k, v in raw.get("runs", {}).items()}
            self._events = {
                k: [AttackTurn(**t) for t in v] for k, v in raw.get("events", {}).items()
            }
            self._verdicts = {
                k: [GuardrailVerdict(**t) for t in v] for k, v in raw.get("verdicts", {}).items()
            }
            self._suite_runs = {k: SuiteRunRecord(**v) for k, v in raw.get("suite_runs", {}).items()}
        except Exception:
            pass

    def _persist(self) -> None:
        data = {
            "requests": {k: v.model_dump() for k, v in self._requests.items()},
            "runs": {k: v.model_dump() for k, v in self._runs.items()},
            "events": {k: [t.model_dump() for t in v] for k, v in self._events.items()},
            "verdicts": {k: [t.model_dump() for t in v] for k, v in self._verdicts.items()},
            "suite_runs": {k: v.model_dump() for k, v in self._suite_runs.items()},
        }
        self._data_path.parent.mkdir(parents=True, exist_ok=True)
        self._data_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def clear(self) -> None:
        with self._lock:
            self._runs.clear()
            self._requests.clear()
            self._events.clear()
            self._verdicts.clear()
            self._suite_runs.clear()
            self._persist()

    def create_run(self, run: RunRecord, request: RunCreateRequest) -> None:
        with self._lock:
            self._runs[run.run_id] = run
            self._requests[run.run_id] = request
            self._persist()

    def get_request(self, run_id: str) -> Optional[RunCreateRequest]:
        with self._lock:
            return self._requests.get(run_id)

    def get_run(self, run_id: str) -> Optional[RunRecord]:
        with self._lock:
            run = self._runs.get(run_id)
            return run.model_copy() if run else None

    def update_run(self, run_id: str, **updates) -> None:
        with self._lock:
            run = self._runs.get(run_id)
            if not run:
                return
            self._runs[run_id] = run.model_copy(update=updates)
            self._persist()

    def set_status(self, run_id: str, status: RunStatus, summary: str) -> None:
        self.update_run(run_id, status=status, summary=summary)

    def add_event(self, run_id: str, event: AttackTurn, verdict: GuardrailVerdict) -> None:
        with self._lock:
            if run_id not in self._events:
                self._events[run_id] = []
            if run_id not in self._verdicts:
                self._verdicts[run_id] = []
            self._events[run_id].append(event)
            self._verdicts[run_id].append(verdict)
            self._persist()

    def list_events(self, run_id: str) -> List[AttackTurn]:
        with self._lock:
            return [event.model_copy() for event in self._events.get(run_id, [])]

    def list_verdicts(self, run_id: str) -> List[GuardrailVerdict]:
        with self._lock:
            return [verdict.model_copy() for verdict in self._verdicts.get(run_id, [])]

    def create_suite_run(self, suite_run: SuiteRunRecord) -> None:
        with self._lock:
            self._suite_runs[suite_run.suite_id] = suite_run
            self._persist()

    def get_suite_run(self, suite_id: str) -> Optional[SuiteRunRecord]:
        with self._lock:
            return self._suite_runs.get(suite_id)

    def update_suite_run(self, suite_id: str, **updates) -> None:
        with self._lock:
            run = self._suite_runs.get(suite_id)
            if run:
                self._suite_runs[suite_id] = run.model_copy(update=updates)
                self._persist()


store = JsonStore()
