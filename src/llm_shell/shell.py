"""Shell detection and command execution."""

from __future__ import annotations

import os
import subprocess
import sys


def detect_shell() -> str:
    """Return the name of the current shell (bash, zsh, fish, powershell, cmd)."""
    if sys.platform == "win32":
        shell_env = os.environ.get("COMSPEC", "").lower()
        if "powershell" in shell_env or os.environ.get("PSModulePath"):
            return "powershell"
        return "cmd"

    shell_path = os.environ.get("SHELL", "")
    name = os.path.basename(shell_path).lower()
    if name in ("bash", "zsh", "fish", "sh", "dash", "ksh"):
        return name
    return "bash"


def run_command(command: str, shell: str) -> tuple[int, str, str]:
    """Run *command* in the detected shell; return (returncode, stdout, stderr)."""
    if shell == "fish":
        args = ["fish", "-c", command]
    elif shell in ("powershell", "pwsh"):
        args = ["powershell", "-Command", command]
    elif shell == "cmd":
        args = ["cmd", "/c", command]
    else:
        args = [shell, "-c", command]

    result = subprocess.run(args, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr
