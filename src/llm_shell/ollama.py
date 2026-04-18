"""Ollama API client for llm-shell."""

from __future__ import annotations

import httpx

OLLAMA_DEFAULT_URL = "http://localhost:11434"

_SUGGEST_SYSTEM = """\
You are a shell command expert. The user describes what they want to do in plain English.
Return ONLY the shell command — no explanation, no markdown, no backticks, no prose.
One command per response. If multiple commands are needed, join them with && or pipe them.
Generate syntax appropriate for the shell specified by the user.\
"""

_EXPLAIN_SYSTEM = """\
You are a shell command expert. Explain what the given shell command does.
Be concise (3-5 sentences). Use plain language. No markdown headers.\
"""


def suggest_command(
    task: str,
    shell: str,
    *,
    model: str = "mistral",
    base_url: str = OLLAMA_DEFAULT_URL,
    timeout: float = 60.0,
) -> str:
    prompt = f"Shell: {shell}\nTask: {task}"
    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        response = client.post(
            "/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": _SUGGEST_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "options": {"temperature": 0.2},
            },
        )
        response.raise_for_status()
        content = response.json()["message"]["content"].strip()
        return _strip_fences(content)


def explain_command(
    command: str,
    *,
    model: str = "mistral",
    base_url: str = OLLAMA_DEFAULT_URL,
    timeout: float = 60.0,
) -> str:
    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        response = client.post(
            "/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": _EXPLAIN_SYSTEM},
                    {"role": "user", "content": f"Command: {command}"},
                ],
                "stream": False,
                "options": {"temperature": 0.3},
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()


def list_models(base_url: str = OLLAMA_DEFAULT_URL) -> list[str]:
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        response = client.get("/api/tags")
        response.raise_for_status()
        return [m["name"] for m in response.json().get("models", [])]


def _strip_fences(text: str) -> str:
    if text.startswith("```"):
        lines = [l for l in text.splitlines() if not l.startswith("```")]
        return "\n".join(lines).strip()
    return text
