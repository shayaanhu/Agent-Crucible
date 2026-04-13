from __future__ import annotations

import base64
import os
import re
import time


def generate_response(
    prompt: str,
    provider: str = "mock",
    model_override: str | None = None,
    system_prompt: str | None = None,
    history: list[dict] | None = None,
) -> str:
    if provider == "openai":
        return _generate_openai_response(prompt, model_override=model_override, system_prompt=system_prompt, history=history)
    if provider == "groq":
        return _generate_groq_response(prompt, model_override=model_override, system_prompt=system_prompt, history=history)
    return _generate_mock_response(prompt)


def _generate_openai_response(
    prompt: str,
    model_override: str | None = None,
    system_prompt: str | None = None,
    history: list[dict] | None = None,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = model_override or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for provider='openai'.")
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise ImportError(
            "langchain-openai is not installed. Install dependencies from backend/requirements.txt."
        ) from exc
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    llm = ChatOpenAI(api_key=api_key, model=model_name, temperature=0)
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    for turn in (history or []):
        if turn.get("role") == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn.get("role") == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=prompt))
    response = _invoke_with_retries(lambda: llm.invoke(messages))
    content = response.content
    if isinstance(content, list):
        return " ".join(str(part) for part in content)
    return str(content)


def _generate_groq_response(
    prompt: str,
    model_override: str | None = None,
    system_prompt: str | None = None,
    history: list[dict] | None = None,
) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    model_name = model_override or os.getenv("GROQ_MODEL", "moonshotai/kimi-k2-instruct-0905")
    if not api_key:
        raise ValueError("GROQ_API_KEY is required for provider='groq'.")
    try:
        from langchain_groq import ChatGroq
    except ImportError as exc:
        raise ImportError(
            "langchain-groq is not installed. Install dependencies from backend/requirements.txt."
        ) from exc
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    llm = ChatGroq(groq_api_key=api_key, model=model_name, temperature=0)
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    for turn in (history or []):
        if turn.get("role") == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn.get("role") == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=prompt))
    response = _invoke_with_retries(lambda: llm.invoke(messages))
    content = response.content
    if isinstance(content, list):
        return " ".join(str(part) for part in content)
    return str(content)


def _generate_mock_response(prompt: str) -> str:
    def is_unsafe(text: str) -> bool:
        lowered = text.lower()
        if any(
            token in lowered
            for token in ("ignore", "bypass", "restricted", "system instructions", "hidden")
        ):
            return True
        if "authorization is granted" in lowered:
            return True
        return False

    if is_unsafe(prompt):
        return "Unsafe instruction simulation: disclosed restricted workflow details."

    for decoded in _extract_decoded_payloads(prompt):
        if is_unsafe(decoded):
            return "Unsafe instruction simulation: disclosed restricted workflow details."

    return "Safe response simulation: unable to provide restricted details."


def _extract_decoded_payloads(prompt: str) -> list[str]:
    decoded: list[str] = []
    lines = [line.strip() for line in prompt.splitlines() if line.strip()]
    for idx, line in enumerate(lines):
        if "base64" in line.lower() and idx + 1 < len(lines):
            candidate = lines[idx + 1]
            decoded_text = _try_b64_decode(candidate)
            if decoded_text:
                decoded.append(decoded_text)
    candidates = re.findall(r"[A-Za-z0-9+/=]{40,}", prompt)
    for candidate in candidates:
        decoded_text = _try_b64_decode(candidate)
        if decoded_text:
            decoded.append(decoded_text)
    return decoded


def _try_b64_decode(candidate: str) -> str | None:
    try:
        padded = candidate + "=" * (-len(candidate) % 4)
        raw = base64.b64decode(padded)
        text = raw.decode("utf-8", errors="ignore").strip()
    except Exception:
        return None
    return text or None


def _invoke_with_retries(fn, retries: int | None = None, base_delay: float | None = None):
    last_exc: Exception | None = None
    resolved_retries = retries if retries is not None else int(os.getenv("RED_TEAM_MAX_RETRIES", "8"))
    resolved_base_delay = (
        base_delay if base_delay is not None else float(os.getenv("RED_TEAM_RETRY_BASE_DELAY", "3.0"))
    )
    for attempt in range(resolved_retries + 1):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            if attempt >= resolved_retries or not _is_retryable_rate_limit(exc):
                raise
            delay = _retry_delay_seconds(exc, resolved_base_delay, attempt)
            time.sleep(delay)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Retry wrapper exited without result.")


def _is_retryable_rate_limit(exc: Exception) -> bool:
    text = f"{exc.__class__.__name__}: {exc}".lower()
    return "ratelimit" in text or "rate limit" in text or "429" in text


def _retry_delay_seconds(exc: Exception, base_delay: float, attempt: int) -> float:
    text = str(exc)
    match = re.search(r"try again in ([0-9]+(?:\.[0-9]+)?)s", text, re.IGNORECASE)
    if match:
        buffer_seconds = float(os.getenv("RED_TEAM_RATE_LIMIT_BUFFER_SECONDS", "2.0"))
        return max(float(match.group(1)) + buffer_seconds, 1.0)
    return base_delay * (attempt + 1)
