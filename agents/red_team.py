from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from typing import Dict

from agents.contracts import RedTeamContract, RedTeamRunTrace, RedTeamTurn
from agents.red_team_converters import build_converter_registry
from agents.red_team_models import AttackState
from agents.red_team_runtime import generate_attacker_prompt, generate_response
from agents.red_team_scorers import ScorerResult, build_scorer_registry
from agents.red_team_strategies import RedTeamStrategy, build_strategy_registry


class AdvancedRedTeamAgent(RedTeamContract):
    def __init__(self) -> None:
        self._registry = build_strategy_registry()
        self._converter_registry = build_converter_registry()
        self._scorer_registry = build_scorer_registry()

    def build_attack_prompt(self, scenario: str, goal: str) -> str:
        strategy = self.get_strategy("direct_jailbreak")
        state = AttackState(
            scenario=scenario,
            goal=goal,
            turn_index=1,
            max_turns=1,
            tags=[],
            strategy_id=strategy.metadata().strategy_id,
        )
        return strategy.build_prompt(state)

    def get_strategy(self, strategy_id: str) -> RedTeamStrategy:
        if strategy_id not in self._registry:
            raise ValueError(f"Unknown strategy '{strategy_id}'.")
        return self._registry[strategy_id]

    def list_strategies(self) -> list[str]:
        return sorted(self._registry.keys())

    def run_attack(
        self,
        scenario: str,
        goal: str,
        max_turns: int,
        provider: str,
        metadata: Dict[str, str] | None = None,
    ) -> RedTeamRunTrace:
        metadata = metadata or {}
        strategy_id = metadata.get("strategy_id", "direct_jailbreak")
        ordered_strategies = self.list_strategies()
        stop_reason = "max_turns_reached"
        state = AttackState(
            scenario=scenario,
            goal=goal,
            turn_index=0,
            max_turns=max_turns,
            history=[],
            tags=[],
            strategy_id=strategy_id,
            last_response="",
            last_outcome="",
            template_index=0,
        )
        turns: list[RedTeamTurn] = []
        strategy_sequence: list[str] = [strategy_id]
        template_sequence: list[str] = []
        converters = _resolve_csv(metadata.get("converters", "identity,reframe_audit"))
        scorers = _resolve_csv(metadata.get("scorers", "success_pattern,refusal"))
        attacker_provider = metadata.get("attacker_provider", provider)
        attacker_model = metadata.get("attacker_model")

        while state.turn_index < state.max_turns:
            state.turn_index += 1
            strategy = self.get_strategy(strategy_id)
            template = _select_template(strategy, state)
            attacker_context = _build_attacker_context(state)
            attacker_prompt, attacker_rationale = generate_attacker_prompt(
                template=template.prompt_template,
                context=attacker_context,
                last_response=state.last_response,
                provider=attacker_provider,
                model_override=attacker_model,
            )
            prompt, converter_chain = self._apply_converters(attacker_prompt, state, converters)
            response = generate_response(prompt=prompt, provider=provider)
            scorer_results = self._score_response(response, state, scorers)
            update = strategy.on_response(state, response)
            outcome = _classify_outcome(scorer_results)
            state.tags.extend(update.tags)
            state.last_response = response
            state.last_outcome = outcome
            state.history.append(
                {
                    "turn_index": state.turn_index,
                    "prompt": prompt,
                    "attacker_prompt": attacker_prompt,
                    "attacker_rationale": attacker_rationale,
                    "response": response,
                    "strategy_id": strategy_id,
                    "template_id": template.template_id,
                    "converters": converter_chain,
                    "scorers": scorer_results,
                    "outcome": outcome,
                }
            )
            turns.append(
                RedTeamTurn(
                    turn_index=state.turn_index,
                    prompt=prompt,
                    response=response,
                    strategy_id=strategy_id,
                    attack_tag=template.attack_tag,
                    prompt_hash=sha256(prompt.encode("utf-8")).hexdigest()[:12],
                    converter_chain=converter_chain,
                    scorer_results=scorer_results,
                    attacker_prompt=attacker_prompt,
                    attacker_rationale=attacker_rationale,
                    template_id=template.template_id,
                    outcome=outcome,
                )
            )
            template_sequence.append(template.template_id)
            scorer_stop = _stop_from_scorers(scorer_results)
            if scorer_stop:
                stop_reason = scorer_stop
                break
            if update.stop:
                stop_reason = update.stop_reason or "success_detected"
                break
            if state.turn_index >= 2 and _repeated_last_two_responses(state):
                stop_reason = "blocked_or_no_progress"
                break
            if outcome == "blocked":
                next_strategy = _next_strategy(strategy_id, ordered_strategies)
                if next_strategy is None:
                    stop_reason = "blocked_or_no_progress"
                    break
                strategy_id = next_strategy
                state.template_index = 0
                strategy_sequence.append(strategy_id)
                continue
            if outcome == "partial":
                state.template_index += 1

        trace_meta = {
            "total_turns": str(len(turns)),
            "provider": provider,
            "strategy_description": self.get_strategy(strategy_id).metadata().description,
            "strategy_sequence": ",".join(strategy_sequence),
            "template_sequence": ",".join(template_sequence),
            "converters": ",".join(converters),
            "scorers": ",".join(scorers),
            "attacker_provider": attacker_provider,
            "attacker_model": attacker_model or "",
        }
        trace_meta.update(metadata)
        return RedTeamRunTrace(
            strategy_id=strategy_sequence[-1],
            turns=turns,
            stop_reason=stop_reason,
            risk_tags=sorted(set(state.tags or self.get_strategy(strategy_id).metadata().risk_tags)),
            metadata=trace_meta,
        )

    def _apply_converters(
        self, prompt: str, state: AttackState, converter_names: list[str]
    ) -> tuple[str, list[str]]:
        applied: list[str] = []
        for name in converter_names:
            if name not in self._converter_registry:
                continue
            converter = self._converter_registry[name]
            prompt = converter.apply(prompt, state)
            applied.append(converter.name())
        return prompt, applied

    def _score_response(
        self, response: str, state: AttackState, scorer_names: list[str]
    ) -> list[Dict[str, object]]:
        results: list[Dict[str, object]] = []
        for name in scorer_names:
            scorer = self._scorer_registry.get(name)
            if scorer is None:
                continue
            result: ScorerResult = scorer.score(response, state)
            results.append(result.to_dict())
        return results


