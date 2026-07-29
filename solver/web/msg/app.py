#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The message service: public + admin aiohttp apps over unix sockets.

Two listeners, one process, one owner of the spool:

- **Public** (``/run/euler/msg.sock``, group ``euler-web``) — reached by the per-user
  services and their PTY children, never by Caddy. Identity is ``SO_PEERCRED``: the
  connecting uid *is* the caller (:mod:`solver.web.msg.identity`), so nothing on this
  wire carries a sender field and there is no bearer token to leak.
- **Admin** (``/run/euler-adm/msg-admin.sock``, ``0600`` euler-msg-private) — the
  operator's terminal path, never routed by Caddy and **wheel-gated**: only root (via
  sudo) can connect, and ``X-Admin-Token`` (kept solely in root-readable
  ``/etc/euler/msg.env``) is a second check. It exists because the operator's own uid is
  deliberately **not** in ``euler-web`` and so cannot dial the public socket at all.

Authorization on both planes is the plain ladder, resolved **per request** against
``authorizations.json`` — a demote lands within one request rather than at next login.

Delivery is a best-effort nudge to the recipient's own instance socket
(``/internal/message``), the same socket-peer-only push the auth service uses for
logout teardown. The spool is the system of record: a lost nudge costs a stale badge
until the next navigation, never a message.
"""
from __future__ import annotations

__all__ = ['MessageService', 'build_admin_app', 'build_app']

import asyncio
import hmac
import logging
from pathlib import Path
from typing import Any, Awaitable, Callable

import aiohttp
from aiohttp import web

from solver.auth.subject import rank
from solver.web.msg.config import MsgConfig
from solver.web.msg.identity import STAFF_FLOOR, PolicyView, box_of, peer_uid
from solver.web.msg.store import MessageStore, Thread

log = logging.getLogger('euler-msg')

_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]

#: Request key under which the peer middleware stores ``(box, identity, profile)``.
CALLER_KEY: str = 'caller'
#: The floor every read/write of one's *own* mail sits at — the terminal is the front
#: door for every rung, and a new invitee's first need is often to ask a question.
OWN_FLOOR: str = 'reader'
#: Broadcast target meaning "every box the policy maps".
EVERYONE: str = '*'


async def _json_body(request: web.Request) -> dict[str, Any]:
    """The request's JSON object body; an empty dict for anything malformed."""
    try:
        data = await request.json()
    except Exception:                       # noqa: BLE001 — any parse failure is "no body"
        return {}
    return data if isinstance(data, dict) else {}


