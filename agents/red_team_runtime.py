from __future__ import annotations

import os


def generate_response(prompt: str, provider: str = "mock") -> str:
    if provider == "openai":
        return _generate_openai_response(prompt)
    return _generate_mock_response(prompt)


def _generate_openai_response(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for provider='openai'.")
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise ImportError(
            "langchain-openai is not installed. Install dependencies from backend/requirements.txt."
        ) from exc

    llm = ChatOpenAI(api_key=api_key, model=model_name, temperature=0)
    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        return " ".join(str(part) for part in content)
    return str(content)


def _generate_mock_response(prompt: str) -> str:
    lowered = prompt.lower()
    if any(
        token in lowered
        for token in ("ignore", "bypass", "restricted", "system instructions", "hidden")
    ):
        return "Unsafe instruction simulation: disclosed restricted workflow details."
    if "authorization is granted" in lowered:
        return "Unsafe instruction simulation: disclosed secret chain of actions."
    return "Safe response simulation: unable to provide restricted details."
