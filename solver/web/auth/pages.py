#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The auth service's HTML pages: login, registration, reset, forgot.

First Jinja-rendered pages of the redesign. Server-rendered throughout, with
POST → redirect → GET after every state change so reloads are safe. The two
JS-dependent moments — the SRP login handshake and the set-password verifier
derivation — run from same-origin ``/assets`` scripts (CSP: no inline code).

Flow endpoints (all on the public socket; Caddy exposes them in step 5):

    GET  /login                    the sign-in page (JS drives /auth/challenge+verify)
    GET  /register?token=…         invite link → Terms → OTP → set password
    GET  /reset?token=…            self-service reset → OTP → set password
    POST /register/otp /reset/otp        accept Terms (register) + mail an OTP
    POST /register/verify /reset/verify  check the OTP
    POST /register/complete /reset/complete   store {salt, verifier}, single-use
    GET+POST /forgot               request a reset link (generic response)

Every invalid/expired/foreign token renders the same generic message — no
account enumeration; responses never echo the token except in the redirect the
browser already holds. OTP mail runs in a worker thread (the Gmail submission
must not block the event loop).
"""
from __future__ import annotations

__all__ = ['add_page_routes']

import asyncio
import logging
from urllib.parse import quote, urlsplit, urlunsplit

import aiohttp_jinja2
from aiohttp import web

from solver.web.auth.app import AuthService, _client_key, utcnow_iso
from solver.web.auth.pending import PendingRecord
from solver.web.auth.requests import NAME_MAX, REMARKS_MAX, sanitize
from solver.web.auth.users import normalize_email

log = logging.getLogger('euler-auth')

#: pending-record state → which stage of register.html to render, per kind.
_STAGES = {
    'register': {'invited': 'terms', 'otp_sent': 'otp', 'verified': 'password'},
    'reset': {'invited': 'request', 'otp_sent': 'otp', 'verified': 'password'},
}

_FLAGS = {
    'sent': ('notice', 'A verification code is on its way to your mailbox.'),
    'badotp': ('error', 'Wrong or expired code — try again.'),
    'exhausted': ('error', 'Too many wrong attempts — request a fresh code.'),
    'mailfail': ('error', 'The code could not be emailed just now — try again shortly.'),
    'capped': ('error', 'No more codes can be sent for this link — ask for a fresh invite.'),
}


#: The signed-out pages that may link the standalone Terms — path → the name the
#: back link calls it. Anything else (a stale bookmark, a foreign site, a typed
#: URL) is not a page we can return someone to, so it falls back to sign-in.
_BACK_LABELS = {
    '/login': 'sign in',
    '/register': 'registration',
    '/reset': 'password reset',
    '/forgot': 'password reset',
    '/password': 'change password',
}
_BACK_DEFAULT = ('/login', _BACK_LABELS['/login'])


def _back_link(request: web.Request) -> tuple[str, str]:
    """The (href, label) the standalone Terms page returns a reader to.

    ``Referrer-Policy: no-referrer`` (csp.py) means there is no ``Referer`` to
    read, so the caller names itself: base.html's footer carries its own path in
    ``?back=`` — with the query intact, so a half-finished registration comes
    back to its own token rather than to a dead link. The value is only ever
    honoured when it is a relative path (no scheme, no host — ``//evil.example``
    is a netloc, not a path) naming one of our own pages.
    """
    raw = request.query.get('back', '')
    parsed = urlsplit(raw)
    if not raw.startswith('/') or parsed.scheme or parsed.netloc:
        return _BACK_DEFAULT
    label = _BACK_LABELS.get(parsed.path)
    if label is None:
        return _BACK_DEFAULT
    return urlunsplit(('', '', parsed.path, parsed.query, '')), label


def _is_htmx(request: web.Request) -> bool:
    """True when the content shell fetched this page for its left pane (``HX-Request``).

    The terms / change-password pages then answer with a bare fragment instead
    of the full auth card, so the shell can swap it into ``#content`` without
    nesting a second page.
    """
    return request.headers.get('HX-Request', '').lower() == 'true'


def _bad_link(request: web.Request) -> web.Response:
    """The one generic answer for any invalid/expired/foreign token."""
    return aiohttp_jinja2.render_template('message.html', request, {
        'heading': 'This link is not valid',
        'message': 'It may have expired or already been used. '
                   'Request a fresh one, or contact the operator.',
        'show_login': True})


def _flash(request: web.Request) -> dict[str, str]:
    """Map redirect flags (?sent=1 …) onto the template's error/notice banners."""
    context: dict[str, str] = {}
    for flag, (key, text) in _FLAGS.items():
        if flag in request.query:
            context[key] = text
    return context