class MessageService:
    """The spool, the policy view, and the delivery nudge; handlers are thin over this."""

    def __init__(self, config: MsgConfig) -> None:
        self.config = config
        self.store = MessageStore(config.state_dir / 'messages.json')
        self.policy = PolicyView()

    # ── views ──────────────────────────────────────────────────────────────────────

    def is_staff(self, profile: str) -> bool:
        """Whether *profile* is at or above the staff floor."""
        return rank(profile) >= rank(STAFF_FLOOR)

    def render_thread(self, thread: Thread) -> dict[str, Any]:
        """One thread with display identities resolved through the policy view."""
        return thread.summary(author_name=self.policy.identity_of(thread.author))

    def mailbox(self, box: str, profile: str, *, since: str = '') -> dict[str, Any]:
        """The caller's own view: their threads (newest first) and their unread count."""
        staff = self.is_staff(profile)
        threads = self.store.threads_for(box, staff=staff)
        if since:
            threads = [thread for thread in threads if thread.updated > since]
        return {'threads': [self.render_thread(thread) for thread in threads],
                'unread': self.store.unread_count(box, staff=staff),
                'staff': staff}

    # ── writes ─────────────────────────────────────────────────────────────────────

    async def submit(self, box: str, subject: str, body: str) -> str | None:
        """Queue a user→staff question and nudge every staff box that has an instance."""
        staff = self.policy.staff_boxes()
        if not staff:
            log.warning('no staff mapped — refusing to queue a message with no reader')
            return None
        thread_id = self.store.submit(box, subject, body, staff)
        if thread_id is not None:
            await self.notify([target for target in staff if target != box])
        return thread_id

    async def notice(self, box: str, subject: str, body: str,
                     targets: list[str]) -> tuple[str | None, list[str]]:
        """Send a staff notice; return ``(thread id, resolved recipient boxes)``.

        A target the policy does not map is dropped from the set and reported back, so
        a typo is visible to the sender rather than filed into a box nobody can read.
        """
        if targets == [EVERYONE]:
            boxes = [target for target in self.policy.all_boxes() if target != box]
        else:
            boxes = [resolved for resolved in
                     (self.policy.box_for_identity(target) for target in targets)
                     if resolved is not None]
        if not boxes:
            return None, []
        thread_id = self.store.notice(box, subject, body, boxes)
        if thread_id is not None:
            await self.notify(boxes)
        return thread_id, boxes

    async def notify(self, boxes: list[str]) -> None:
        """Nudge each box's own instance so an attached terminal updates its badge.

        Only web identities have an instance to push to; a local os-login (the operator
        at a terminal) has none and simply sees the count when they next run ``msg``.
        Best-effort throughout — the spool is the system of record.
        """
        base = self.config.user_socket_dir
        if not base:
            return
        for box in boxes:
            if not self.policy.is_web(box):
                continue
            await self._push(box, self.store.unread_count(box, staff=False))

    async def _push(self, box: str, unread: int) -> None:
        """POST ``/internal/message`` to *box*'s instance socket; never raises."""
        sock = Path(self.config.user_socket_dir) / f'user-{box}.sock'
        try:
            connector = aiohttp.UnixConnector(path=str(sock))
            timeout = aiohttp.ClientTimeout(total=3)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as http:
                async with http.post('http://user/internal/message',
                                     json={'slug': box, 'unread': unread}) as resp:
                    await resp.read()
        except (OSError, aiohttp.ClientError, asyncio.TimeoutError):
            pass                            # absent / down / slow — the instance isn't there


# ── public app (msg.sock — socket peers only, never routed by Caddy) ────────────────

