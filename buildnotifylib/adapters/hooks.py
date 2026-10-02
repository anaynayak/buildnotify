import os
import re
import shlex
import subprocess

PLACEHOLDER_TOKENS = re.compile(r"#status#|#projects#|.", re.DOTALL)


class ShellScriptHook:
    def run(self, script: str, status: str, projects: str) -> None:
        command = substitute_placeholders(script, {"#status#": status, "#projects#": projects})
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
