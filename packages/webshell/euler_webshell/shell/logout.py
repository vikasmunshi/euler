#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `logout` shell command: sign out of the web session from the terminal.

A shell cannot sign itself out: the session lives in cookies only the browser holds. So
`logout` asks the page, over `OSC 5379`, and the page draws the countdown and submits the
same form the header's Logout does — one sign-out, whichever control started it. The auth
service then tears this shell down, so the command never returns in the ordinary case. It
waits instead, and a shell no page answered closes itself and says what is left signed in.
"""
from __future__ import annotations

__all__ = ['COUNTDOWN_SECONDS', 'logout']

import time

from euler_webshell.shell import osc
from solver.config import config
from solver.shell import console, register

#: How long the page counts down before it signs out; the notice's button skips it.
COUNTDOWN_SECONDS: int = 5
#: How long past the countdown the sign-out may take before the shell gives up on the page.
_GRACE_SECONDS: int = 10


@register(requires='reader')
def logout() -> int:
    """Sign out of the web session, after a short countdown the notice can skip.

    The page signs out the way the header's Logout does: the session and its remember-me
    token end, the vault locks and this shell closes. Web shell only: a terminal session
    ends with `exit`.
    """
    if config.subject.channel != 'web':
        console.print('[error]error:[/error] logout is for the web shell; use [accent]exit[/accent] here')
        return 2
    osc.logout(COUNTDOWN_SECONDS)
    time.sleep(COUNTDOWN_SECONDS + _GRACE_SECONDS)
    console.print('[warning]no page answered: this shell is closing, but the browser session is '
                  'still signed in.[/warning]')
    raise SystemExit(1)
