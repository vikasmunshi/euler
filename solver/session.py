#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Session Capture: context manager for capturing stdout and writing to a log file. """
from __future__ import annotations

from pathlib import Path
from sys import modules as sys_modules
from types import TracebackType
from typing import Any, IO, cast
from uuid import uuid7

from solver.cli import SolverShell
from solver.config import root_dir


class SessionCapture:
    """Context-managed stdout tee: writes to both the terminal and a session log file."""
    __slots__ = ('_file', '_filename', 'original', 'sessions_dir', 'shell')
    _file: IO[str]
    _filename: str
    original: IO[str]
    sessions_dir: Path
    shell: SolverShell

    def __init__(self, shell: SolverShell | None = None) -> None:
        session_id: str = uuid7().hex
        self._filename = f'{session_id}.txt'
        self.sessions_dir = root_dir / 'sessions'
        self.shell = shell or SolverShell()
        self.shell.session_id = session_id

    def __enter__(self) -> SessionCapture:
        _sys = sys_modules['sys']
        self.sessions_dir.mkdir(exist_ok=True)
        self.original = _sys.stdout
        self._file = (root_dir / 'sessions' / self._filename).open('w')
        _sys.stdout = cast(IO[str], cast(object, self))  # type: ignore [attr-defined]
        self.shell.stdout = _sys.stdout
        return self

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc_value: BaseException | None,
                 tb: TracebackType | None) -> None:
        _sys = sys_modules['sys']
        _sys.stdout = self.original  # type: ignore [attr-defined]
        self.shell.stdout = _sys.stdout
        self._file.close()
        print(f'Session log written to sessions/{self._filename}')

    def write(self, s: str) -> int:
        self.original.write(s)
        self._file.write(s)
        return len(s)

    def flush(self) -> None:
        self.original.flush()
        self._file.flush()

    def writable(self) -> bool:
        return self.original.writable() and self._file.writable()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.original, name)


__all__ = ('SessionCapture',)
