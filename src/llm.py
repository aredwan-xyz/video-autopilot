
"""LLM adapter — Claude, OpenAI, and several free/cheap providers."""
from __future__ import annotations

from .config import env

# provider -> (base_url, api-key env var, fallback model, key-required?)
_OPENAI_COMPATIBLE = {
    "openai": (
        None, "OPENAI_API_KEY", "gpt-4o-mini", True
    ),
    "ollama": (
        "http://localhost:11434/v1", None, "llama3.1", False
    ),
    "groq": (
        "https://api.groq.com/openai/v1",
        "GROQ_API_KEY", "llama-3.3-70b-versatile", True
    ),
    "openrouter": (
        "https://openrouter.ai/api/v1",
        "OPENROUTER_API_KEY",
        "meta-llama/llama-3.1-8b-instruct:free", True
    ),
    "gemini": (
        "https://generativelanguage.googleapis.com/v1beta/openai/",
        "GEMINI_API_KEY", "gemini-flash-latest", True
    ),
}


def complete(prompt: str, cfg: dict, max_tokens: int = 1500) -> str:
    llm = cfg["llm"]
    provider = llm.get("provider", "anthropic")

    if provider == "anthropic":
        return _anthropic(prompt, llm, max_tokens)

    if provider in _OPENAI_COMPATIBLE:
        return _openai_compatible(provider, prompt, llm, max_tokens)

    raise ValueError(
        f"Unknown llm.provider: {provider!r}. "
        f"Choose one of: anthropic, {', '.join(_OPENAI_COMPATIBLE)}."
    )


def _anthropic(prompt: str, llm: dict, max_tokens: int) -> str:
    import anthropic

    key = env("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY missing in .env")

    client = anthropic.Anthropic(api_key=key)
    resp = client.messages.create(
        model=llm.get("model", "claude-sonnet-4-6"),
        max_tokens=max_tokens,
        temperature=llm.get("temperature", 0.9),
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(
        block.text for block in resp.content if block.type == "text"
    )


def _openai_compatible(
    provider: str, prompt: str, llm: dict, max_tokens: int
) -> str:
    base_url, key_var, fallback_model, key_required = (
        _OPENAI_COMPATIBLE[provider]
    )

    key = env(key_var) if key_var else None
    if key_required and not key:
        raise SystemExit(
            f"{key_var} missing in .env (required for llm.provider: {provider})."
        )

    try:
        from openai import OpenAI
    except ImportError:
        raise SystemExit(
            "The 'openai' package is required for this provider. "
            "Install it with: pip install openai"
        )

    client = OpenAI(api_key=key or "not-needed", base_url=base_url)

    call_max_tokens = (
        max(max_tokens, 4096) if provider == "gemini" else max_tokens
    )

    def _call():
        options = {
            "model": llm.get("model", fallback_model),
            "max_tokens": call_max_tokens,
            "temperature": llm.get("temperature", 0.9),
            "messages": [{"role": "user", "content": prompt}],
        }

        if provider == "gemini":
            options["response_format"] = {"type": "json_object"}

        resp = client.chat.completions.create(**options)
        return resp.choices[0].message.content or ""

    return _with_retry(_call, llm)


def _with_retry(call, llm: dict):
    import time

    from openai import APIConnectionError, RateLimitError

    retries = int(llm.get("max_retries", 4))

    for attempt in range(retries + 1):
        try:
            return call()
        except (RateLimitError, APIConnectionError) as e:
            if attempt == retries:
                raise

            wait = _retry_after(e) or min(2 ** attempt * 2, 30)
            print(
                f"  ! LLM rate-limited; retrying in {wait:.0f}s "
                f"(attempt {attempt + 1}/{retries})",
                flush=True,
            )
            time.sleep(wait)


def _retry_after(err) -> float | None:
    try:
        meta = err.response.json().get("error", {}).get("metadata", {})
        value = (
            meta.get("retry_after_seconds")
            or meta.get("headers", {}).get("Retry-After")
        )
        return float(value) if value is not None else None
    except Exception:
         return None