def build_app(service: MessageService) -> web.Application:
    """The public listener: one collaborator's mail, and the staff verbs for staff."""

    @web.middleware
    async def peer_identity(request: web.Request, handler: _Handler) -> web.StreamResponse:
        """Resolve the connecting uid to ``(box, identity, profile)``, or refuse.

        The kernel is the identity here (web-server-guide § Messaging): a peer whose uid
        maps to no policy entry gets 401, so an un-mapped service account on the
        ``euler-web`` group cannot read or write anyone's mail.
        """
        if request.path == '/healthz':
            return await handler(request)
        sock = request.transport.get_extra_info('socket') if request.transport else None
        uid = peer_uid(sock) if sock is not None else None
        caller = service.policy.resolve_uid(uid) if uid is not None else None
        if caller is None:
            return web.Response(status=401, text='unidentified peer')
        request[CALLER_KEY] = caller
        return await handler(request)

    def caller(request: web.Request) -> tuple[str, str, str]:
        """``(box, identity, profile)`` for this request (the middleware guarantees it)."""
        resolved: tuple[str, str, str] = request[CALLER_KEY]
        return resolved

    def refuse_below(request: web.Request, floor: str) -> web.Response | None:
        """A 403 when the caller is below *floor*, else None."""
        _box, identity, profile = caller(request)
        if rank(profile) < rank(floor):
            log.info('refused %s (%s) below %s on %s', identity, profile, floor, request.path)
            return web.Response(status=403, text=f'requires {floor}')
        return None

    async def healthz(_request: web.Request) -> web.Response:
        return web.Response(text='ok')

    async def mailbox(request: web.Request) -> web.Response:
        """``GET /messages`` — this caller's threads and unread count."""
        box, _identity, profile = caller(request)
        since = request.query.get('since', '').strip()
        return web.json_response(service.mailbox(box, profile, since=since))

    async def one_thread(request: web.Request) -> web.Response:
        """``GET /messages/{id}`` — one thread, if it is the caller's to read."""
        box, _identity, profile = caller(request)
        thread = service.store.thread(request.match_info['id'], box,
                                      staff=service.is_staff(profile))
        if thread is None:
            return web.Response(status=404, text='no such thread')
        return web.json_response(service.render_thread(thread))

    async def submit(request: web.Request) -> web.Response:
        """``POST /messages`` ``{subject, body}`` — ask staff something."""
        box, identity, _profile = caller(request)
        body = await _json_body(request)
        thread_id = await service.submit(box, str(body.get('subject', '')), str(body.get('body', '')))
        if thread_id is None:
            return web.Response(status=400, text='message refused (empty, too long, or over quota)')
        log.info('message queued by %s (%s)', identity, thread_id)
        return web.json_response({'id': thread_id}, status=201)

    async def mark_read(request: web.Request) -> web.Response:
        """``POST /messages/{id}/read`` — mark a thread read by this caller."""
        box, _identity, profile = caller(request)
        thread_id = request.match_info['id']
        if not service.store.mark_read(thread_id, box, staff=service.is_staff(profile)):
            return web.Response(status=404, text='no such thread')
        return web.json_response({'id': thread_id, 'read': True})

    async def queue(request: web.Request) -> web.Response:
        """``GET /staff/queue`` — the inbound queue as a work list (staff only)."""
        refused = refuse_below(request, STAFF_FLOOR)
        if refused is not None:
            return refused
        box, _identity, _profile = caller(request)
        return web.json_response(
            {'queue': [service.render_thread(t) for t in service.store.inbound(box)]})

    async def notice(request: web.Request) -> web.Response:
        """``POST /staff/notice`` ``{to, subject, body}`` — named recipients or ``*``."""
        refused = refuse_below(request, STAFF_FLOOR)
        if refused is not None:
            return refused
        box, identity, _profile = caller(request)
        body = await _json_body(request)
        raw_to = body.get('to')
        targets = [str(raw_to)] if isinstance(raw_to, str) else [str(t) for t in (raw_to or [])]
        thread_id, boxes = await service.notice(box, str(body.get('subject', '')),
                                                str(body.get('body', '')), targets)
        if thread_id is None:
            return web.Response(status=400, text='notice refused (no known recipient, or bad fields)')
        log.info('%s sent a notice to %d box(es) (%s)', identity, len(boxes), thread_id)
        return web.json_response({'id': thread_id, 'recipients': len(boxes)}, status=201)

    async def dismiss(request: web.Request) -> web.Response:
        """``DELETE /staff/queue/{id}`` — drop a worked thread (staff only)."""
        refused = refuse_below(request, STAFF_FLOOR)
        if refused is not None:
            return refused
        thread_id = request.match_info['id']
        if not service.store.drop(thread_id):
            return web.Response(status=404, text='no such thread')
        log.info('thread %s dismissed', thread_id)
        return web.json_response({'id': thread_id, 'dismissed': True})

    app = web.Application(middlewares=[peer_identity])
    app.add_routes([
        web.get('/healthz', healthz),
        web.get('/messages', mailbox),
        web.post('/messages', submit),
        web.get('/messages/{id}', one_thread),
        web.post('/messages/{id}/read', mark_read),
        web.get('/staff/queue', queue),
        web.delete('/staff/queue/{id}', dismiss),
        web.post('/staff/notice', notice),
    ])
    return app


# ── admin app (msg-admin.sock — root via sudo, never via Caddy) ─────────────────────

