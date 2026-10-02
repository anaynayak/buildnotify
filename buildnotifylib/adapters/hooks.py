import logging
import os
import re
import shlex
import subprocess
import sys

PLACEHOLDERS = ("#status#", "#projects#")
PLACEHOLDER_TOKENS = re.compile(r"#status#|#projects#|.", re.DOTALL)
WINDOWS_PLACEHOLDERS = (
    "Not running the custom script: #status# and #projects# can't be quoted safely for cmd.exe. "
    "Read the BUILDNOTIFY_STATUS and BUILDNOTIFY_PROJECTS environment variables in the script instead."
)

log = logging.getLogger(__name__)


class ShellScriptHook:
    """Run the custom script through the platform shell.

    The status and projects always reach the script as BUILDNOTIFY_STATUS and BUILDNOTIFY_PROJECTS.
    The legacy #status#/#projects# placeholders are POSIX-shell only: cmd.exe has no quoting that
    neutralises & | ^ % reliably, so on Windows a script that uses them is refused, not run.
    """

    def __init__(self, windows: bool | None = None):
        self.windows = sys.platform == "win32" if windows is None else windows

    def run(self, script: str, status: str, projects: str) -> None:
        if self.windows and any(placeholder in script for placeholder in PLACEHOLDERS):
            log.warning(WINDOWS_PLACEHOLDERS)
            return
        values = {"#status#": status, "#projects#": projects}
        command = script if self.windows else substitute_placeholders(script, values)
        env = dict(os.environ, BUILDNOTIFY_STATUS=status, BUILDNOTIFY_PROJECTS=projects)
        subprocess.Popen(command, shell=True, env=env)


def substitute_placeholders(script: str, values: dict[str, str]) -> str:
    parts, quote, escaped = [], "", False
    for token in PLACEHOLDER_TOKENS.findall(script):
        replace = token in values and not escaped
        quote, escaped = next_shell_state(token, quote, escaped)
        parts.append(quote + shlex.quote(values[token]) + quote if replace else token)
    return "".join(parts)


def next_shell_state(token: str, quote: str, escaped: bool) -> tuple[str, bool]:
    if escaped or len(token) > 1:
        return quote, False
    if token == "\\" and quote != "'":
        return quote, True
    if token in ('"', "'") and quote in ("", token):
        return ("" if quote else token), False
    return quote, False
