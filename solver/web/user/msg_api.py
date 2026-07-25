#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Message routes for the per-user service (web-server-guide § Messaging).

The browser half of the message spool. These routes exist only on the per-user
instance, and that is what makes them cheap: the process runs as the collaborator's own
uid, so a call to ``msg.sock`` is authenticated by ``SO_PEERCRED`` alone — no session
cookie is forwarded, no token is held, and the spool needs no contact with the auth
service to know who is asking.

Nothing here holds state. Every handler is a translation between the spool's JSON and a
rendered fragment, so the store stays the single system of record and this tier cannot
develop its own idea of what a thread says.

Two deliveries, both nudges over paths that already exist:

- ``POST /internal/message`` — socket-peer only (Caddy answers ``/internal/*`` itself),
  pushed by ``euler-msg`` when something lands for this user. It sends a **text frame**
  to any attached terminal, which ``terminal.js`` relays to the page and the header's
  chip picks up. It never touches the PTY: a service-originated sequence in the shell's
  byte stream would re-fire out of the replay buffer on every reattach.
- the chip's own ``GET /messages/badge`` on document load, so a user who was away sees
  the count without a push having reached them.
"""
from __future__ import annotations

__all__ = ['add_message_routes']

import json
import logging
import os
from typing import Any

import aiohttp
from aiohttp import web

from solver.auth import Authorizations
from solver.web.msg import DEFAULT_MSG_SOCKET, MSG_SOCKET_ENV
from solver.web.msg.identity import STAFF_FLOOR
from solver.web.msg.store import BODY_MAX, SUBJECT_MAX
from solver.web.site.app import redirect_slash, requires
from solver.web.site.render import MSG_SPOOL_KEY, SUBJECT_KEY, render
from solver.web.ws.manager import PtyManager

log = logging.getLogger('euler-user')

#: Reading and writing your *own* mail sits at the reader floor — the terminal is the
#: front door for every rung, and asking a question is often a new invitee's first act.
_MSG_REQUIRES: str = 'reader'
#: Home crumb, matching the content tier's own.
_HOME = ('euler', '/')
#: How long to wait on the spool. It is a local socket doing a small JSON read; a
#: slow answer means the service is wedged, and a page should say so rather than hang.
_TIMEOUT = aiohttp.ClientTimeout(total=10)


def _socket_path() -> str:
    """The spool socket this instance dials (env-overridable for tests and dev runs)."""
    return os.environ.get(MSG_SOCKET_ENV, DEFAULT_MSG_SOCKET)


async def _spool(request: web.Request, method: str, path: str,
                 body: dict[str, Any] | None = None) -> tuple[int, Any]:
    """One call to ``msg.sock`` as this uid; ``(status, parsed)``.

    A dead or absent spool comes back as ``(503, {})`` rather than raising, so a page
    renders an empty mailbox with a notice instead of a 500 — the rest of the site has
    nothing to do with messaging and must not fail with it.
    """
    try:
        connector = aiohttp.UnixConnector(path=_socket_path())
        async with aiohttp.ClientSession(connector=connector, timeout=_TIMEOUT) as http:
            async with http.request(method, f'http://msg{path}', json=body) as resp:
                try:
                    return resp.status, await resp.json()
                except (aiohttp.ContentTypeError, json.JSONDecodeError, ValueError):
                    return resp.status, await resp.text()
    except (OSError, aiohttp.ClientError, TimeoutError) as exc:
        log.warning('message spool unreachable: %s', exc)
        return 503, {}


def _is_staff(request: web.Request) -> bool:
    """Whether this request's subject is at or above the staff floor."""
    subject = request.get(SUBJECT_KEY)
    return subject is not None and subject.has(STAFF_FLOOR)


def _recipients(request: web.Request) -> list[str]:
    """Every identity the policy maps — the notice form's datalist.

    Read straight from the world-readable policy file rather than asked of the spool:
    it is the same source the spool itself validates against, and the answer is not
    secret (a maintainer picking a recipient already knows the roster).
    """
    return sorted(Authorizations.load().all_users())


async def _pane(request: web.Request, *, flash: str = '', status: int = 200) -> web.Response:
    """Render the mailbox pane: your threads, plus the staff queue when you are staff."""
    code, data = await _spool(request, 'GET', '/messages')
    mailbox: dict[str, Any] = data if isinstance(data, dict) else {}
    staff = _is_staff(request)
    queue: list[Any] = []
    if staff:
        queue_code, queue_data = await _spool(request, 'GET', '/staff/queue')
        if queue_code == 200 and isinstance(queue_data, dict):
            queue = queue_data.get('queue') or []
    if code == 503 and not flash:
        flash = 'The message service is not reachable right now.'
    return render(request, 'messages.html', {
        'threads': mailbox.get('threads') or [],
        'unread': mailbox.get('unread') or 0,
        'queue': queue,
        'is_staff': staff,
        'recipients': _recipients(request) if staff else [],
        'thread': None,
        'flash': flash,
        'subject_max': SUBJECT_MAX,
        'body_max': BODY_MAX,
        'crumbs': [_HOME, ('messages', None)],
    }, block='content', status=status)


def add_message_routes(app: web.Application, manager: PtyManager) -> None:
    """Register the message pane, its writes, and the delivery push on the per-user app.

    *manager* is passed in rather than read from an app key: the key that holds it is
    defined in :mod:`solver.web.user.app`, which imports this module, so reaching for it
    here would close an import cycle for no gain.
    """

    @web.middleware
    async def spool_present(request: web.Request, handler: Any) -> web.StreamResponse:
        """Tell every render on this tier that a spool exists behind the header's chip.

        A flag, never a count: the chip must not cost a spool read per navigation, so it
        fetches its own number once per document (:mod:`solver.web.site.render`).
        """
        request[MSG_SPOOL_KEY] = True
        return await handler(request)  # type: ignore[no-any-return]

    app.middlewares.append(spool_present)

    @requires(_MSG_REQUIRES)
    async def pane(request: web.Request) -> web.StreamResponse:
        """``GET /messages/`` — the mailbox."""
        return await _pane(request)

    @requires(_MSG_REQUIRES)
    async def badge(request: web.Request) -> web.StreamResponse:
        """``GET /messages/badge`` — the header chip alone, with the live unread count.

        The refresh half of the chip's contract, the same shape ``/git`` has: the count
        changes when someone *else* acts, which no navigation can predict, so the chip
        asks for itself on load and on the delivery nudge.
        """
        code, data = await _spool(request, 'GET', '/messages')
        unread = data.get('unread', 0) if code == 200 and isinstance(data, dict) else 0
        return render(request, '_msg.html', {'msg_unread': unread})

    @requires(_MSG_REQUIRES)
    async def one_thread(request: web.Request) -> web.StreamResponse:
        """``GET /messages/{id}`` — one thread, marked read as it is shown."""
        thread_id = request.match_info['id']
        code, data = await _spool(request, 'GET', f'/messages/{thread_id}')
        if code != 200 or not isinstance(data, dict):
            raise web.HTTPNotFound(text='no such thread')
        await _spool(request, 'POST', f'/messages/{thread_id}/read')
        return render(request, 'messages.html', {
            'thread': data,
            'is_staff': _is_staff(request),
            'subject_max': SUBJECT_MAX,
            'body_max': BODY_MAX,
            'crumbs': [_HOME, ('messages', '/messages/'), (data.get('subject', 'thread'), None)],
        }, block='content')

    @requires(_MSG_REQUIRES)
    async def compose(request: web.Request) -> web.StreamResponse:
        """``POST /messages/`` — ask staff something; answers with the pane."""
        form = await request.post()
        code, data = await _spool(request, 'POST', '/messages', {
            'subject': str(form.get('subject', '')), 'body': str(form.get('body', ''))})
        if code == 201:
            return await _pane(request, flash='Sent — the maintainers will see it in their queue.')
        detail = data if isinstance(data, str) else 'message refused'
        return await _pane(request, flash=detail, status=400 if code < 500 else 503)

    @requires(_MSG_REQUIRES)
    async def reply(request: web.Request) -> web.StreamResponse:
        """``POST /messages/{id}/reply`` — answer on a thread you are party to."""
        thread_id = request.match_info['id']
        form = await request.post()
        code, _data = await _spool(request, 'POST', f'/messages/{thread_id}/reply',
                                   {'body': str(form.get('body', ''))})
        if code != 200:
            return await _pane(request, flash='Reply refused.', status=400)
        return await one_thread(request)

    @requires(STAFF_FLOOR)
    async def notice(request: web.Request) -> web.StreamResponse:
        """``POST /messages/notice`` — a staff notice to named recipients, or everyone.

        An empty recipient box means everyone: the common case for a notice is "tell
        the collaborators", and making that the default of an empty field beats a
        checkbox that has to be found.
        """
        form = await request.post()
        raw = str(form.get('to', '')).strip()
        targets: Any = [part.strip() for part in raw.split(',') if part.strip()] if raw else '*'
        code, data = await _spool(request, 'POST', '/staff/notice', {
            'to': targets, 'subject': str(form.get('subject', '')),
            'body': str(form.get('body', ''))})
        if code == 201 and isinstance(data, dict):
            count = data.get('recipients', 0)
            return await _pane(request, flash=f'Notice sent to {count} recipient(s).')
        detail = data if isinstance(data, str) else 'notice refused'
        return await _pane(request, flash=detail, status=400 if code < 500 else 503)

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

    # `/messages/badge` before `/messages/{id}`: aiohttp matches in registration order,
    # and the dynamic route would otherwise swallow the literal one.
    app.add_routes([
        web.get('/messages', redirect_slash),      # canonical trailing slash (§ The site)
        web.get('/messages/', pane),
        web.post('/messages/', compose),
        web.get('/messages/badge', badge),
        web.post('/messages/notice', notice),
        web.get('/messages/{id}', one_thread),
        web.post('/messages/{id}/reply', reply),
        web.post('/internal/message', internal_message),
    ])
