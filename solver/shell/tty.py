#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Terminal I/O: the shared rich console, the prompt-toolkit session, and the command-block reader.

Reads one **command block** at a time, spanning multiple input lines while the
text is incomplete (unbalanced braces, an open quote, a dangling `&&`/`||`, or a
`loop` header without a body — all decided by `lexer.is_complete`).

* `make_session` builds an interactive prompt-toolkit `PromptSession` with
  history, auto-suggest, completion, and `{ … }`-aware multi-line editing.
* `read_blocks` is a plain `input()`-based fallback for non-interactive use
  (pipes, tests) where prompt-toolkit has no terminal.
"""
from __future__ import annotations

__all__ = ['console', 'make_session', 'read_blocks', 'trim_history']

import os
from pathlib import Path
from typing import Any, Callable, Generator

from prompt_toolkit import PromptSession
from prompt_toolkit.application import get_app
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from rich.console import Console

from solver.config import config
from solver.shell.lexer import is_complete

#: Shared console instance; importable by command modules.
console: Console = Console(theme=config.theme, highlight=False)


def _buffer_incomplete() -> bool:
    """True while the current prompt buffer is an unfinished block (stay multi-line)."""
    try:
        return not is_complete(get_app().current_buffer.text)
    except Exception:  # noqa: BLE001 — outside an app context
        return False


def _continuation(width: int, line_number: int, wrap_count: int) -> FormattedText:
    """Continuation prompt, indented by the open-brace depth at this line."""
    try:
        prior = get_app().current_buffer.text.split('\n')[:line_number]
        depth = max(sum(ln.count('{') - ln.count('}') for ln in prior), 0)
    except Exception:  # noqa: BLE001
        depth = 0
    return FormattedText([
        ('class:prompt.bar', '▎'),
        ('class:prompt.symbol', ' · '),
        ('class:prompt.continuation', '  ' * depth),
    ])


def _keybindings() -> KeyBindings:
    """Extra key bindings layered on prompt-toolkit's defaults."""
    kb = KeyBindings()

    @kb.add('c-l')
    def _(event: KeyPressEvent) -> None:
        event.app.renderer.clear()

    return kb


def make_session(*, history_file: Path, completer: Completer, style: Any,
                 bottom_toolbar: Callable[[], Any]) -> PromptSession:
    """Build an interactive prompt-toolkit session that returns one block per call."""
    return PromptSession(
        history=FileHistory(str(history_file)),
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
        complete_while_typing=True,
        key_bindings=_keybindings(),
        style=style,
        bottom_toolbar=bottom_toolbar,
        multiline=Condition(_buffer_incomplete),
        prompt_continuation=_continuation,
    )


def trim_history(history_file: Path, max_entries: int = 5000) -> None:
    """Deduplicate the FileHistory file and cap it at *max_entries* entries.

    Keeps the most recent occurrence of each unique command and at most the
    newest *max_entries* unique entries. Safe to call when the file is missing
    or unreadable.
    """
    if not history_file.exists():
        return
    try:
        raw = history_file.read_text(encoding='utf-8')
    except OSError:
        return
    entries: list[tuple[str, str]] = []
    current_ts: str | None = None
    current_lines: list[str] = []
    for line in raw.splitlines():
        if line.startswith('# '):
            if current_ts is not None and current_lines:
                entries.append((current_ts, '\n'.join(current_lines)))
            current_ts = line
            current_lines = []
        elif line.startswith('+'):
            current_lines.append(line[1:])
    if current_ts is not None and current_lines:
        entries.append((current_ts, '\n'.join(current_lines)))
    seen: set[str] = set()
    kept: list[tuple[str, str]] = []
    for ts, text in reversed(entries):
        if text in seen:
            continue
        seen.add(text)
        kept.append((ts, text))
        if len(kept) >= max_entries:
            break
    kept.reverse()
    tmp = history_file.with_suffix(history_file.suffix + '.tmp')
    try:
        with tmp.open('w', encoding='utf-8') as f:
            for ts, text in kept:
                f.write(f'\n{ts}\n')
                for line in text.split('\n'):
                    f.write(f'+{line}\n')
        os.replace(tmp, history_file)
    except OSError:
        try:
            tmp.unlink()
        except OSError:
            pass


def read_blocks(prompt: str = '>>> ', continuation: str = '... ') -> Generator[str, None, None]:
    """Yield command blocks read from stdin via `input()` (non-interactive fallback).

    Blank entries are skipped; `Ctrl-C` discards the partial block; `Ctrl-D`
    (EOF) ends the stream.
    """
    buffer = ''
    while True:
        try:
            line = input(prompt if not buffer else continuation)
        except EOFError:
            if buffer.strip():
                yield buffer
            return
        except KeyboardInterrupt:
            buffer = ''
            print('^C')
            continue
        buffer += line + '\n'
        if is_complete(buffer):
            block, buffer = buffer, ''
            if block.strip():
                yield block
