#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `claude-skill` command: run Claude Code in-shell against the locked workspace."""
from __future__ import annotations

__all__ = ['claude_skill']

import json
import shlex
import subprocess
from typing import Any, Callable, Literal

from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from solver.config import ExitCodes, config
from solver.core.checkout import auto_checkout
from solver.core.lock import check_workspace_lock_command
from solver.shell import console, register
from solver.shell.command import Context
from solver.shell.variables import variables


@register(help_text='Launch the Claude Euler Solver skill.', pass_ctx=True)
@check_workspace_lock_command
@auto_checkout
def claude_skill(
        ctx: Context,
        action: Literal['solve', 'review'],
        additional_prompt: str = '',
) -> int:
    """Run Claude Code over the locked workspace via the claude-euler-solver skill.

    Launches Claude Code headless against the current `workspace/` (which this
    shell holds the lock for), runs the requested action, and streams a
    live-updating Markdown summary back into the shell, ending with a footer of
    turns / duration / cost. Heavier and slower than `claude-api` — it actually
    runs `solver` commands, edits files, evaluates, and iterates. Needs the
    `claude` CLI on PATH and an `ANTHROPIC_API_KEY`.

    Args:
        action:             What to do — 'solve' (write and verify a Python
                            solution, translate it to C, then document and
                            summarise), or 'review' (audit an existing solution
                            for C↔Python parity, in-source docs, and notes.html).
        additional_prompt:  Extra free-text instructions appended to the skill
                            invocation. Defaults to empty.
    """
    if (problem := variables.problem) is None:
        console.print('[error]No problem in the workspace[/error] — run [accent]init <n>[/accent] first.')
        return ExitCodes.EXIT_ERROR
    problem_number = problem.number
    cmdline = ('claude -p --output-format stream-json --verbose '
               '--include-partial-messages '
               f'{shlex.quote(f'/claude-euler-solver {problem_number} {action} {additional_prompt}')}'.strip())
    title = f'[accent]claude · {action}[/accent]'
    parts: list[str] = []  # streamed text_delta chunks
    meta: dict[str, Any] = {}  # the final `result` event payload
    noise: list[str] = []  # non-JSON lines (e.g. error output)

    def _footer() -> str | None:
        duration: int | None
        bits: list[str] = []
        if (turns := meta.get('num_turns')) is not None:
            bits.append(f'{turns} turns')
        if (duration := meta.get('duration_ms')) is not None:
            bits.append(f'{duration / 1000:.1f}s')
        if (cost := meta.get('total_cost_usd')) is not None:
            bits.append(f'${cost:.4f}')
        return f'[muted]{" · ".join(bits)}[/muted]' if bits else None

    def _panel(done: bool = False) -> Panel:
        text = str(meta['result']) if done and 'result' in meta else ''.join(parts)
        body: Any = Markdown(text) if text else Text('(no output)' if done else '…', style='muted')
        return Panel(body, border_style='panel.border', title=title, title_align='left',
                     padding=(1, 2), subtitle=_footer() if done else None, subtitle_align='right')

    def _consume(stream: Any, on_update: Callable[[], None]) -> None:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                noise.append(line)
                continue
            if msg.get('type') == 'stream_event':
                delta = msg.get('event', {}).get('delta', {})
                if delta.get('type') == 'text_delta':
                    parts.append(str(delta.get('text', '')))
                    on_update()
            elif msg.get('type') == 'result':
                meta.update(msg)

    with subprocess.Popen(cmdline, shell=True, cwd=config.root_dir, text=True, bufsize=1,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
        if proc.stdout is None:
            console.print(f'[error]no stdout[/error] {cmdline}')
            return ExitCodes.EXIT_ERROR
        # Stream into a transient live panel.  When a session log is active its
        # tee is paused for the duration, so the high-frequency redraws reach the
        # terminal but never flood the transcript — only the final panel below is
        # logged.
        with ctx.shell.pause_logging():
            with Live(_panel(), console=console, refresh_per_second=10, transient=True) as live:
                _consume(proc.stdout, lambda: live.update(_panel()))
        rc = proc.wait()
    if rc != 0:
        console.print(f'[error]claude exited {rc}[/error]')
        if noise:
            console.print(f'[warning]{"\n".join(noise).strip()}[/warning]')
        return rc
    console.print(_panel(done=True))
    return ExitCodes.EXIT_OK
