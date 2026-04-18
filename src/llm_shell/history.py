"""History management — stores suggestions at ~/.local/share/llm-shell/history.jsonl."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

HISTORY_PATH = Path.home() / ".local" / "share" / "llm-shell" / "history.jsonl"


def append(task: str, command: str, shell: str, executed: bool = False) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "shell": shell,
        "task": task,
        "command": command,
        "executed": executed,
    }
    with HISTORY_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def load(n: int = 20) -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    lines = HISTORY_PATH.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries[-n:]
