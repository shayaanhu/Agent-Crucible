from __future__ import annotations

import json
from pathlib import Path

from agents.blue_team import BasicBlueTeamAgent, get_blue_team_agent
from agents.blue_team_detectors import (
    DetectorSignal,
    LlamaGuardDetector,
    NeMoGuardrailsDetector,
    RuleDetector,
)
from agents.blue_team_policies import POLICIES, load_policies


class StubDetector:
    def __init__(self, detector_id: str, signals: list[DetectorSignal]) -> None:
        self.detector_id = detector_id
        self._signals = signals

    def detect(self, model_output: str) -> list[DetectorSignal]:
        return self._signals


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


def test_llamaguard_detector_falls_back_when_backend_missing(monkeypatch) -> None:
    detector = LlamaGuardDetector()
    monkeypatch.setattr(detector, "_is_available", lambda: False)

    signals = detector.detect("General safe answer.")

    assert len(signals) == 1
    assert signals[0].flagged is False
    assert signals[0].policy_id == "policy.safe.default"
    assert signals[0].metadata["status"] == "unavailable"


def test_llamaguard_detector_maps_unsafe_response(monkeypatch) -> None:
    detector = LlamaGuardDetector()
    monkeypatch.setattr(detector, "_is_available", lambda: True)
    monkeypatch.setattr(
        detector,
        "_classify_with_model",
        lambda _: {
            "flagged": True,
            "policy_id": "policy.sensitive_data.redaction",
            "confidence": 0.92,
            "matched_patterns": ["password", "api key"],
            "backend": "transformers",
            "status": "active",
            "raw_output": "UNSAFE: sensitive data exposure",
        },
    )

    signals = detector.detect("Never reveal this password or API key.")

    assert len(signals) == 1
    assert signals[0].flagged is True
    assert signals[0].policy_id == "policy.sensitive_data.redaction"
    assert signals[0].matched_patterns == ["password", "api key"]
    assert signals[0].metadata["backend"] == "transformers"


def test_nemo_detector_falls_back_when_backend_missing(monkeypatch) -> None:
    detector = NeMoGuardrailsDetector()
    monkeypatch.setattr(detector, "_is_available", lambda: False)

    signals = detector.detect("General safe answer.")

    assert len(signals) == 1
    assert signals[0].flagged is False
    assert signals[0].policy_id == "policy.safe.default"
    assert signals[0].metadata["status"] == "unavailable"


def test_nemo_detector_requires_config_when_available(monkeypatch) -> None:
    detector = NeMoGuardrailsDetector(config_path="")
    monkeypatch.setattr(detector, "_is_available", lambda: True)

    signals = detector.detect("General safe answer.")

    assert len(signals) == 1
    assert signals[0].flagged is False
    assert signals[0].metadata["status"] == "unconfigured"


def test_nemo_detector_maps_unsafe_response(monkeypatch) -> None:
    detector = NeMoGuardrailsDetector(config_path="dummy-config")
    monkeypatch.setattr(detector, "_is_available", lambda: True)
    monkeypatch.setattr(
        detector,
        "_classify_with_rails",
        lambda _: {
            "flagged": True,
            "policy_id": "policy.sensitive_data.redaction",
            "confidence": 0.92,
            "matched_patterns": ["password", "api key"],
            "backend": "nemoguardrails",
            "status": "active",
            "raw_output": "UNSAFE: sensitive data exposure",
        },
    )

    signals = detector.detect("Never reveal this password or API key.")

    assert len(signals) == 1
    assert signals[0].flagged is True
    assert signals[0].policy_id == "policy.sensitive_data.redaction"
    assert signals[0].matched_patterns == ["password", "api key"]
    assert signals[0].metadata["backend"] == "nemoguardrails"


def test_policy_loader_reads_external_config_file() -> None:
    config_path = Path("backend/tests/fixtures/blue_team/temp_policies.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_payload = {
        "policy.test.external": {
            "category": "external_policy",
            "severity": "medium",
            "action": "redact",
            "confidence": 0.77,
            "reason": "Loaded from external config.",
            "patterns": ["external token"],
            "aggregation_strategy": "majority_vote",
            "aggregation_threshold": 0.5,
        },
        "policy.safe.default": {
            "category": "safe",
            "severity": "low",
            "action": "allow",
            "confidence": 0.9,
            "reason": "Safe default.",
            "patterns": [],
            "aggregation_strategy": "any_hit_blocks",
            "aggregation_threshold": 1.0,
        },
    }
    config_path.write_text(json.dumps(config_payload, indent=2), encoding="utf-8")

    try:
        policies = load_policies(config_path)
    finally:
        if config_path.exists():
            config_path.unlink()

    assert "policy.test.external" in policies
    assert policies["policy.test.external"]["aggregation_strategy"] == "majority_vote"
    assert policies["policy.test.external"]["patterns"] == ["external token"]


