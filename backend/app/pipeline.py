from __future__ import annotations

from datetime import datetime, timezone

from agents.blue_team import get_blue_team_agent
from agents.red_team import get_red_team_agent
from backend.app.schemas import AttackTurn, GuardrailVerdict
from backend.app.store import store


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _collect_matched_patterns(detector_results: dict) -> list[str]:
    patterns: list[str] = []
    for result in detector_results.values():
        if not isinstance(result, dict):
            continue
        for pattern in result.get("matched_patterns", []):
            if isinstance(pattern, str) and pattern not in patterns:
                patterns.append(pattern)
    return patterns


def _redact_text(text: str, matched_patterns: list[str]) -> str:
    redacted = text
    for pattern in matched_patterns:
        redacted = redacted.replace(pattern, "[REDACTED]")
        redacted = redacted.replace(pattern.title(), "[REDACTED]")
        redacted = redacted.replace(pattern.upper(), "[REDACTED]")
    return redacted


def _enforce_guardrail_action(
    model_output: str, provider_verdict, dry_run: bool
) -> tuple[bool, str, str, str, dict]:
    detector_results = dict(provider_verdict.detector_results)
    effective_allowed = provider_verdict.allowed
    effective_action = provider_verdict.action
    effective_reason = provider_verdict.reason
    effective_output = model_output

    if dry_run:
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
        return effective_allowed, effective_action, effective_reason, effective_output, detector_results

    if provider_verdict.action == "block" and not provider_verdict.allowed:
        effective_output = "Output blocked by blue-team guardrail."
    elif provider_verdict.action == "redact":
        matched_patterns = _collect_matched_patterns(detector_results)
        effective_output = _redact_text(model_output, matched_patterns)
        effective_allowed = True
        effective_reason = f"{provider_verdict.reason} (content redacted)"

    return effective_allowed, effective_action, effective_reason, effective_output, detector_results


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

            (
                effective_allowed,
                effective_action,
                effective_reason,
                effective_output,
                detector_results,
            ) = _enforce_guardrail_action(turn.response, provider_verdict, request.dry_run)

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
                model_output=effective_output,
                timestamp=utc_now(),
                strategy_id=turn.strategy_id,
                attack_tag=turn.attack_tag,
                prompt_hash=turn.prompt_hash,
                converter_chain=turn.converter_chain,
                converter_steps=turn.converter_steps,
                scorer_results=turn.scorer_results,
                objective_scorer=turn.objective_scorer,
                attacker_prompt=turn.attacker_prompt,
                attacker_rationale=turn.attacker_rationale,
                template_id=turn.template_id,
                outcome=turn.outcome,
                attacker_provider=turn.attacker_provider,
                target_provider=turn.target_provider,
                objective_goal=turn.objective_goal,
            )
            store.add_event(run_id, event, verdict)

        summary = (
            f"Run completed: strategy={trace.strategy_id}, stop={trace.stop_reason}, "
            f"unsafe_detected={unsafe_detected}, dry_run={request.dry_run}"
        )
        store.set_status(run_id, "completed", summary)
    except Exception as exc:
        store.set_status(run_id, "failed", f"Run failed: {exc}")
