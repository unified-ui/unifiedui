"""HTTP helper for calling unified-ui endpoints via the debug backdoor (REQ 007).

Lets Copilot/scripts call any platform-service or agent-service endpoint as any
synthesised user without an OAuth flow.

Usage:
    cd unifiedui/scripts/debug
    export DEBUG_BACK_DOOR_SECRET='<the-32-char-secret-from-your-env>'
    uv run --with httpx python -i backdoor_call.py

Then in the REPL:
    me = platform.get("/identity/me")
    health = agent.get("/health")
    new_tenant = platform.post("/organizations/<ORG>/tenants", json={"name": "Debug T"})
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

DEFAULT_PLATFORM = os.environ.get("PLATFORM_BASE_URL", "http://localhost:8000/api/v1/platform-service")
DEFAULT_AGENT = os.environ.get("AGENT_BASE_URL", "http://localhost:8085/api/v1/agent-service")

SECRET = os.environ.get("DEBUG_BACK_DOOR_SECRET", "")
USER_ID = os.environ.get("DEBUG_USER_ID", "copilot-debug")
USER_UPN = os.environ.get("DEBUG_USER_UPN", "copilot-debug@example.com")
USER_NAME = os.environ.get("DEBUG_USER_NAME", "Copilot Debug")
TENANT_ID = os.environ.get("DEBUG_TENANT_ID", "")
GROUPS = os.environ.get("DEBUG_GROUPS", "")


def _headers() -> dict[str, str]:
    """Build the X-Debug-* header set."""
    if not SECRET:
        raise RuntimeError("DEBUG_BACK_DOOR_SECRET env var is required")
    h = {
        "X-Debug-Backdoor": SECRET,
        "X-Debug-User-Id": USER_ID,
        "X-Debug-User-Upn": USER_UPN,
        "X-Debug-User-Name": USER_NAME,
        "X-Use-Cache": "false",
    }
    if TENANT_ID:
        h["X-Debug-Tenant-Id"] = TENANT_ID
    if GROUPS:
        h["X-Debug-Groups"] = GROUPS
    return h


class BackdoorClient:
    """Tiny HTTP client that injects the backdoor headers on every request."""

    def __init__(self, base_url: str, label: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.label = label

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        import httpx  # type: ignore[import-not-found]

        url = self.base_url + ("/" + path.lstrip("/"))
        headers = _headers()
        headers.update(kwargs.pop("headers", {}))
        resp = httpx.request(method, url, headers=headers, timeout=30, **kwargs)
        ct = resp.headers.get("content-type", "")
        body: Any = resp.json() if "json" in ct else resp.text
        print(f"[{self.label}] {method} {path} -> {resp.status_code}")
        if resp.status_code >= 400:
            print(json.dumps(body, indent=2, default=str), file=sys.stderr)
        return body

    def get(self, path: str, **kw: Any) -> Any:
        return self._request("GET", path, **kw)

    def post(self, path: str, **kw: Any) -> Any:
        return self._request("POST", path, **kw)

    def put(self, path: str, **kw: Any) -> Any:
        return self._request("PUT", path, **kw)

    def patch(self, path: str, **kw: Any) -> Any:
        return self._request("PATCH", path, **kw)

    def delete(self, path: str, **kw: Any) -> Any:
        return self._request("DELETE", path, **kw)


platform = BackdoorClient(DEFAULT_PLATFORM, "platform")
agent = BackdoorClient(DEFAULT_AGENT, "agent")


def main() -> None:
    """Print connection info and a self-test against /healthcheck."""
    if not SECRET:
        print("[backdoor_call] !! DEBUG_BACK_DOOR_SECRET not set", file=sys.stderr)
        return
    print(f"[backdoor_call] platform = {DEFAULT_PLATFORM}")
    print(f"[backdoor_call] agent    = {DEFAULT_AGENT}")
    print(f"[backdoor_call] user     = {USER_ID} <{USER_UPN}>")
    print("[backdoor_call] try: platform.get('/healthcheck')")


main()
