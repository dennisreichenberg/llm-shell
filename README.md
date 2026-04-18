# llm-shell

AI-powered shell command suggester. Describe what you want to do in plain text — `llm-shell` returns the exact shell command via a local [Ollama](https://ollama.ai) model.

## Install

```bash
cd llm-shell && pip install -e .
```

Requires Ollama running locally (`ollama serve`).

## Usage

```bash
# Suggest a command
llm-shell "list all docker containers using more than 1GB of memory"

# Suggest and execute after confirmation
llm-shell "find all .py files modified in the last 7 days" --run

# Copy the suggested command to clipboard
llm-shell "compress this directory to a tar.gz" --copy

# Explain what a command does
llm-shell explain "awk '{sum+=$1} END {print sum}' numbers.txt"

# Show recent history
llm-shell history

# List available models
llm-shell models

# Use a different model
llm-shell "restart nginx" --model llama3

# Override shell detection
llm-shell "list files by size" --shell fish
```

## Shell detection

`llm-shell` automatically detects your current shell (`bash`, `zsh`, `fish`, `powershell`, `cmd`) from the `$SHELL` environment variable and generates syntax appropriate for it.

## History

All suggestions are stored at `~/.local/share/llm-shell/history.jsonl`. Each entry records the timestamp, shell, task description, suggested command, and whether it was executed.

## Options

| Option | Description |
|--------|-------------|
| `--model`, `-m` | Ollama model to use (default: `mistral`) |
| `--host` | Ollama base URL (default: `http://localhost:11434`) |
| `--shell` | Override shell detection |
| `--run`, `-r` | Execute after confirmation |
| `--copy`, `-c` | Copy to clipboard |
