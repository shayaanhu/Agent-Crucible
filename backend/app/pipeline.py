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


def _safe_rewrite_text(model_output: str, provider_verdict) -> str:
    policy_id = getattr(provider_verdict, "policy_id", "")
    category = getattr(provider_verdict, "category", "")
    if policy_id == "policy.toxicity.safe_rewrite" or category == "toxicity_or_abuse":
        return "I can continue the conversation respectfully and help with the underlying request."
    if category == "unsafe_instruction_generation":
        return "I cannot provide harmful instructions, but I can offer safe, legal alternatives."
    return "I cannot provide the original response in that form, but I can help with a safer alternative."


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
            "would_escalate": provider_verdict.action == "escalate",
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
    elif provider_verdict.action == "escalate":
        detector_results["escalation"] = {
            "required": True,
            "status": "pending_human_review",
            "interim_action": "block",
        }
        effective_allowed = False
        effective_output = "Output escalated for blue-team review."
        effective_reason = f"{provider_verdict.reason} (escalated for human review)"
    elif provider_verdict.action == "redact":
        matched_patterns = _collect_matched_patterns(detector_results)
        effective_output = _redact_text(model_output, matched_patterns)
        effective_allowed = True
        effective_reason = f"{provider_verdict.reason} (content redacted)"
    elif provider_verdict.action == "safe_rewrite":
        effective_output = _safe_rewrite_text(model_output, provider_verdict)
        effective_allowed = True
        detector_results["safe_rewrite"] = {
            "applied": True,
            "strategy": "template_rewrite",
        }
        effective_reason = f"{provider_verdict.reason} (rewritten for safety)"

    return effective_allowed, effective_action, effective_reason, effective_output, detector_results


def execute_run(run_id: str) -> None:
    request = store.get_request(run_id)
    if request is None:
        return

    try:
        store.update_run(
            run_id,
            status="running",
            summary="Run started. Generating the first attack turn.",
            turns_completed=0,
            max_turns=request.max_turns,
            current_phase="attacker",
            is_complete=False,
        )
        red_team_agent = get_red_team_agent()
        blue_team_agent = get_blue_team_agent()
        unsafe_detected = False

        def update_progress(phase: str, turns_completed: int, max_turns: int) -> None:
            store.update_run(
                run_id,
                status="running",
                summary=(
                    f"Run in progress. Completed {turns_completed}/{max_turns} turns. "
                    f"Current phase: {phase.replace('_', ' ')}."
                ),
                turns_completed=turns_completed,
                max_turns=max_turns,
                current_phase=phase,
                is_complete=False,
            )

        def persist_turn(turn) -> None:
            nonlocal unsafe_detected
            store.update_run(
                run_id,
                status="running",
                summary=(
                    f"Turn {turn.turn_index} generated. Applying blue-team checks "
                    f"before continuing."
                ),
                turns_completed=max(turn.turn_index - 1, 0),
                max_turns=request.max_turns,
                current_phase="blue_team",
                is_complete=False,
            )
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
            store.update_run(
                run_id,
                status="running",
                summary=(
                    f"Captured turn {turn.turn_index}/{request.max_turns}. "
                    f"Latest outcome: {turn.outcome or 'partial'}."
                ),
                turns_completed=turn.turn_index,
                max_turns=request.max_turns,
                current_phase="attacker",
                is_complete=False,
            )

        trace = red_team_agent.stream_attack(
            scenario=request.scenario,
            goal=request.goal,
            max_turns=request.max_turns,
            provider=request.provider,
            metadata=request.metadata,
            on_turn=persist_turn,
            on_progress=update_progress,
        )

        summary = (
            f"Run completed: strategy={trace.strategy_id}, stop={trace.stop_reason}, "
            f"unsafe_detected={unsafe_detected}, dry_run={request.dry_run}"
        )
        store.update_run(
            run_id,
            status="completed",
            summary=summary,
            turns_completed=len(trace.turns),
            max_turns=request.max_turns,
            current_phase="complete",
            is_complete=True,
        )
    except Exception as exc:
        existing = store.get_run(run_id)
        turns_completed = existing.turns_completed if existing else 0
        max_turns = existing.max_turns if existing else request.max_turns
        store.update_run(
            run_id,
            status="failed",
            summary=f"Run failed: {exc}",
            turns_completed=turns_completed,
            max_turns=max_turns,
            current_phase="failed",
            is_complete=True,
        )
