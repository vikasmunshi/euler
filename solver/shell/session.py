#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Session capture: tee shell output and typed input to a plain-text log file.

Exporting via :meth:`rich.console.Console.export_text` only sees output produced
through `console.print` — it misses anything written to `sys.stderr` and any
subprocess that inherits the terminal's file descriptors. Instead, this module
installs a tee on `sys.stdout` / `sys.stderr` for the duration of each command,
plus direct recording of the typed prompt lines (which prompt-toolkit draws
outside the captured streams).

The shell opens a :class:`SessionLog` for the session when `--save` is set,
records each entered block with :meth:`SessionLog.record_command`, and wraps
every dispatch in :meth:`SessionLog.capture`.
"""
from __future__ import annotations

__all__ = ['SessionLog']

import re
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, TextIO

#: Matches a complete ANSI escape sequence (CSI / OSC / two-char escapes).
_ANSI_RE = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|][^\x07\x1b]*(?:\x07|\x1b\\))')
#: Matches a *trailing* escape sequence that has not yet been terminated, so it
#: can be held back across writes rather than logged half-stripped.
_TRAILING_ESC_RE = re.compile(r'\x1b\[?[0-?]*[ -/]*$')


class _TeeStream:
    """A `sys.stdout` / `sys.stderr` replacement that also writes to a log.

    Everything a command emits — Rich output, bare :func:`print` calls, and
    subprocess output routed through these streams — is forwarded verbatim to
    the real terminal *and* (with ANSI styling stripped) to the session log.

    The terminal copy is untouched, so colours and width detection keep working
    (`isatty` / `fileno` / `encoding` proxy through to the wrapped stream). Only
    the logged copy is stripped, giving a clean, plain-text transcript.

    Deliberately a plain duck-typed file object rather than an
    :class:`io.TextIOBase` subclass, whose `encoding` / `errors` are read-only
    and cannot mirror the wrapped stream.
    """

    def __init__(self, stream: TextIO, log: TextIO) -> None:
        self._stream = stream
        self._log = log
        self._carry = ''  # incomplete trailing escape held over to the next write
        self._paused = False  # while True, forward to the terminal but not the log
        self.encoding: str = getattr(stream, 'encoding', 'utf-8')
        self.errors: str | None = getattr(stream, 'errors', None)

    # -- writing -----------------------------------------------------------

    def write(self, s: str) -> int:
        n = self._stream.write(s)
        if self._paused:  # terminal copy only — keep this output out of the log
            return n
        data = self._carry + s
        self._carry = ''
        match = _TRAILING_ESC_RE.search(data)
        if match and match.group():
            self._carry = data[match.start():]
            data = data[:match.start()]
        try:
            self._log.write(_ANSI_RE.sub('', data))
        except (OSError, ValueError):  # log closed underneath us — ignore
            pass
        return n

    def flush(self) -> None:
        try:
            self._stream.flush()
        except (OSError, ValueError):
            pass
        if self._paused:
            return
        try:
            if self._carry:
                self._log.write(_ANSI_RE.sub('', self._carry))
                self._carry = ''
            self._log.flush()
        except (OSError, ValueError):
            pass

    # -- capability passthrough -------------------------------------------

    def isatty(self) -> bool:
        return self._stream.isatty()

    def fileno(self) -> int:
        return self._stream.fileno()

    def writable(self) -> bool:
        return True

    def __getattr__(self, name: str) -> Any:
        # Delegate anything we don't override (closed, writelines, …) to the
        # wrapped stream so the tee is a faithful stand-in.
        return getattr(self._stream, name)


class SessionLog:
    """Captures an interactive shell session to a plain-text log file.

    Construct one to begin logging; call :meth:`close` to finish. The shell
    wraps each command dispatch in :meth:`capture` (teeing the real streams) and
    records every entered block with :meth:`record_command`.
    """

    def __init__(self, path: Path) -> None:
        self._file: TextIO = open(path, 'w', encoding='utf-8')
        self._capturing = False
        self._tees: list[_TeeStream] = []  # the tees installed by the active capture

    @contextmanager
    def capture(self) -> Iterator[None]:
        """Tee `sys.stdout` / `sys.stderr` into the log for one dispatch.

        Active only while a command runs — the interactive prompt keeps the real
        streams so prompt-toolkit's redraws never reach the log. Reentrant
        invocations are a no-op: the outermost capture already covers them.
        """
        if self._capturing:
            yield
            return
        real_out, real_err = sys.stdout, sys.stderr
        self._capturing = True
        self._tees = [_TeeStream(real_out, self._file), _TeeStream(real_err, self._file)]
        sys.stdout, sys.stderr = self._tees
        try:
            yield
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout, sys.stderr = real_out, real_err
            self._tees = []
            self._capturing = False

    @contextmanager
    def pause(self) -> Iterator[None]:
        """Suspend *log* writes while keeping terminal output flowing.

        The active tees keep forwarding to the real terminal but stop copying to
        the log file for the duration — used to keep a high-frequency
        :class:`rich.live.Live` region's redraws out of the transcript while
        still showing them live. A no-op when no capture is active; only the tees
        this call paused are resumed, so it nests safely.
        """
        paused = [tee for tee in self._tees if not tee._paused]
        for tee in paused:
            tee._paused = True
        try:
            yield
        finally:
            for tee in paused:
                tee._paused = False

    def record_command(self, label: str, block: str) -> None:
        """Append an entered block to the log, right before its captured output.

        prompt-toolkit draws the prompt outside the captured streams, so the
        block would otherwise be missing from the transcript. Multi-line blocks
        are written with the prompt on the first line and a continuation marker
        on the rest, mirroring what the user saw at the prompt.
        """
        first, *rest = block.splitlines() or ['']
        self._file.write(f'▎ {label} ❯ {first}\n')
        for line in rest:
            self._file.write(f'▎ · {line}\n')
        self._file.flush()

    def close(self) -> None:
        """Flush and close the log file."""
        self._file.close()
