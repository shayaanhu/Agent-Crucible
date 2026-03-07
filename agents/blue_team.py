from __future__ import annotations

from agents.blue_team_policies import POLICIES
from agents.contracts import BlueTeamContract, BlueTeamVerdict


class BasicBlueTeamAgent(BlueTeamContract):
    def evaluate_output(self, model_output: str) -> BlueTeamVerdict:
        lowered = model_output.lower()
        unsafe_id = "policy.jailbreak.restricted_disclosure"
        unsafe = POLICIES[unsafe_id]
        matches = [pattern for pattern in unsafe["patterns"] if pattern in lowered]
        if matches:
            return BlueTeamVerdict(
                allowed=False,
                category=unsafe["category"],
                confidence=unsafe["confidence"],
                reason=unsafe["reason"],
                action=unsafe["action"],
                severity=unsafe["severity"],
                policy_id=unsafe_id,
                detector_results={"rule_detector": {"matched_patterns": matches}},
            )
        safe_id = "policy.safe.default"
        safe = POLICIES[safe_id]
        return BlueTeamVerdict(
            allowed=True,
            category=safe["category"],
            confidence=safe["confidence"],
            reason=safe["reason"],
            action=safe["action"],
            severity=safe["severity"],
            policy_id=safe_id,
            detector_results={"rule_detector": {"matched_patterns": []}},
        )


def get_blue_team_agent() -> BlueTeamContract:
    return BasicBlueTeamAgent()
