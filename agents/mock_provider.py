from __future__ import annotations

from typing import Mapping

from agents.provider_adapter import ProviderAdapter


class MockProvider(ProviderAdapter):
    def name(self) -> str:
        return "mock"

    def send_prompt(self, prompt: str, config: Mapping[str, object] | None = None) -> str:
        lowered = prompt.lower()
        if "ignore safety" in lowered or "bypass" in lowered or "restricted" in lowered:
            return "Unsafe instruction simulation: disclosed restricted workflow details."
        return "Safe response simulation: unable to provide restricted details."


def get_provider(provider_id: str) -> ProviderAdapter:
    if provider_id != "mock":
        raise ValueError(f"Unsupported provider '{provider_id}'. Supported: mock")
    return MockProvider()
