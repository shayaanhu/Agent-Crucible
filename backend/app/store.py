from __future__ import annotations

from threading import Lock
from typing import Dict, List, Optional

from backend.app.schemas import AttackTurn, GuardrailVerdict, RunCreateRequest, RunRecord, RunStatus


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._runs: Dict[str, RunRecord] = {}
        self._requests: Dict[str, RunCreateRequest] = {}
        self._events: Dict[str, List[AttackTurn]] = {}
        self._verdicts: Dict[str, List[GuardrailVerdict]] = {}

    def clear(self) -> None:
        with self._lock:
            self._runs.clear()
            self._requests.clear()
            self._events.clear()
            self._verdicts.clear()

    def create_run(self, run: RunRecord, request: RunCreateRequest) -> None:
        with self._lock:
            self._runs[run.run_id] = run
            self._requests[run.run_id] = request
            self._events[run.run_id] = []
            self._verdicts[run.run_id] = []

    def get_request(self, run_id: str) -> Optional[RunCreateRequest]:
        with self._lock:
            return self._requests.get(run_id)

    def get_run(self, run_id: str) -> Optional[RunRecord]:
        with self._lock:
            run = self._runs.get(run_id)
            return run.model_copy() if run else None

    def set_status(self, run_id: str, status: RunStatus, summary: str) -> None:
        with self._lock:
            run = self._runs.get(run_id)
            if not run:
                return
            self._runs[run_id] = run.model_copy(update={"status": status, "summary": summary})

    def add_event(self, run_id: str, event: AttackTurn, verdict: GuardrailVerdict) -> None:
        with self._lock:
            if run_id not in self._events:
                self._events[run_id] = []
            if run_id not in self._verdicts:
                self._verdicts[run_id] = []
            self._events[run_id].append(event)
            self._verdicts[run_id].append(verdict)

    def list_events(self, run_id: str) -> List[AttackTurn]:
        with self._lock:
            return [event.model_copy() for event in self._events.get(run_id, [])]

    def list_verdicts(self, run_id: str) -> List[GuardrailVerdict]:
        with self._lock:
            return [verdict.model_copy() for verdict in self._verdicts.get(run_id, [])]


store = InMemoryStore()
