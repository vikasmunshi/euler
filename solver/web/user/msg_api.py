#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The header's message chip for the per-user service (web-server-guide § Messaging).

The whole browser half of the message spool, and deliberately almost nothing: **one
read-only fragment** and the delivery push. There is no messages page, no compose form
and no thread view, because the spool is not a mailbox — it is how a *command* tells
staff something they must act on (`user` filing a key-authorization request). Reading and
writing happen in the shell, where `requires()` is the boundary; the chip reports, and
its rows type `msg read <id>` into the terminal.

The consequence worth stating: **the browser cannot write to the spool at all.** Every
message and every reply arrives over ``msg.sock`` from a uid the kernel vouched for. This
tier holds no write route to remove the temptation, which is a smaller surface than a
guarded one.

Two deliveries, both over paths that already exist:

- ``POST /internal/message`` — socket-peer only (Caddy answers ``/internal/*`` itself),
  pushed by ``euler-msg`` when something lands for this user. It sends a **text frame**
  to any attached terminal, which ``terminal.js`` relays to the page so the chip re-reads.
  It never touches the PTY: a service-originated sequence in the shell's byte stream would
  land in the replay buffer and re-fire on every reattach.
- ``GET /messages`` on document load, so a user who was away sees the count without a
  push having reached them.
"""
from __future__ import annotations

__all__ = ['add_message_routes']

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import aiohttp
from aiohttp import web

from solver.web.msg import DEFAULT_MSG_SOCKET, MSG_SOCKET_ENV
from solver.web.msg.identity import STAFF_FLOOR
from solver.web.site.app import requires
from solver.web.site.render import MSG_SPOOL_KEY, render
from solver.web.ws.manager import PtyManager

log = logging.getLogger('euler-user')

#: Reading your own chip sits at the reader floor — every rung gets one.
_MSG_REQUIRES: str = 'reader'
#: Rows in the menu. Enough to see what is waiting without turning the chip into a page;
#: `msg list` in the shell is the complete view.
_ROWS: int = 5
#: How long to wait on the spool. It is a local socket doing a small JSON read; a slow
#: answer means the service is wedged, and the header must not hold the page for it.
_TIMEOUT = aiohttp.ClientTimeout(total=5)


def _socket_path() -> str:
    """The spool socket this instance dials (env-overridable for tests and dev runs)."""
    return os.environ.get(MSG_SOCKET_ENV, DEFAULT_MSG_SOCKET)


async def _mailbox(request: web.Request) -> dict[str, Any]:
    """This caller's threads and unread count; an empty mailbox when the spool is absent.

    A dead or undeployed spool reads as "no messages" rather than raising: messaging is
    the least important thing in the header, and it must not take a page render down with
    it. The chip is identical either way — which is the honest rendering, since a spool
    that cannot be reached genuinely has nothing to tell us.
    """
    try:
        connector = aiohttp.UnixConnector(path=_socket_path())
        async with aiohttp.ClientSession(connector=connector, timeout=_TIMEOUT) as http:
            async with http.get('http://msg/messages') as resp:
                if resp.status != 200:
                    log.warning('message spool refused the mailbox read (%s)', resp.status)
                    return {}
                data = await resp.json()
                return data if isinstance(data, dict) else {}
    except (OSError, aiohttp.ClientError, TimeoutError, ValueError) as exc:
        log.debug('message spool unreachable: %s', exc)
        return {}


def _when(stamp: str) -> str:
    """A menu-width timestamp: the time for today, the date for anything older.

    The row has one narrow column for this, and "when" at a glance is either "today, at
    this time" or "a while ago, on this date" — a full ISO string in that space would be
    truncated into neither.
    """
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    return stamp[11:16] if stamp[:10] == today else stamp[:10]


def _rows(threads: list[Any]) -> list[dict[str, Any]]:
    """The newest :data:`_ROWS` threads, unread first, as menu rows.

    Unread first because the chip's job is "what wants you"; within each group the spool's
    own newest-first order is kept. Only the fields the row shows survive the trip — the
    body never reaches the browser, since it is read in the shell.
    """
    ordered = sorted((t for t in threads if isinstance(t, dict)),
                     key=lambda t: not t.get('unread'))
    return [{'id': str(t.get('id', '')),
             'author_name': str(t.get('author_name', '')),
             'subject': str(t.get('subject', '')),
             'unread': bool(t.get('unread')),
             'when': _when(str(t.get('updated', '')))}
            for t in ordered[:_ROWS]]


def add_message_routes(app: web.Application, manager: PtyManager) -> None:
    """Register the header chip's fragment and the delivery push on the per-user app.

    *manager* is passed in rather than read from an app key: the key that holds it is
    defined in :mod:`solver.web.user.app`, which imports this module, so reaching for it
    here would close an import cycle for no gain.
    """

    @web.middleware
    async def spool_present(request: web.Request, handler: Any) -> web.StreamResponse:
        """Tell every render on this tier that a spool exists behind the header's chip.

        A flag, never a count: the chip must not cost a spool read per navigation, so it
        fetches its own state once per document (:mod:`solver.web.site.render`).
        """
        request[MSG_SPOOL_KEY] = True
        return await handler(request)  # type: ignore[no-any-return]

    app.middlewares.append(spool_present)

    @requires(_MSG_REQUIRES)
    async def chip(request: web.Request) -> web.StreamResponse:
        """``GET /messages`` — the header's message chip alone, with its rows.

        The same shape ``/git`` has, and for the same reason: the count moves when someone
        *else* acts, which no navigation can predict, so the chip asks for itself on load
        and on the delivery nudge rather than riding every fragment out-of-band.
        """
        mailbox = await _mailbox(request)
        threads = mailbox.get('threads') or []
        return render(request, '_msg.html', {
            'unread': mailbox.get('unread') or 0,
            'total': len(threads),
            'threads': _rows(threads),
            # The rung the queue verb needs, so the template does not carry a second
            # copy of it — the floor lives with the service that enforces it.
            'staff_floor': STAFF_FLOOR,
        })

    async def internal_message(request: web.Request) -> web.Response:
        """``POST /internal/message`` — the spool's delivery nudge.

        Socket-peer only, like the auth service's logout push: Caddy answers
        ``/internal/*`` with 404 rather than routing it, so the only callers are root and
        the ``euler-web`` tier over this user's own socket. It changes nothing — it tells
        an attached terminal that the count moved, and the browser re-reads the chip.
        """
        try:
            body: Any = await request.json()
        except json.JSONDecodeError:
            return web.Response(status=400, text='bad request')
        unread = int(body.get('unread', 0)) if isinstance(body, dict) else 0
        sent = await manager.notify_all(json.dumps({'euler': 'message', 'unread': unread}))
        log.info('message nudge (%d unread) reached %d terminal(s)', unread, sent)
        return web.json_response({'notified': sent})

    app.add_routes([
        web.get('/messages', chip),
        web.post('/internal/message', internal_message),
    ])
