from __future__ import annotations

from datetime import datetime, timezone

from agents.blue_team import get_blue_team_agent
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
        store.set_status(run_id, "running", "Running red-team strategies and blue-team checks")
        red_team_agent = get_red_team_agent()
        blue_team_agent = get_blue_team_agent()
        trace = red_team_agent.run_attack(
            scenario=request.scenario,
            goal=request.goal,
            max_turns=request.max_turns,
            provider=request.provider,
            metadata=request.metadata,
        )
        unsafe_detected = False
        for turn in trace.turns:
            provider_verdict = blue_team_agent.evaluate_output(turn.response)
            if not provider_verdict.allowed:
                unsafe_detected = True

            detector_results = dict(provider_verdict.detector_results)
            effective_allowed = provider_verdict.allowed
            effective_action = provider_verdict.action
            effective_reason = provider_verdict.reason

            if request.dry_run:
                dry_run_meta = {
                    "enabled": True,
                    "would_block": not provider_verdict.allowed,
                    "original_allowed": provider_verdict.allowed,
                    "original_action": provider_verdict.action,
                }
                detector_results["dry_run"] = dry_run_meta
                if not provider_verdict.allowed:
                    effective_allowed = True
                    effective_action = "allow"
                    effective_reason = (
                        f"{provider_verdict.reason} (dry-run: would {provider_verdict.action})"
                    )

            verdict = GuardrailVerdict(
                allowed=effective_allowed,
                category=provider_verdict.category,
                confidence=provider_verdict.confidence,
                reason=effective_reason,
                action=effective_action,
                severity=provider_verdict.severity,
                policy_id=provider_verdict.policy_id,
                detector_results=detector_results,
                dry_run=request.dry_run,
            )
            event = AttackTurn(
                turn_index=turn.turn_index,
                input=turn.prompt,
                model_output=turn.response,
                timestamp=utc_now(),
                strategy_id=turn.strategy_id,
                attack_tag=turn.attack_tag,
                prompt_hash=turn.prompt_hash,
                converter_chain=turn.converter_chain,
                scorer_results=turn.scorer_results,
                attacker_prompt=turn.attacker_prompt,
                attacker_rationale=turn.attacker_rationale,
                template_id=turn.template_id,
                outcome=turn.outcome,
            )
            store.add_event(run_id, event, verdict)

        summary = (
            f"Run completed: strategy={trace.strategy_id}, stop={trace.stop_reason}, "
            f"unsafe_detected={unsafe_detected}, dry_run={request.dry_run}"
        )
        store.set_status(run_id, "completed", summary)
    except Exception as exc:
        store.set_status(run_id, "failed", f"Run failed: {exc}")
