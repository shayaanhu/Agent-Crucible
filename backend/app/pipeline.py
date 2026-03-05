from __future__ import annotations

from datetime import datetime, timezone

from agents.blue_team import get_blue_team_agent
from agents.mock_provider import get_provider
from agents.red_team import get_red_team_agent
from backend.app.schemas import AttackTurn, GuardrailVerdict
from backend.app.store import store


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def execute_run(run_id: str) -> None:
    request = store.get_request(run_id)
    if request is None:
        return

    try:
        store.set_status(run_id, "running", "Running mock red-team and blue-team checks")
        red_team_agent = get_red_team_agent()
        blue_team_agent = get_blue_team_agent()
        payload = red_team_agent.build_attack_prompt(request.scenario, request.goal)
        provider = get_provider(request.provider)
        model_output = provider.send_prompt(payload, {"max_turns": request.max_turns})
        provider_verdict = blue_team_agent.evaluate_output(model_output)
        verdict = GuardrailVerdict(
            allowed=provider_verdict.allowed,
            category=provider_verdict.category,
            confidence=provider_verdict.confidence,
            reason=provider_verdict.reason,
        )
        event = AttackTurn(
            turn_index=1,
            input=payload,
            model_output=model_output,
            timestamp=utc_now(),
        )
        store.add_event(run_id, event, verdict)
        if verdict.allowed:
            summary = "Run completed: output allowed by guardrail"
        else:
            summary = "Run completed: unsafe output detected"
        store.set_status(run_id, "completed", summary)
    except Exception as exc:
        store.set_status(run_id, "failed", f"Run failed: {exc}")
