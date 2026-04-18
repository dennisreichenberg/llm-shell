"""Unit tests for ollama helpers (no network calls)."""

from llm_shell.ollama import _strip_fences


def test_strip_fences_removes_backtick_blocks():
    raw = "```bash\ndocker ps\n```"
    assert _strip_fences(raw) == "docker ps"


def test_strip_fences_passthrough_plain():
    raw = "docker ps"
    assert _strip_fences(raw) == "docker ps"


def test_strip_fences_multiline_command():
    raw = "```\nfind . -name '*.py' | xargs grep TODO\n```"
    result = _strip_fences(raw)
    assert "find ." in result
    assert "```" not in result
