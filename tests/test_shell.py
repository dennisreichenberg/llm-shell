"""Unit tests for shell detection."""

import sys
from unittest.mock import patch

from llm_shell.shell import detect_shell


def test_detect_shell_uses_env(monkeypatch):
    if sys.platform != "win32":
        monkeypatch.setenv("SHELL", "/usr/bin/zsh")
        assert detect_shell() == "zsh"


def test_detect_shell_fish(monkeypatch):
    if sys.platform != "win32":
        monkeypatch.setenv("SHELL", "/usr/bin/fish")
        assert detect_shell() == "fish"


def test_detect_shell_fallback(monkeypatch):
    if sys.platform != "win32":
        monkeypatch.setenv("SHELL", "/usr/bin/unknown-shell")
        assert detect_shell() == "unknown-shell"
