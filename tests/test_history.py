"""Unit tests for history module."""

import json
from pathlib import Path

import pytest

from llm_shell import history as hist


def test_append_and_load(tmp_path, monkeypatch):
    monkeypatch.setattr(hist, "HISTORY_PATH", tmp_path / "history.jsonl")
    hist.append("list files", "ls -la", "bash", executed=False)
    hist.append("show disk usage", "df -h", "bash", executed=True)

    entries = hist.load(10)
    assert len(entries) == 2
    assert entries[0]["task"] == "list files"
    assert entries[1]["executed"] is True


def test_load_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(hist, "HISTORY_PATH", tmp_path / "nonexistent.jsonl")
    assert hist.load() == []


def test_load_respects_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(hist, "HISTORY_PATH", tmp_path / "history.jsonl")
    for i in range(10):
        hist.append(f"task {i}", f"cmd {i}", "bash")
    assert len(hist.load(3)) == 3
