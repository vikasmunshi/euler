#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""PTY bridge: run an interactive ``solver`` shell on a pseudo-terminal (DD-13).

``PtySession`` starts the shell on a PTY so the child sees a real terminal
(``sys.stdin.isatty()`` is true) and runs the full prompt-toolkit interactive
loop — completion, multi-line ``{ … }`` blocks, rich colours — rather than the
non-interactive piped fallback.

The child is spawned with ``pty.openpty()`` + ``subprocess.Popen`` — **not**
``pty.fork()``: the service's event loop runs executor threads (the PTY
drainers), and forking a threaded process to run Python before exec is
deadlock-prone (and a ``DeprecationWarning`` since 3.12). Popen's C-level
fork+exec is async-signal-safe; a tiny ``-c`` bootstrap then runs *after* exec
to make the slave the **controlling terminal** (``setsid`` + ``TIOCSCTTY``, what
``pty.fork`` would have done) so the line discipline delivers Ctrl-C as SIGINT.

The parent keeps the PTY master file descriptor: read it for the shell's
output, write to it for keystrokes, ioctl it to propagate the browser
terminal's size.

Identity transfers by the **one-time shell ticket** (DD-9), never the
environment as a credential: the child gets ``SOLVER_TICKET`` and redeems it at
startup (:mod:`solver.auth.identity`) over ``EULER_AUTH_SOCKET`` — the same
socket the service minted it from — which consumes the ticket and returns the
authoritative ``(email, profile, …)``. The instance's **pin** carries in the
environment so the child can refuse a ticket routed to the wrong instance: the
per-user service passes ``slug`` (``EULER_USER_SLUG`` — the redeemed e-mail must
map to it, MT-4/MT-7); the legacy per-profile ws passes ``profile``
(``EULER_PROFILE``). Any inherited ``SOLVER_USER`` is dropped — it is display-only
and the ticket is the truth.
"""
from __future__ import annotations

__all__ = ['PtySession']

import fcntl
import os
import pty
import struct
import subprocess
import sys
import termios

from solver.web.auth import AUTH_SOCKET_ENV

#: How many bytes to pull off the master fd per read.
_READ_CHUNK: int = 65536

#: Post-exec bootstrap: session leader + controlling terminal, then the shell.
#: Runs as ``python -c <this> <argv...>`` (so ``sys.argv[1:]`` is the command) —
#: after Popen's exec, hence thread-safe where a preexec_fn would not be.
_CTTY_BOOTSTRAP: str = (
    'import fcntl, os, sys, termios\n'
    'os.setsid()\n'
    'fcntl.ioctl(0, termios.TIOCSCTTY, 0)\n'
    'os.execvp(sys.argv[1], sys.argv[1:])\n'
)


class PtySession:
    """An interactive ``solver`` shell running on a pseudo-terminal.

    On construction the child is spawned on a fresh PTY: it execs *argv* (the
    solver shell; tests substitute a stub) with ``SOLVER_TICKET`` and the
    instance pin (``EULER_USER_SLUG`` or ``EULER_PROFILE``) exported and a
    colour-capable ``TERM``; the parent retains the PTY master ``fd``. The caller
    drives I/O — ``read()``/``write()`` move bytes, ``resize()`` propagates the
    browser terminal geometry, ``close()`` terminates the child.
    """

    def __init__(self, ticket: str, profile: str = '', argv: tuple[str, ...] = (),
                 auth_socket: str = '', slug: str = '') -> None:
        env = dict(os.environ)
        env['TERM'] = 'xterm-256color'  # prompt-toolkit/rich render styled output
        env['SOLVER_TICKET'] = ticket   # single-use; consumed at redemption (DD-9)
        if slug:
            env['EULER_USER_SLUG'] = slug        # per-user instance pin (MT-4/MT-7)
        if profile:
            env['EULER_PROFILE'] = profile       # legacy per-profile ws pin (DD-13)
        if auth_socket:
            # The child redeems against the *same* socket the parent minted from.
            # Without this it falls back to the compiled-in default path, which is
            # right only when the service happened to be configured by that env var
            # — the socket is the service's configuration, so pass it explicitly.
            env[AUTH_SOCKET_ENV] = auth_socket
        env.pop('SOLVER_USER', None)    # display-only; the ticket is the identity
        master, slave = pty.openpty()
        try:
            self._process = subprocess.Popen(
                [sys.executable, '-c', _CTTY_BOOTSTRAP, *argv],
                stdin=slave, stdout=slave, stderr=slave, env=env, close_fds=True)
        finally:
            os.close(slave)             # the child's stdio holds the slave now
        self.fd: int = master
        self.pid: int = self._process.pid

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
        return self._process.poll() is None

    def close(self) -> None:
        """Terminate the shell and release the master fd (idempotent)."""
        if self._process.poll() is None:
            self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:  # pragma: no cover — a wedged shell
            self._process.kill()
            self._process.wait()
        try:
            os.close(self.fd)
        except OSError:
            pass
