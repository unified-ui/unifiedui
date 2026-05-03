"""Microsoft Foundry helper for Copilot prompt-iteration (REQ 007).

Lets Copilot send prompts to the Foundry project's deployed models using the
project API key (no AAD login required) via the OpenAI v1 `/responses` endpoint.

What this CAN do:
- Send prompts and read replies (single-turn or multi-turn)
- Iterate on system instructions before they are baked into a real Foundry agent
- Smoke-test that a model deployment is reachable

What this CAN'T do:
- Create / list / delete Foundry **agents** (that needs AAD identity in the
  correct tenant + Azure AI Developer role). Use the Foundry portal or
  `az login` + the foundry MCP tools for that.

Naming convention: when Copilot is asked to create a real Foundry agent for
debugging, it MUST prefix the agent name with `co-debug-` so the user can bulk
delete them later.

Usage:
    cd unifiedui/scripts/debug
    # FOUNDRY_PROJECT_* env vars must already be exported (e.g. via platform-service .env)
    uv run --with httpx python -i foundry_smoke.py

REPL:
    >>> ping("gpt-4.1")
    >>> ask("gpt-4.1", "Summarise REQ 007 in one sentence.", system="You are terse.")
    >>> chat("gpt-4.1", [{"role": "user", "content": "hi"}])
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

API_KEY = os.environ.get("FOUNDRY_PROJECT_API_KEY", "")
OPENAI_ENDPOINT = os.environ.get("FOUNDRY_PROJECT_OPENAI_ENDPOINT", "")
PROJECT_ENDPOINT = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "")
DEFAULT_MODEL = os.environ.get("FOUNDRY_DEFAULT_MODEL", "gpt-4.1")


def _require_creds() -> None:
    """Raise a friendly error if env vars are missing."""
    missing = [
        n
        for n in ("FOUNDRY_PROJECT_API_KEY", "FOUNDRY_PROJECT_OPENAI_ENDPOINT")
        if not os.environ.get(n)
    ]
    if missing:
        raise RuntimeError(
            f"Missing env vars: {', '.join(missing)}. "
            "Source platform-service .env first."
        )


def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST JSON to an OpenAI v1 endpoint with the api-key header."""
    import httpx  # type: ignore[import-not-found]

    _require_creds()
    url = f"{OPENAI_ENDPOINT.rstrip('/')}/{path.lstrip('/')}"
    resp = httpx.post(
        url,
        headers={"api-key": API_KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if resp.status_code >= 400:
        print(f"[foundry] {resp.status_code} {resp.text[:600]}", file=sys.stderr)
    resp.raise_for_status()
    return resp.json()


def ask(model: str, user: str, system: str | None = None) -> str:
    """Single-turn ask. Returns the text response."""
    payload: dict[str, Any] = {"model": model, "input": user}
    if system:
        payload["instructions"] = system
    data = _post("responses", payload)
    parts: list[str] = []
    for out in data.get("output", []):
        for c in out.get("content", []):
            if c.get("type") == "output_text":
                parts.append(c.get("text", ""))
    return "\n".join(parts)


def chat(model: str, messages: list[dict[str, str]]) -> str:
    """Multi-turn chat via /chat/completions."""
    data = _post("chat/completions", {"model": model, "messages": messages})
    return data["choices"][0]["message"]["content"]


def ping(model: str = DEFAULT_MODEL) -> bool:
    """Smoke-test a deployment by asking it to reply PONG."""
    try:
        reply = ask(model, "Reply with exactly: PONG")
        ok = "PONG" in reply.upper()
        print(f"[foundry] {model}: {reply!r} -> {'OK' if ok else 'UNEXPECTED'}")
        return ok
    except Exception as e:
        print(f"[foundry] {model}: FAILED {e}", file=sys.stderr)
        return False


def list_models() -> list[str]:
    """List model IDs the project's API key can see (catalog, not deployments)."""
    import httpx  # type: ignore[import-not-found]

    _require_creds()
    url = f"{OPENAI_ENDPOINT.rstrip('/')}/models"
    resp = httpx.get(url, headers={"api-key": API_KEY}, timeout=30)
    resp.raise_for_status()
    return sorted({m["id"] for m in resp.json().get("data", [])})


def main() -> None:
    """Print connection info and run a quick ping."""
    if not API_KEY or not OPENAI_ENDPOINT:
        print("[foundry] !! FOUNDRY_PROJECT_API_KEY / FOUNDRY_PROJECT_OPENAI_ENDPOINT not set", file=sys.stderr)
        return
    print(f"[foundry] OpenAI endpoint = {OPENAI_ENDPOINT}")
    print(f"[foundry] Project endpoint = {PROJECT_ENDPOINT or '<not set>'}")
    print(f"[foundry] Default model = {DEFAULT_MODEL}")
    print("[foundry] Ready. Try: ping(); ask('gpt-4.1', 'hi')")


main()