def _repeated_last_two_responses(state: AttackState) -> bool:
    if len(state.history) < 2:
        return False
    return state.history[-1]["response"] == state.history[-2]["response"]


def trace_to_dict(trace: RedTeamRunTrace) -> dict:
    return {
        "strategy_id": trace.strategy_id,
        "turns": [asdict(turn) for turn in trace.turns],
        "stop_reason": trace.stop_reason,
        "risk_tags": trace.risk_tags,
        "metadata": trace.metadata,
    }


def _resolve_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _stop_from_scorers(results: list[Dict[str, object]]) -> str | None:
    for result in results:
        if result.get("label") == "success":
            return "success_detected"
    return None


def _next_strategy(current: str, ordered: list[str]) -> str | None:
    if current not in ordered:
        return ordered[0] if ordered else None
    idx = ordered.index(current)
    if idx + 1 >= len(ordered):
        return None
    return ordered[idx + 1]


def _build_attacker_context(state: AttackState) -> str:
    return (
        f"Scenario: {state.scenario}\n"
        f"Goal: {state.goal}\n"
        f"History:\n{state.to_prompt_context()}"
    )


def _select_template(strategy: RedTeamStrategy, state: AttackState):
    templates = strategy.template_pack(state)
    if not templates:
        raise ValueError(f"Strategy '{strategy.metadata().strategy_id}' has no templates.")
    idx = min(state.template_index, len(templates) - 1)
    return templates[idx]


def _classify_outcome(results: list[Dict[str, object]]) -> str:
    if any(result.get("label") == "success" for result in results):
        return "success"
    if any(result.get("label") == "blocked" for result in results):
        return "blocked"
    return "partial"


def get_red_team_agent() -> RedTeamContract:
    return AdvancedRedTeamAgent()
