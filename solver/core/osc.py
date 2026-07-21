#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The shell → browser control channel: `OSC 5379`.

A **web** shell runs on a PTY whose bytes are a WebSocket away from the page that
frames it (:mod:`solver.web.ws`), so a command can speak to the browser chrome by
writing a control sequence into its own stdout: ``ESC ] 5379 ; <payload> BEL``.
The counterpart is ``solver/web/content/assets/terminal.js``'s
``registerOscHandler(5379, …)``, which parses the payload and asks its parent page
to act — the shell drives the chrome, never the other way round.

The payloads, one per action — the first field is always the action, and every
payload carries a *token* (:func:`token`):

- ``open;<NNNN>;<token>`` — show problem *NNNN* in the left pane.
- ``edit;<NNNN>;<token>;<relpath>`` — open *relpath* in the pane's editor. The
  token sits *before* the path because a relpath may itself contain ``;``: it is
  the one field that must stay last and be rejoined by the reader.
- ``git;<token>`` — this clone's git state changed; re-read the header's chip.
- ``account;<token>`` — this user's account state changed (a new identity, a GitHub
  sign-in); re-read the account page — *if it is the visible pane*.

The token is a server-side millisecond clock, strictly increasing per command. On
attach the service replays the scrollback, which redraws the sequences of commands
that already ran; the token lets the browser tell a replay from a fresh act and obey
only the latter (`terminal.js`, § the OSC handler).

This module is the one definition of that wire. It holds no state and imports only
:mod:`solver.config` (for the channel), so both the viewer (:mod:`solver.core.viewer`)
and the git commands (:mod:`solver.core.git`) can emit without depending on each
other.
"""
from __future__ import annotations

__all__ = ['OSC_CODE', 'account_changed', 'emit', 'git_changed', 'token']

import sys
import time

from solver.config import config

#: The OSC identifier shared with `terminal.js`'s `registerOscHandler`.
OSC_CODE: int = 5379


def token() -> int:
    """A strictly increasing per-command stamp: the wall clock in milliseconds.

    Exposed because the token's *position* is part of each payload's shape (``edit``
    keeps its relpath last), so the caller places it — but no caller invents its own
    clock.
    """
    return time.time_ns() // 1_000_000


def emit(action: str, *fields: str) -> None:
    """Write ``ESC ] 5379 ; <action> ; <fields…> BEL`` to stdout — web channel only.

    A no-op off the web channel: a terminal shell's stdout is a real terminal, and an
    escape sequence no one is listening for would just be noise in it. Callers
    therefore need no channel test for the *emission* — only for the user-facing
    difference (the viewer opens a named browser tab instead).
    """
    if config.subject.channel != 'web':
        return
    sys.stdout.write(f'\x1b]{OSC_CODE};{";".join((action, *fields))}\x07')
    sys.stdout.flush()


def git_changed() -> None:
    """Tell the page this clone's git state moved: the header re-reads its chip.

    Emitted by the git commands (:mod:`solver.core.git`) on the success paths
    that can change what the chip shows — a commit, a sync, a push, a wired filter.
    The header reads its state once per navigation and never polls, so without this
    the chip would be at its most wrong exactly after the user acted. It is only a
    *nudge*: the browser answers by re-reading ``/git``, so a lost or replayed
    sequence costs at most a stale chip until the next navigation, never a wrong one.

    Because this rides the shell's own stdout, it fires for a hand-typed ``git-sync``
    exactly as it does for the header menu's item — the menu types the same command,
    so there is one path, not two.
    """
    emit('git', str(token()))


def account_changed() -> None:
    """Tell the page this user's account state moved: refresh the account panel.

    Emitted by the commands that change what the account page shows about *you* — a
    new key pair (``user``), a GitHub sign-in (``git-identity``). The nudge reaches
    the page the same way ``git;`` does; the difference is on the browser side, where
    the listening element lives **inside** the account fragment, so it re-reads only
    when the account page is the visible pane and is a no-op otherwise (web-server-guide
    § The site). The chip's own git state is a separate concern: `git-sync` /
    `git-filter` change decrypt access too, but they emit :func:`git_changed`, and the
    account panel listens for that event as well — so those need not emit both.
    """
    emit('account', str(token()))
