#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The content service aiohttp app: identity from forward_auth, routes, gating.

``build_app`` wires the shared CSP middleware (:mod:`solver.web.csp`) and an
**identity middleware** that turns Caddy's trusted ``X-User`` / ``X-Profile``
(set by ``forward_auth``; client-supplied copies are stripped at the edge, §4.1)
into a :class:`~solver.auth.subject.Subject`. Routes gate on it with
:func:`requires`, the web counterpart of the shell's ``@register(requires=…)``
(DD-12): the same ``object:permission`` grants, checked against ``X-Profile``.

The route surface is the contract in ``docs/site-design.md``: the app shell at
``/`` (four regions: header · ``#content`` · ``#ws`` · footer), the 5b read routes
rendering into ``#content`` (full page on a direct visit, fragment on htmx —
:mod:`solver.web.site.render`), and the canonical trailing-slash 301s. The edit
routes (5c/5d) and the live terminal (Phase 6) land on the same spine.
"""
from __future__ import annotations

__all__ = ['build_app']

import html
import json
import logging
from pathlib import Path
from typing import Awaitable, Callable

import aiohttp_jinja2
import jinja2
from aiohttp import web

from solver.auth import Authorizations, Subject, slugify
from solver.web.csp import csp_middleware
from solver.web.site import content
from solver.web.site.config import SiteConfig
from solver.web.site.render import SUBJECT_KEY, render

log = logging.getLogger('euler-content')

_TEMPLATES = Path(__file__).resolve().parent / 'templates'
_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]

#: The capability every authenticated profile holds — "may view the site".
VIEW = 'web-content:read'

#: Request key under which build_app stores its SiteConfig for handlers.
CONFIG_KEY = web.AppKey('site_config', SiteConfig)


def _subject_from_headers(request: web.Request, authz: Authorizations,
                          pin: str = '') -> Subject | None:
    """Build the request's Subject from the forward_auth headers, or None.

    Caddy guarantees these headers on every routed request (and strips any
    client-supplied copies). A missing/unknown profile yields None — the
    identity middleware then answers 401, since only Caddy should reach us.

    *pin* is this instance's own profile (``EULER_PROFILE``, DD-12): when set, a
    request whose ``X-Profile`` differs is refused (None). Caddy routes each
    profile to its own per-profile uid's socket, so a mismatch means misrouting
    or a bypass — the code-side backstop to the OS per-profile boundary.
    """
    user = request.headers.get('X-User', '').strip()
    profile = request.headers.get('X-Profile', '').strip()
    if not profile or profile not in authz.known_profiles():
        return None
    if pin and profile != pin:
        return None
    return Subject(user=user, slug=slugify(user or profile), channel='web',
                   auth_method='forward-auth', profile=profile,
                   permissions=authz.permissions_for(profile))


def requires(capability: str) -> Callable[[_Handler], _Handler]:
    """Gate a handler on *capability* against the request's Subject (DD-12).

    401 when there is no subject (an unauthenticated caller that bypassed Caddy);
    403 when the subject lacks the grant. Mirrors the shell decorator's contract.
    """

    def _wrap(handler: _Handler) -> _Handler:
        async def _guarded(request: web.Request) -> web.StreamResponse:
            subject: Subject | None = request.get(SUBJECT_KEY)
            if subject is None:
                raise web.HTTPUnauthorized(text='authentication required')
            if not subject.has(capability):
                raise web.HTTPForbidden(text=f'requires {capability}')
            return await handler(request)

        return _guarded

    return _wrap


# ── path helpers ─────────────────────────────────────────────────────────────────────

async def redirect_slash(request: web.Request) -> web.StreamResponse:
    """301 a slashless GET to its canonical trailing-slash form (site-design §6)."""
    location = request.rel_url.path + '/'
    if request.rel_url.query_string:
        location += '?' + request.rel_url.query_string
    raise web.HTTPMovedPermanently(location=location)


def _problem_number(request: web.Request) -> int:
    """The route's problem number; 301s a non-zero-padded form to the canonical
    ``NNNN`` (one URL per view), 404s an out-of-range number."""
    raw = request.match_info['n']
    number = int(raw)
    if not 0 < number < 10000:
        raise web.HTTPNotFound(text=f'problem {raw} not found')
    if raw != f'{number:04d}':
        tail = request.match_info.get('filename', '')
        location = f'/solutions/{number:04d}/{tail}'
        raise web.HTTPMovedPermanently(location=location)
    return number


# ── handlers ────────────────────────────────────────────────────────────────────────

async def healthz(request: web.Request) -> web.Response:
    """Liveness probe (unauthenticated) — Caddy/monitoring only."""
    return web.Response(text='ok')


@requires(VIEW)
async def home(request: web.Request) -> web.StreamResponse:
    """The landing — the default ``#content`` (full shell on a direct visit)."""
    problems = content.load_problems(request.app[CONFIG_KEY].repo_root)
    solved = sum(1 for p in problems.values() if p.solved)
    return render(request, 'home.html', {'solved': solved, 'total': len(problems)},
                  block='content')


@requires('solutions:read')
async def solutions_index(request: web.Request) -> web.StreamResponse:
    """``GET /solutions/`` — problems.json as 10×10 century grids + summary."""
    problems = content.load_problems(request.app[CONFIG_KEY].repo_root)
    grids = content.centuries(problems)
    solved = sum(1 for p in problems.values() if p.solved)
    return render(request, 'solutions.html',
                  {'grids': grids, 'solved': solved, 'total': len(problems)},
                  block='content')


