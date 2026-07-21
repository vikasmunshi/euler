#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `claude-solve` / `claude-blog` commands: run Claude Code in-shell via a skill."""
from __future__ import annotations

__all__ = ['claude_solve', 'claude_blog']

import json
import shlex
import subprocess
from typing import Any, Callable, Iterable, Literal

from prompt_toolkit.completion import Completion
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.shell import console, register
from solver.shell.command import Context


@register(requires='contributor', help_text='Launch the Claude Euler Solver skill.', pass_ctx=True)
def claude_solve(
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
    `claude` CLI on PATH and an `ANTHROPIC_API_KEY`.

    Args:
        problem:            The `problem` to work on; defaults to the current problem.
        action:             What to do — 'solve' (write and verify a Python
                            solution, translate it to C, then document and
                            summarise), or 'review' (audit an existing solution
                            for C↔Python parity, in-source docs, and notes.html).
        additional_prompt:  Extra free-text instructions appended to the skill
                            invocation. Defaults to empty.
    """
    invocation = f'/claude-euler-solver {problem.number} {action} {additional_prompt}'.strip()
    return _run_skill(ctx, invocation, f'[accent]claude · {action}[/accent]')


def _topic_completions(_ctx: Context, incomplete: str) -> Iterable[str | Completion]:
    """`claude-blog` targets: every tag as its ``<facet>/<slug>`` topic path, **most-referenced
    first**, each shown with its facet and distinct-problem count."""
    try:
        central = json.loads(config.central_tags_file.read_text())
    except (OSError, json.JSONDecodeError):
        return []

    def refs(tag: dict[str, Any]) -> int:
        return len({r.split('_')[0] for r in tag.get('refs', [])})

    out: list[str | Completion] = []
    for tag in sorted(central.get('tags', []), key=lambda t: (-refs(t), t['slug'])):
        path = f"{tag['facet']}/{tag['slug']}"
        if path.startswith(incomplete) or incomplete in tag['slug']:
            out.append(Completion(path, start_position=-len(incomplete),
                                  display=tag['slug'], display_meta=f"{tag['facet']} · {refs(tag)}"))
    return out


@register(requires='maintainer', pass_ctx=True, completers={'topic': _topic_completions},
          help_text='Launch the Claude Euler Blogger skill to write a topic article for a tag/topic.')
def claude_blog(ctx: Context, topic: str, additional_prompt: str = '') -> int:
    """Write (or flesh out) a topic article via the claude-euler-blogger skill.

    *topic* names what to write about: a tag's ``<facet>/<slug>`` path (e.g.
    ``technique/sieve-of-eratosthenes``), a bare tag slug, or a curated topic path
    (``number-theory/primes``). Tab-completion offers the tags, most-referenced first.
    Launches Claude Code headless to research the covering problems and write the article
    under ``topics/``, then streams a live Markdown summary. Needs the `claude` CLI and an
    `ANTHROPIC_API_KEY`.

    Args:
        topic:              The tag or topic to write about (completed most-referenced first).
        additional_prompt:  Extra free-text guidance for the writer. Defaults to empty.
    """
    invocation = f'/claude-euler-blogger {topic} {additional_prompt}'.strip()
    return _run_skill(ctx, invocation, '[accent]claude · blog[/accent]')


def _run_skill(ctx: Context, invocation: str, title: str) -> int:
    """Run ``claude -p <invocation>`` headless, stream its output into a transient live panel,
    then print the final Markdown result with a turns / duration / cost footer."""
    cmdline = ('claude -p --output-format stream-json --verbose '
               f'--include-partial-messages {shlex.quote(invocation)}').strip()
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
