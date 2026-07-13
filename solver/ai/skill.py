#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `euler-solve` command: run Claude Code in-shell against a problem's solution files."""
from __future__ import annotations

__all__ = ['euler_solve']

import json
import shlex
import subprocess
from typing import Any, Callable, Literal

from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.shell import console, register
from solver.shell.command import Context


@register(requires=('ai:execute',), help_text='Launch the Claude Euler Solver skill.', pass_ctx=True)
def euler_solve(
        ctx: Context,
        problem: Problem,
        action: Literal['solve', 'review'],
        additional_prompt: str = '',
) -> int:
    """Run Claude Code over a problem's solution files via the claude-euler-solver skill.

    Launches Claude Code headless against the given problem's solution directory,
    runs the requested action, and streams a
    live-updating Markdown summary back into the shell, ending with a footer of
    turns / duration / cost. Heavier and slower than `claude-api` — it actually
    runs `solver` commands, edits files, evaluates, and iterates. Needs the
    `claude` CLI on PATH and an `ANTHROPIC_API_KEY` (over the web tier both are
    provided by the deploy: the CLI from `/opt/euler`, the key via the `euler-ai`
    broker — DD-15).

    Args:
        problem:            The `problem` to work on; defaults to the current problem.
        action:             What to do — 'solve' (write and verify a Python
                            solution, translate it to C, then document and
                            summarise), or 'review' (audit an existing solution
                            for C↔Python parity, in-source docs, and notes.html).
        additional_prompt:  Extra free-text instructions appended to the skill
                            invocation. Defaults to empty.
    """
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
        cost: float | None
        if (cost := meta.get('total_cost_usd')) is not None:
            cost_eur = cost / config.ecb_usd_rate
            bits.append(f'${cost:.4f}')
            bits.append(f'€{cost_eur:.4f}')
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
