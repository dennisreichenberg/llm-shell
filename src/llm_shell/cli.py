"""CLI entry point for llm-shell."""

from __future__ import annotations

import sys

import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.text import Text

from . import history as hist
from .ollama import OLLAMA_DEFAULT_URL, explain_command, list_models, suggest_command
from .shell import detect_shell, run_command

console = Console()
err = Console(stderr=True)


@click.group(invoke_without_command=True)
@click.pass_context
@click.argument("task", required=False)
@click.option("--model", "-m", default="mistral", show_default=True, help="Ollama model to use.")
@click.option("--host", default=OLLAMA_DEFAULT_URL, show_default=True, help="Ollama base URL.")
@click.option("--shell", "shell_override", default=None, help="Override shell detection.")
@click.option("--run", "-r", "do_run", is_flag=True, help="Execute the suggested command after confirmation.")
@click.option("--copy", "-c", "do_copy", is_flag=True, help="Copy command to clipboard.")
def main(
    ctx: click.Context,
    task: str | None,
    model: str,
    host: str,
    shell_override: str | None,
    do_run: bool,
    do_copy: bool,
) -> None:
    """Suggest a shell command for TASK using a local Ollama model.

    \b
    Examples:
      llm-shell "list all docker containers using more than 1GB of memory"
      llm-shell "find all .py files modified in the last 7 days" --run
      llm-shell "compress this directory to a tar.gz" --copy
    """
    if ctx.invoked_subcommand is not None:
        return

    if not task:
        click.echo(ctx.get_help())
        sys.exit(0)

    shell = shell_override or detect_shell()
    console.print(f"[dim]Shell:[/dim] [cyan]{shell}[/cyan]  [dim]Model:[/dim] [cyan]{model}[/cyan]\n")

    try:
        with console.status("[bold green]Thinking…"):
            command = suggest_command(task, shell, model=model, base_url=host)
    except httpx.ConnectError:
        err.print(f"[red]Cannot connect to Ollama at {host}.[/red] Is Ollama running?")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        err.print(f"[red]Ollama API error {e.response.status_code}:[/red] {e.response.text[:200]}")
        sys.exit(1)

    syntax = Syntax(command, "bash", theme="monokai", word_wrap=True)
    console.print(Panel(syntax, title="Suggested command", border_style="green"))

    executed = False

    if do_copy:
        try:
            import pyperclip
            pyperclip.copy(command)
            console.print("[dim]Copied to clipboard.[/dim]")
        except Exception as exc:
            err.print(f"[yellow]Could not copy to clipboard:[/yellow] {exc}")

    if do_run:
        if Confirm.ask("\nExecute this command?", default=False):
            console.print()
            returncode, stdout, stderr = run_command(command, shell)
            if stdout:
                console.print(stdout.rstrip())
            if stderr:
                err.print(stderr.rstrip())
            executed = True
            if returncode != 0:
                err.print(f"[red]Command exited with code {returncode}.[/red]")
                sys.exit(returncode)

    hist.append(task, command, shell, executed=executed)


@main.command("explain")
@click.argument("command")
@click.option("--model", "-m", default="mistral", show_default=True, help="Ollama model to use.")
@click.option("--host", default=OLLAMA_DEFAULT_URL, show_default=True, help="Ollama base URL.")
def explain_cmd(command: str, model: str, host: str) -> None:
    """Explain what COMMAND does in plain language."""
    try:
        with console.status("[bold green]Explaining…"):
            explanation = explain_command(command, model=model, base_url=host)
    except httpx.ConnectError:
        err.print(f"[red]Cannot connect to Ollama at {host}.[/red]")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        err.print(f"[red]Ollama API error {e.response.status_code}:[/red] {e.response.text[:200]}")
        sys.exit(1)

    console.print(Panel(Text(explanation), title="Explanation", border_style="cyan"))


@main.command("history")
@click.option("--n", default=20, show_default=True, help="Number of recent entries to show.")
def history_cmd(n: int) -> None:
    """Show recent command history."""
    entries = hist.load(n)
    if not entries:
        console.print("[yellow]No history yet.[/yellow]")
        return

    console.print(f"[bold]Last {len(entries)} entries:[/bold]\n")
    for entry in entries:
        ts = entry.get("ts", "")[:19].replace("T", " ")
        shell = entry.get("shell", "?")
        task = entry.get("task", "")
        command = entry.get("command", "")
        executed = "[green]✓[/green]" if entry.get("executed") else "[dim]–[/dim]"
        console.print(f"[dim]{ts}[/dim] [{shell}] {executed} [bold]{task}[/bold]")
        console.print(f"  [cyan]{command}[/cyan]\n")


@main.command("models")
@click.option("--host", default=OLLAMA_DEFAULT_URL, show_default=True, help="Ollama base URL.")
def models_cmd(host: str) -> None:
    """List available Ollama models."""
    try:
        available = list_models(host)
    except httpx.ConnectError:
        err.print(f"[red]Cannot connect to Ollama at {host}.[/red]")
        sys.exit(1)

    if not available:
        console.print("[yellow]No models found.[/yellow] Pull one with: ollama pull mistral")
        return

    console.print("[bold]Available Ollama models:[/bold]")
    for m in available:
        console.print(f"  [cyan]{m}[/cyan]")