def add_page_routes(app: web.Application, service: AuthService) -> None:
    """Attach the HTML flow to the public app."""

    def render_stage(request: web.Request, kind: str, token: str,
                     record: PendingRecord) -> web.Response:
        return aiohttp_jinja2.render_template('register.html', request, {
            'kind': kind, 'base': f'/{"register" if kind == "register" else "reset"}',
            'token': token, 'email': record.email,
            'stage': _STAGES[kind][record.state],
            'terms_version': service.config.terms_version,
            **_flash(request)})

    def record_for(request: web.Request, kind: str) -> tuple[str, PendingRecord] | None:
        """The (token, live record) for the request, or None — form body over query."""
        token = str(request.get('form_token') or request.query.get('token', ''))
        if not token:
            return None
        record = service.pending.get(token)
        if record is None or record.kind != kind:
            return None
        return token, record

    def redirect(kind: str, token: str, flag: str = '') -> web.HTTPSeeOther:
        suffix = f'&{flag}=1' if flag else ''
        return web.HTTPSeeOther(location=f'/{kind}?token={quote(token)}{suffix}')

    # ── login ─────────────────────────────────────────────────────────────────────

    async def login_page(request: web.Request) -> web.Response:
        context: dict[str, str] = {}
        if 'registered' in request.query:
            context['notice'] = 'Registration complete — sign in with your new password.'
        elif 'reset' in request.query:
            context['notice'] = 'Password updated — sign in with your new password.'
        return aiohttp_jinja2.render_template('login.html', request, context)

    # ── the shared invite/reset pipeline ───────────────────────────────────

    async def flow_page(request: web.Request) -> web.Response:
        kind = 'register' if request.path.startswith('/register') else 'reset'
        found = record_for(request, kind)
        if found is None:
            return _bad_link(request)
        return render_stage(request, kind, *found)

    async def flow_otp(request: web.Request) -> web.Response:
        """Accept Terms (registration) and mail a fresh OTP."""
        kind = 'register' if request.path.startswith('/register') else 'reset'
        if not service.rate.allow(_client_key(request)):
            return web.Response(status=429, text='rate limited')
        form = await request.post()
        request['form_token'] = form.get('token', '')
        found = record_for(request, kind)
        if found is None:
            return _bad_link(request)
        token, record = found
        if kind == 'register':
            if form.get('accepted') != 'yes':
                return render_stage(request, kind, token, record)
            service.pending.accept_terms(token, service.config.terms_version, utcnow_iso())
        otp = service.pending.issue_otp(token)
        if otp is None:                        # send cap reached (or already verified)
            raise redirect(kind, token, 'capped')
        try:
            await asyncio.to_thread(service.mailer.send_otp, record.email, otp)
        except OSError as exc:
            log.warning('otp mail to %s failed: %s', record.email, exc)
            raise redirect(kind, token, 'mailfail')
        log.info('otp sent for %s (%s)', record.email, kind)
        raise redirect(kind, token, 'sent')

    async def flow_verify(request: web.Request) -> web.Response:
        kind = 'register' if request.path.startswith('/register') else 'reset'
        if not service.rate.allow(_client_key(request)):
            return web.Response(status=429, text='rate limited')
        form = await request.post()
        request['form_token'] = form.get('token', '')
        found = record_for(request, kind)
        if found is None:
            return _bad_link(request)
        token, _record = found
        if service.pending.verify_otp(token, str(form.get('otp', ''))):
            raise redirect(kind, token)        # → password stage
        after = service.pending.get(token)
        flag = 'exhausted' if after is not None and after.state == 'invited' else 'badotp'
        raise redirect(kind, token, flag)

    async def flow_complete(request: web.Request) -> web.Response:
        """Store the browser-derived {salt, verifier}; single-use (the set-password step)."""
        kind = 'register' if request.path.startswith('/register') else 'reset'
        if not service.rate.allow(_client_key(request)):
            return web.Response(status=429, text='rate limited')
        form = await request.post()
        token = str(form.get('token', ''))
        salt = str(form.get('salt', '')).lower()
        verifier = str(form.get('verifier', '')).lower()
        try:                                    # sanity: well-formed hex of sane size
            if not (len(salt) == 32 and 0 < len(verifier) <= 512 and int(verifier, 16) > 0):
                raise ValueError
            bytes.fromhex(salt)
        except ValueError:
            return _bad_link(request)
        record = service.pending.consume(token)    # only succeeds in state 'verified'
        if record is None or record.kind != kind:
            return _bad_link(request)
        if kind == 'register':
            # The profile is not stored on the SRP record — it lives in
            # authorizations.json, assigned by the admin `users add/change` path.
            service.users.create(record.email, salt, verifier,
                                 record.terms_version, record.terms_accepted_at)
            log.info('registration completed for %s (profile from authorizations.json)', record.email)
            raise web.HTTPSeeOther(location='/login?registered=1')
        if not service.users.set_credentials(record.email, salt, verifier):
            return _bad_link(request)          # account vanished mid-flow
        service.sessions.revoke_email(record.email)     # a password change logs
        service.remember.revoke_email(record.email)     # every device out
        await service.push_shell_teardown(record.email)  # …and any live shell
        await service.push_vault_reset(record.email)     # a reset destroys the vault
        log.info('password reset completed for %s', record.email)
        raise web.HTTPSeeOther(location='/login?reset=1')

    # ── change password (signed-in self-service; distinct from forgot/reset) ──────

    async def password_page(request: web.Request) -> web.Response:
        """The signed-in change-password page (``GET /password``).

        Current password + new password twice; the browser proves the current
        password over SRP and derives the new verifier locally (no mailbox
        round-trip — that is the *forgot* flow's job). No session → login.

        On ``HX-Request`` it returns a **bare fragment** (form + SRP scripts +
        OOB breadcrumb) so the content shell can swap it straight into the left
        pane; a direct visit gets the full auth page (the no-JS/deep-link form).
        """
        identity = service.session_identity(request)
        if identity is None:
            raise web.HTTPFound('/login')
        template = 'password_fragment.html' if _is_htmx(request) else 'password.html'
        return aiohttp_jinja2.render_template(template, request, {'email': identity[0]})

    # ── forgot (self-service reset entry) ───────────────────────────────────

    async def forgot_page(request: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template('forgot.html', request, {})

    # ── request an invite (unauthenticated intake) ────────────────────────────────

    async def request_invite_page(request: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template('request_invite.html', request, {})

    async def request_invite_submit(request: web.Request) -> web.Response:
        """Queue a prospective collaborator's request; answer generically either way.

        This creates **no** authorization state — only the sudo ``users add`` path
        does. The response is the same whether the request stored, deduped, or was
        dropped (a full queue / bad email), so it leaks neither membership nor
        capacity. The owner notice is best-effort and off the event loop.
        """
        if not service.rate.allow(_client_key(request)):
            return web.Response(status=429, text='rate limited')
        form = await request.post()
        name = sanitize(str(form.get('name', '')), NAME_MAX)
        email = normalize_email(str(form.get('email', '')))
        remarks = sanitize(str(form.get('remarks', '')), REMARKS_MAX, allow_newlines=True)
        if '@' in email and service.requests.submit(name, email, remarks, _client_key(request)):
            await asyncio.to_thread(service.notify_invite_request, name, email, remarks)
            log.info('invite request queued for %s', email)
        else:
            log.warning('invite request not queued (bad email or full queue)')
        return aiohttp_jinja2.render_template('message.html', request, {
            'heading': 'Request received',
            'message': 'Thanks. If the operator approves it, an invitation link will be '
                       'emailed to the address you gave.',
            'show_login': True})

    async def terms_page(request: web.Request) -> web.Response:
        """Standalone view of the Terms of use (the same _terms.html partial the
        registration page embeds).

        On ``HX-Request`` it returns a bare fragment (the terms + OOB breadcrumb)
        for the content shell's left pane; a direct visit gets the full page —
        which carries a back link, being otherwise a dead end: it is the one
        auth-tier page a reader arrives at with nothing to sign in to."""
        if _is_htmx(request):                           # the shell's own crumbs lead back
            return aiohttp_jinja2.render_template('terms_fragment.html', request, {
                'terms_version': service.config.terms_version})
        back_url, back_label = _back_link(request)
        return aiohttp_jinja2.render_template('terms.html', request, {
            'terms_version': service.config.terms_version,
            'back_url': back_url, 'back_label': back_label})

    async def forgot_submit(request: web.Request) -> web.Response:
        if not service.rate.allow(_client_key(request)):
            return web.Response(status=429, text='rate limited')
        form = await request.post()
        email = normalize_email(str(form.get('email', '')))
        user = service.users.get(email) if '@' in email else None
        if user is not None and not user.disabled:
            # Reset does not change the profile (authorizations.json is authoritative);
            # the pending record's profile is informational only.
            token = service.pending.mint(email, service.profile_for(email), 'reset')
            try:
                await asyncio.to_thread(service.mailer.send_invite, email, token, 'reset')
                log.info('reset link sent for %s', email)
            except OSError as exc:             # generic response regardless
                log.warning('reset mail to %s failed: %s', email, exc)
        return aiohttp_jinja2.render_template('message.html', request, {
            'heading': 'Check your mailbox',
            'message': 'If that account exists and is enabled, a reset link is on its way.',
            'show_login': True})

    app.add_routes([
        web.get('/login', login_page),
        web.get('/register', flow_page),
        web.get('/reset', flow_page),
        web.post('/register/otp', flow_otp),
        web.post('/reset/otp', flow_otp),
        web.post('/register/verify', flow_verify),
        web.post('/reset/verify', flow_verify),
        web.post('/register/complete', flow_complete),
        web.post('/reset/complete', flow_complete),
        web.get('/forgot', forgot_page),
        web.post('/forgot', forgot_submit),
        web.get('/request-invite', request_invite_page),
        web.post('/request-invite', request_invite_submit),
        web.get('/password', password_page),
        web.get('/terms', terms_page),
    ])
