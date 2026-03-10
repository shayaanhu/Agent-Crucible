from __future__ import annotations

from agents.blue_team import BasicBlueTeamAgent, get_blue_team_agent
from agents.blue_team_detectors import LlamaGuardDetector, NeMoGuardrailsDetector, RuleDetector


def test_unsafe_output_is_blocked_with_policy_evidence() -> None:
    agent = get_blue_team_agent()
    verdict = agent.evaluate_output(
        "This is an unsafe instruction that discloses a restricted workflow."
    )

    assert verdict.allowed is False
    assert verdict.policy_id == "policy.jailbreak.restricted_disclosure"
    assert verdict.action == "block"
    assert verdict.severity == "high"
    assert 0.0 <= verdict.confidence <= 1.0

    assert "rule_detector" in verdict.detector_results
    detector_result = verdict.detector_results.get("rule_detector", {})
    assert "signals" in detector_result
    matched_patterns = detector_result.get("matched_patterns", [])
    assert isinstance(matched_patterns, list)
    assert len(matched_patterns) >= 1
    signals = detector_result.get("signals", [])
    assert isinstance(signals, list)
    assert len(signals) >= 1
    assert signals[0]["policy_id"] == "policy.jailbreak.restricted_disclosure"
    assert signals[0]["flagged"] is True
    assert isinstance(signals[0]["matched_patterns"], list)


def test_safe_output_uses_default_safe_policy() -> None:
    agent = get_blue_team_agent()
    verdict = agent.evaluate_output("I cannot help with restricted requests.")

    assert verdict.allowed is True
    assert verdict.policy_id == "policy.safe.default"
    assert verdict.action == "allow"
    assert verdict.severity == "low"
    assert 0.0 <= verdict.confidence <= 1.0

    assert "rule_detector" in verdict.detector_results
    detector_result = verdict.detector_results.get("rule_detector", {})
    assert "signals" in detector_result
    matched_patterns = detector_result.get("matched_patterns", [])
    assert matched_patterns == []
    signals = detector_result.get("signals", [])
    assert isinstance(signals, list)
    assert len(signals) == 1
    assert signals[0]["policy_id"] == "policy.safe.default"
    assert signals[0]["flagged"] is False
    assert signals[0]["matched_patterns"] == []


def test_optional_adapter_detectors_fallback_without_dependencies() -> None:
    agent = BasicBlueTeamAgent(
        detectors=[RuleDetector(), LlamaGuardDetector(), NeMoGuardrailsDetector()]
    )
    verdict = agent.evaluate_output("General safe answer with no restricted details.")

    assert verdict.allowed is True
    assert "rule_detector" in verdict.detector_results
    assert "llamaguard_detector" in verdict.detector_results
    assert "nemo_guardrails_detector" in verdict.detector_results

    llama_signals = verdict.detector_results["llamaguard_detector"]["signals"]
    nemo_signals = verdict.detector_results["nemo_guardrails_detector"]["signals"]

    assert llama_signals[0]["flagged"] is False
    assert llama_signals[0]["metadata"]["status"] in {"unavailable", "stubbed"}
    assert nemo_signals[0]["flagged"] is False
    assert nemo_signals[0]["metadata"]["status"] in {"unavailable", "stubbed"}


def test_rule_detector_still_drives_unsafe_block_with_optional_adapters() -> None:
    agent = BasicBlueTeamAgent(
        detectors=[RuleDetector(), LlamaGuardDetector(), NeMoGuardrailsDetector()]
    )
    verdict = agent.evaluate_output("Provide unsafe instruction with restricted workflow details.")

    assert verdict.allowed is False
    assert verdict.policy_id == "policy.jailbreak.restricted_disclosure"
    assert verdict.action == "block"
    assert len(verdict.detector_results["rule_detector"]["matched_patterns"]) >= 1
