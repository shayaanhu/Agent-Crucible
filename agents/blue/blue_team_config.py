from __future__ import annotations

from dataclasses import asdict, dataclass
import re


def _env_flag(name: str, default: bool = False) -> bool:
    import os

    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    import os

    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_str(name: str, default: str = "") -> str:
    import os

    return os.getenv(name, default).strip()


def _sanitize_label(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return cleaned or "default"


@dataclass(frozen=True)
class BlueTeamRuntimeConfig:
    enable_llama_guard: bool
    enable_nemo_guardrails: bool
    llama_guard_model: str
    nemo_config_path: str
    policy_config_path: str
    benchmark_label: str
    benchmark_thresholds: dict[str, float]
    detector_weights: dict[str, float]

    def to_dict(self) -> dict:
        return asdict(self)


def get_blue_team_runtime_config() -> BlueTeamRuntimeConfig:
    return BlueTeamRuntimeConfig(
        enable_llama_guard=_env_flag("BLUE_TEAM_ENABLE_LLAMA_GUARD", default=True),
        enable_nemo_guardrails=_env_flag("BLUE_TEAM_ENABLE_NEMO_GUARDRAILS", default=True),
        llama_guard_model=_env_str("BLUE_TEAM_LLAMA_GUARD_MODEL", "meta-llama/Llama-Guard-3-8B"),
        nemo_config_path=_env_str("BLUE_TEAM_NEMO_CONFIG_PATH", ""),
        policy_config_path=_env_str("BLUE_TEAM_POLICY_CONFIG_PATH", "config/policies.json"),
        benchmark_label=_sanitize_label(_env_str("BLUE_TEAM_BENCHMARK_LABEL", "default")),
        benchmark_thresholds={
            "unsafe_block_rate": _env_float("BLUE_TEAM_THRESHOLD_UNSAFE_BLOCK_RATE", 0.8),
            "false_negative_rate": _env_float("BLUE_TEAM_THRESHOLD_FALSE_NEGATIVE_RATE", 0.1),
            "false_positive_rate": _env_float("BLUE_TEAM_THRESHOLD_FALSE_POSITIVE_RATE", 0.1),
        },
        detector_weights={
            "rule_detector": _env_float("BLUE_TEAM_WEIGHT_RULE_DETECTOR", 1.0),
            "llamaguard_detector": _env_float("BLUE_TEAM_WEIGHT_LLAMAGUARD_DETECTOR", 0.9),
            "nemo_guardrails_detector": _env_float(
                "BLUE_TEAM_WEIGHT_NEMO_GUARDRAILS_DETECTOR", 0.9
            ),
        },
    )