@requires('solutions:read')
async def problem_page(request: web.Request) -> web.StreamResponse:
    """``GET /solutions/{n}/`` — the solution_dir rendered: statement, files,
    test cases, results, notes."""
    number = _problem_number(request)
    repo_root = request.app[CONFIG_KEY].repo_root
    info = content.load_problems(repo_root).get(number)
    sdir = content.solution_dir(repo_root, number)
    if info is None and not sdir.is_dir():
        raise web.HTTPNotFound(text=f'problem {number} not found')

    def read_html(name: str) -> str:
        try:
            return (sdir / name).read_text(encoding='utf-8')
        except OSError:
            return ''

    def pretty(name: str) -> str:
        data = content.load_json(sdir / name)
        return json.dumps(data, indent=2, ensure_ascii=False) if data is not None else ''

    return render(request, 'problem.html', {
        'number': number,
        'info': info,
        'statement': read_html('statement.html'),
        'notes': read_html('notes.html'),
        'files': content.problem_files(sdir),
        'test_cases': pretty('test_cases.json'),
        'results': content.load_json(sdir / 'results.json') or [],
    }, block='content')


@requires('solutions:read')
async def problem_file(request: web.Request) -> web.StreamResponse:
    """``GET /solutions/{n}/{filename}`` — one problem file: source rendered in the
    viewer, anything non-text (statement resources: images, data) as raw bytes."""
    number = _problem_number(request)
    filename = request.match_info['filename']
    sdir = content.solution_dir(request.app[CONFIG_KEY].repo_root, number)
    target = content.resolve_file(sdir, filename)
    if target is None:
        raise web.HTTPNotFound(text=f'{filename} not found for problem {number}')
    if target.suffix not in content.TEXT_SUFFIXES:
        return web.FileResponse(target)
    try:
        text = target.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return web.FileResponse(target)
    return render(request, 'file.html', {
        'number': number,
        'filename': filename,
        'text': text,
        'lines': text.count('\n') + 1,
    }, block='content')


@requires('docs:read')
async def docs_index(request: web.Request) -> web.StreamResponse:
    """``GET /docs/`` — the guides index (docs/*.md + the composed `ai` reference)."""
    return render(request, 'docs.html',
                  {'entries': content.list_docs(request.app[CONFIG_KEY].repo_root)},
                  block='content')


@requires('docs:read')
async def doc_page(request: web.Request) -> web.StreamResponse:
    """``GET /docs/{name}`` — one rendered guide (the file may live outside docs/)."""
    name = request.match_info['name']
    text = content.read_doc(request.app[CONFIG_KEY].repo_root, name)
    if text is None:
        raise web.HTTPNotFound(text=f'no guide called {html.escape(name)}')
    return render(request, 'doc.html', {
        'name': name,
        'body': content.render_markdown(text),
    }, block='content')


@requires('docs:read')
async def topics_index(request: web.Request) -> web.StreamResponse:
    """``GET /topics/`` — the topics index (blog-style writeups)."""
    return render(request, 'topics.html',
                  {'entries': content.list_topics(request.app[CONFIG_KEY].repo_root)},
                  block='content')


@requires('docs:read')
async def topic_page(request: web.Request) -> web.StreamResponse:
    """``GET /topics/{name}`` — one rendered topic page."""
    name = request.match_info['name']
    text = content.read_topic(request.app[CONFIG_KEY].repo_root, name)
    if text is None:
        raise web.HTTPNotFound(text=f'no topic called {html.escape(name)}')
    return render(request, 'topic.html', {
        'name': name,
        'body': content.render_markdown(text, route_base='/topics/'),
    }, block='content')


@requires('users:read')
async def account(request: web.Request) -> web.StreamResponse:
    """``GET /account`` — the signed-in user + profile (from X-User / X-Profile)."""
    return render(request, 'account.html', block='content')


# ── app wiring ────────────────────────────────────────────────────────────────────────

def build_app(config: SiteConfig) -> web.Application:
    """Build the content-service application for one process."""
    authz = Authorizations.load()
    pin = config.profile

    @web.middleware
    async def identity_middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
        request[SUBJECT_KEY] = _subject_from_headers(request, authz, pin)
        return await handler(request)

    app = web.Application(middlewares=[csp_middleware, identity_middleware])
    app[CONFIG_KEY] = config
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(_TEMPLATES)),
                         autoescape=jinja2.select_autoescape(['html', 'xml']))
    app.add_routes([
        web.get('/healthz', healthz),
        web.get('/', home),
        # solutions — canonical with the trailing slash (site-design §6)
        web.get('/solutions', redirect_slash),
        web.get('/solutions/', solutions_index),
        web.get(r'/solutions/{n:\d+}', redirect_slash),
        web.get(r'/solutions/{n:\d+}/', problem_page),
        web.get(r'/solutions/{n:\d+}/{filename:.+}', problem_file),
        # docs + topics
        web.get('/docs', redirect_slash),
        web.get('/docs/', docs_index),
        web.get(r'/docs/{name}', doc_page),
        web.get('/topics', redirect_slash),
        web.get('/topics/', topics_index),
        web.get(r'/topics/{name}', topic_page),
        # account
        web.get('/account', account),
    ])
    if config.serve_static:
        # Dev only — in production Caddy serves these from /etc/euler/web-content.
        app.router.add_static('/assets', config.static_dir / 'assets')
        app.router.add_static('/vendor', config.static_dir / 'vendor')
    return app