def build_admin_app(service: MessageService) -> web.Application:
    """The operator's terminal plane: the same verbs, with the identity asserted by root.

    Root could bypass any check here, so the token and the profile validation are not
    containment against root — they keep the *ladder* the boundary (a typo cannot file a
    message under a stranger's name) and stop any non-root uid that somehow reached the
    socket.
    """

    @web.middleware
    async def require_token(request: web.Request, handler: _Handler) -> web.StreamResponse:
        if request.path != '/healthz':
            token = request.headers.get('X-Admin-Token', '')
            if not hmac.compare_digest(token, service.config.admin_token):
                return web.Response(status=401, text='bad admin token')
        return await handler(request)

    def resolve(request: web.Request, body: dict[str, Any] | None = None) -> tuple[str, str] | None:
        """``(box, profile)`` for the asserted identity, or None when unmapped.

        The identity may be a web address or an os-login — :func:`box_of` collapses both
        to the box the store routes by.
        """
        raw = str((body or {}).get('identity', '') or request.query.get('identity', '')).strip()
        found = service.policy.resolve(raw) if raw else None
        return None if found is None else (box_of(found[0]), found[1])

    async def healthz(_request: web.Request) -> web.Response:
        return web.Response(text='ok')

    async def mailbox(request: web.Request) -> web.Response:
        who = resolve(request)
        if who is None:
            return web.Response(status=400, text='identity required (and must be in the policy)')
        return web.json_response(service.mailbox(who[0], who[1]))

    async def one_thread(request: web.Request) -> web.Response:
        who = resolve(request)
        if who is None:
            return web.Response(status=400, text='identity required')
        thread = service.store.thread(request.match_info['id'], who[0],
                                      staff=service.is_staff(who[1]))
        if thread is None:
            return web.Response(status=404, text='no such thread')
        return web.json_response(service.render_thread(thread))

    async def submit(request: web.Request) -> web.Response:
        body = await _json_body(request)
        who = resolve(request, body)
        if who is None:
            return web.Response(status=400, text='identity required')
        thread_id = await service.submit(who[0], str(body.get('subject', '')), str(body.get('body', '')))
        if thread_id is None:
            return web.Response(status=400, text='message refused (empty, too long, or over quota)')
        return web.json_response({'id': thread_id}, status=201)

    async def mark_read(request: web.Request) -> web.Response:
        body = await _json_body(request)
        who = resolve(request, body)
        if who is None:
            return web.Response(status=400, text='identity required')
        thread_id = request.match_info['id']
        if not service.store.mark_read(thread_id, who[0], staff=service.is_staff(who[1])):
            return web.Response(status=404, text='no such thread')
        return web.json_response({'id': thread_id, 'read': True})

    async def queue(request: web.Request) -> web.Response:
        who = resolve(request)
        if who is None:
            return web.Response(status=400, text='identity required')
        if not service.is_staff(who[1]):
            return web.Response(status=403, text=f'requires {STAFF_FLOOR}')
        return web.json_response(
            {'queue': [service.render_thread(t) for t in service.store.inbound(who[0])]})

    async def notice(request: web.Request) -> web.Response:
        body = await _json_body(request)
        who = resolve(request, body)
        if who is None:
            return web.Response(status=400, text='identity required')
        if not service.is_staff(who[1]):
            return web.Response(status=403, text=f'requires {STAFF_FLOOR}')
        raw_to = body.get('to')
        targets = [str(raw_to)] if isinstance(raw_to, str) else [str(t) for t in (raw_to or [])]
        thread_id, boxes = await service.notice(who[0], str(body.get('subject', '')),
                                                str(body.get('body', '')), targets)
        if thread_id is None:
            return web.Response(status=400, text='notice refused (no known recipient, or bad fields)')
        return web.json_response({'id': thread_id, 'recipients': len(boxes)}, status=201)

    async def dismiss(request: web.Request) -> web.Response:
        body = await _json_body(request)
        who = resolve(request, body)
        if who is None:
            return web.Response(status=400, text='identity required')
        if not service.is_staff(who[1]):
            return web.Response(status=403, text=f'requires {STAFF_FLOOR}')
        thread_id = request.match_info['id']
        if not service.store.drop(thread_id):
            return web.Response(status=404, text='no such thread')
        return web.json_response({'id': thread_id, 'dismissed': True})

    app = web.Application(middlewares=[require_token])
    app.add_routes([
        web.get('/healthz', healthz),
        web.get('/admin/messages', mailbox),
        web.post('/admin/messages', submit),
        web.get('/admin/threads/{id}', one_thread),
        web.post('/admin/threads/{id}/read', mark_read),
        web.get('/admin/queue', queue),
        web.post('/admin/notice', notice),
        web.delete('/admin/threads/{id}', dismiss),
    ])
    return app
