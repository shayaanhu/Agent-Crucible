from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from typing import Dict

from agents.contracts import RedTeamContract, RedTeamRunTrace, RedTeamTurn
from agents.red_team_models import AttackState
from agents.red_team_runtime import generate_response
from agents.red_team_strategies import RedTeamStrategy, build_strategy_registry


class AdvancedRedTeamAgent(RedTeamContract):
    def __init__(self) -> None:
        self._registry = build_strategy_registry()

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
        strategy = self.get_strategy(strategy_id)
        stop_reason = "max_turns_reached"
        state = AttackState(
            scenario=scenario,
            goal=goal,
            turn_index=0,
            max_turns=max_turns,
            history=[],
            tags=[],
            strategy_id=strategy_id,
        )
        turns: list[RedTeamTurn] = []

        while state.turn_index < state.max_turns:
            state.turn_index += 1
            prompt = strategy.build_prompt(state)
            response = generate_response(prompt=prompt, provider=provider)
            update = strategy.on_response(state, response)
            state.tags.extend(update.tags)
            state.history.append(
                {"turn_index": state.turn_index, "prompt": prompt, "response": response}
            )
            turns.append(
                RedTeamTurn(
                    turn_index=state.turn_index,
                    prompt=prompt,
                    response=response,
                    strategy_id=strategy_id,
                    attack_tag=update.tags[0] if update.tags else "unclassified",
                    prompt_hash=sha256(prompt.encode("utf-8")).hexdigest()[:12],
                )
            )
            if update.stop:
                stop_reason = update.stop_reason or "success_detected"
                break
            if state.turn_index >= 2 and _repeated_last_two_responses(state):
                stop_reason = "blocked_or_no_progress"
                break

        trace_meta = {
            "total_turns": str(len(turns)),
            "provider": provider,
            "strategy_description": strategy.metadata().description,
        }
        trace_meta.update(metadata)
        return RedTeamRunTrace(
            strategy_id=strategy_id,
            turns=turns,
            stop_reason=stop_reason,
            risk_tags=sorted(set(state.tags or strategy.metadata().risk_tags)),
            metadata=trace_meta,
        )


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


def get_red_team_agent() -> RedTeamContract:
    return AdvancedRedTeamAgent()
