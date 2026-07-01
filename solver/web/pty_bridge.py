#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""PTY bridge: run an interactive `solver` shell on a pseudo-terminal.

`PtySession` forks `python -m solver` onto a PTY so the child sees a real
terminal (`sys.stdin.isatty()` is true), and therefore runs the full
prompt-toolkit interactive loop — completion, multi-line `{ … }` blocks, rich
colours, and the interactive subshells (`! sh`/`! py`/`! claude`) — rather than
the non-interactive piped fallback.

The parent keeps the PTY master file descriptor: read it for the shell's output,
write to it for keystrokes, ioctl it to propagate the browser terminal's size.
The child is a plain `solver` shell operating on the shared solution tree, exactly
like a terminal session started at the command line.
"""
from __future__ import annotations

__all__ = ['PtySession']

import fcntl
import os
import pty
import signal
import struct
import sys
import termios

#: How many bytes to pull off the master fd per read.
_READ_CHUNK: int = 65536


class PtySession:
    """An interactive `solver` shell running on a pseudo-terminal.

    On construction the process is forked: the child execs `python -m solver`
    with a TERM that enables colour; the parent retains `pid` and the PTY master
    `fd`. The caller drives I/O — `read()`/`write()` move bytes, `resize()`
    propagates the browser terminal geometry, `close()` terminates the child.
    """

    def __init__(self, save: bool) -> None:
        pid, fd = pty.fork()
        if pid == 0:  # pragma: no cover — child process, replaced by execvp
            # A colour-capable TERM so prompt-toolkit/rich render styled output.
            os.environ['TERM'] = 'xterm-256color'
            argv = [sys.executable, '-m', 'solver'] + (['--save'] if save else [])
            os.execvp(sys.executable, argv)
            os._exit(127)  # only reached if execvp fails
        self.pid: int = pid
        self.fd: int = fd

    def read(self) -> bytes:
        """Read available output from the shell; b'' signals the child has exited.

        A PTY master raises OSError/EIO once the slave side is gone (the child
        exited); that is reported as end-of-stream rather than an error.
        """
        try:
            return os.read(self.fd, _READ_CHUNK)
        except OSError:
            return b''

    def write(self, data: bytes) -> None:
        """Forward keystrokes (raw bytes from the browser terminal) to the shell."""
        os.write(self.fd, data)

    def resize(self, cols: int, rows: int) -> None:
        """Set the PTY window size so the shell re-renders at the browser's geometry."""
        winsize = struct.pack('HHHH', rows, cols, 0, 0)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    def is_alive(self) -> bool:
        """True while the child shell process is still running."""
        try:
            pid, _ = os.waitpid(self.pid, os.WNOHANG)
        except ChildProcessError:
            return False
        return pid == 0

    def close(self) -> None:
        """Terminate the shell and release the master fd (idempotent)."""
        try:
            os.kill(self.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            pass
        try:
            os.close(self.fd)
        except OSError:
            pass