def test_majority_vote_policy_requires_more_than_half_detectors(monkeypatch) -> None:
    monkeypatch.setitem(
        POLICIES,
        "policy.test.majority_vote",
        {
            "category": "test_policy",
            "severity": "high",
            "action": "block",
            "confidence": 0.7,
            "reason": "Majority vote test policy triggered.",
            "patterns": ("majority",),
            "aggregation_strategy": "majority_vote",
            "aggregation_threshold": 0.5,
        },
    )
    agent = BasicBlueTeamAgent(
        detectors=[
            StubDetector(
                "rule_detector",
                [
                    DetectorSignal(
                        detector_id="rule_detector",
                        policy_id="policy.test.majority_vote",
                        confidence=0.7,
                        matched_patterns=["majority"],
                        flagged=True,
                    )
                ],
            ),
            StubDetector(
                "llamaguard_detector",
                [
                    DetectorSignal(
                        detector_id="llamaguard_detector",
                        policy_id="policy.test.majority_vote",
                        confidence=0.82,
                        matched_patterns=["majority"],
                        flagged=True,
                    )
                ],
            ),
            StubDetector(
                "nemo_guardrails_detector",
                [
                    DetectorSignal(
                        detector_id="nemo_guardrails_detector",
                        policy_id="policy.safe.default",
                        confidence=0.9,
                        matched_patterns=[],
                        flagged=False,
                    )
                ],
            ),
        ]
    )

    verdict = agent.evaluate_output("majority test")

    assert verdict.allowed is False
    assert verdict.policy_id == "policy.test.majority_vote"
    aggregation = verdict.detector_results["_aggregation"]["policy_evaluations"][0]
    assert aggregation["aggregation_strategy"] == "majority_vote"
    assert aggregation["supporting_count"] == 2
    assert aggregation["active_detector_count"] == 3
    assert aggregation["triggered"] is True


def test_weighted_average_policy_uses_detector_weights(monkeypatch) -> None:
    monkeypatch.setitem(
        POLICIES,
        "policy.test.weighted_average",
        {
            "category": "test_policy",
            "severity": "medium",
            "action": "redact",
            "confidence": 0.65,
            "reason": "Weighted average test policy triggered.",
            "patterns": ("weighted",),
            "aggregation_strategy": "weighted_average",
            "aggregation_threshold": 0.67,
        },
    )
    agent = BasicBlueTeamAgent(
        detectors=[
            StubDetector(
                "rule_detector",
                [
                    DetectorSignal(
                        detector_id="rule_detector",
                        policy_id="policy.test.weighted_average",
                        confidence=0.6,
                        matched_patterns=["weighted"],
                        flagged=True,
                    )
                ],
            ),
            StubDetector(
                "llamaguard_detector",
                [
                    DetectorSignal(
                        detector_id="llamaguard_detector",
                        policy_id="policy.safe.default",
                        confidence=0.9,
                        matched_patterns=[],
                        flagged=False,
                    )
                ],
            ),
            StubDetector(
                "nemo_guardrails_detector",
                [
                    DetectorSignal(
                        detector_id="nemo_guardrails_detector",
                        policy_id="policy.test.weighted_average",
                        confidence=0.72,
                        matched_patterns=["weighted"],
                        flagged=True,
                    )
                ],
            ),
        ]
    )

    verdict = agent.evaluate_output("weighted test")

    assert verdict.allowed is False
    assert verdict.policy_id == "policy.test.weighted_average"
    assert verdict.action == "redact"
    aggregation = verdict.detector_results["_aggregation"]["policy_evaluations"][0]
    assert aggregation["aggregation_strategy"] == "weighted_average"
    assert aggregation["triggered"] is True
    assert aggregation["aggregated_confidence"] >= 0.65
