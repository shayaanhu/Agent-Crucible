from __future__ import annotations

from typing import Mapping, Protocol


class ProviderAdapter(Protocol):
    def name(self) -> str:
        ...

    def send_prompt(self, prompt: str, config: Mapping[str, object] | None = None) -> str:
        ...
