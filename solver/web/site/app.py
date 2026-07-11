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
:mod:`solver.web.site.render`), the canonical trailing-slash 301s, and the 5d
edit routes — file editor, collection-level progress editor, delete, notes
regenerate — each write passing the 5c gate (:mod:`solver.web.site.validate`)
and always answering with a fragment. The live terminal (Phase 6) lands on the
same spine.
"""
from __future__ import annotations

__all__ = ['build_app']

import asyncio
import html
import json
import logging
from pathlib import Path
from typing import Awaitable, Callable, TypedDict

import aiohttp_jinja2
import jinja2
from aiohttp import web

from solver.auth import Authorizations, Subject, slugify
from solver.web.csp import csp_middleware
from solver.web.site import content
from solver.web.site.config import SiteConfig
from solver.web.site.render import SUBJECT_KEY, render
from solver.web.site.validate import EDITABLE_SUFFIXES, validate

log = logging.getLogger('euler-content')

_TEMPLATES = Path(__file__).resolve().parent / 'templates'
_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]

#: The capability every authenticated profile holds — "may view the site".
VIEW = 'web-content:read'

#: Request key under which build_app stores its SiteConfig for handlers.
CONFIG_KEY = web.AppKey('site_config', SiteConfig)

#: Ceiling on a request body: the progress-page source (~600 KB today) + headroom;
#: solution files are tiny. aiohttp's 1 MB default is already too close.
_MAX_BODY = 4 * 1024 * 1024

#: Only a bare *solution* file may be deleted — never the statement, notes,
#: test cases, results, or resources (old-app parity).
_DELETABLE_SUFFIXES = frozenset({'.py', '.c'})


class FileEntry(TypedDict):
    """One file-list row: the name plus the affordances the templates gate on."""

    name: str
    editable: bool
    deletable: bool


def _file_entries(sdir: Path) -> list[FileEntry]:
    """The problem's files with their per-file edit/delete affordances.

    Only a bare (top-level) file with an editable suffix opens in the editor;
    nested resources are view-only.
    """
    return [
        FileEntry(name=name,
                  editable='/' not in name and Path(name).suffix in EDITABLE_SUFFIXES,
                  deletable='/' not in name and Path(name).suffix in _DELETABLE_SUFFIXES)
        for name in content.problem_files(sdir)
    ]


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
    """The route's problem number; a GET 301s a non-zero-padded form to the
    canonical ``NNNN`` (one URL per view — writes just accept the number),
    and an out-of-range number is 404."""
    raw = request.match_info['n']
    number = int(raw)
    if not 0 < number < 10000:
        raise web.HTTPNotFound(text=f'problem {raw} not found')
    if request.method == 'GET' and raw != f'{number:04d}':
        location = request.rel_url.path.replace(f'/{raw}/', f'/{number:04d}/', 1)
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
        'files': _file_entries(sdir),
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
        'editable': '/' not in filename and target.suffix in EDITABLE_SUFFIXES,
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


# ── 5d: edit routes — every write passes the 5c gate, every response is a fragment ──

def _editor_target(request: web.Request) -> tuple[int, str, Path]:
    """Resolve an ``/edit/solutions/{n}/{filename}`` route to its on-disk file.

    The route pattern keeps *filename* bare (no ``/``); here it must also carry
    an editable suffix and already exist — the editor edits, `new` creates.
    """
    number = _problem_number(request)
    filename = request.match_info['filename']
    sdir = content.solution_dir(request.app[CONFIG_KEY].repo_root, number)
    target = sdir / filename
    if Path(filename).suffix not in EDITABLE_SUFFIXES or not target.is_file():
        raise web.HTTPNotFound(text=f'{filename} is not an editable file of problem {number}')
    return number, filename, target


@requires('solutions:write')
async def file_editor(request: web.Request) -> web.StreamResponse:
    """``GET /edit/solutions/{n}/{filename}`` — the code editor for the file."""
    number, filename, target = _editor_target(request)
    return render(request, 'edit_file.html', {
        'number': number,
        'filename': filename,
        'text': target.read_text(encoding='utf-8', errors='replace'),
        'status': '', 'ok': True, 'diagnostics': [],
    }, block='content')


@requires('solutions:write')
async def file_save(request: web.Request) -> web.StreamResponse:
    """``POST /edit/solutions/{n}/{filename}`` — gate (5c), write, editor block.

    The submission runs :func:`~solver.web.site.validate.validate`; what lands
    on disk — and returns in the editor buffer — is the gate's *canonical*
    content (auto-fixed / re-indented / sanitised), so the buffer always shows
    exactly what is stored. A refusal returns the submission unmodified with
    the gate's diagnostics; nothing is written.
    """
    number, filename, target = _editor_target(request)
    form = await request.post()
    submitted = str(form.get('content', ''))
    result = await asyncio.get_running_loop().run_in_executor(
        None, validate, filename, submitted.encode('utf-8'),
        request.app[CONFIG_KEY].repo_root)
    if not result.ok:
        return render(request, 'edit_file.html', {
            'number': number, 'filename': filename, 'text': submitted,
            'status': result.message, 'ok': False, 'diagnostics': result.diagnostics,
        }, block='content', fragment=True)
    stored = result.content.decode('utf-8', errors='replace')
    message = result.message
    if stored != submitted:
        message += ' — stored content was canonicalised (shown below)'
    try:
        target.write_bytes(result.content)
    except OSError as exc:
        return render(request, 'edit_file.html', {
            'number': number, 'filename': filename, 'text': submitted,
            'status': f'could not write {filename}: {exc}', 'ok': False, 'diagnostics': [],
        }, block='content', fragment=True)
    return render(request, 'edit_file.html', {
        'number': number, 'filename': filename, 'text': stored,
        'status': message, 'ok': True, 'diagnostics': [],
    }, block='content', fragment=True)


@requires('solutions:delete')
async def file_delete(request: web.Request) -> web.StreamResponse:
    """``DELETE /edit/solutions/{n}/{filename}`` — delete → the file-list block.

    Only a bare ``.py``/``.c`` *solution* file is deletable — never the
    statement, notes, test cases, results, or resources.
    """
    number = _problem_number(request)
    filename = request.match_info['filename']
    sdir = content.solution_dir(request.app[CONFIG_KEY].repo_root, number)
    if Path(filename).suffix not in _DELETABLE_SUFFIXES:
        raise web.HTTPBadRequest(text=f'{filename} is not a deletable solution file')
    (sdir / filename).unlink(missing_ok=True)
    return render(request, '_files.html', {
        'number': number,
        'files': _file_entries(sdir),
        'status': f'deleted {filename}',
    })


@requires('solutions:execute')
async def progress_editor(request: web.Request) -> web.StreamResponse:
    """``GET /edit/solutions/`` — the collection-level progress editor."""
    source = content.read_progress(request.app[CONFIG_KEY].repo_root)
    return render(request, 'edit_progress.html', {
        'source': source, 'status': '', 'ok': True,
    }, block='content')


@requires('solutions:execute')
async def progress_save(request: web.Request) -> web.StreamResponse:
    """``POST /edit/solutions/`` — save progress → the grid block + status.

    Parse-or-reject (5c semantics): the paste must yield at least one problem
    before ``solutions/.progress.html`` and the re-derived ``problems.json``
    are written; a broken paste never lands. Success renders the refreshed
    century grids, failure re-renders the editor with the reason.
    """
    repo_root = request.app[CONFIG_KEY].repo_root
    form = await request.post()
    submitted = str(form.get('content', ''))
    ok, message = await asyncio.get_running_loop().run_in_executor(
        None, content.save_progress, repo_root, submitted.encode('utf-8'))
    if not ok:
        return render(request, 'edit_progress.html', {
            'source': submitted, 'status': message, 'ok': False,
        }, block='content', fragment=True)
    problems = content.load_problems(repo_root)
    return render(request, 'solutions.html', {
        'grids': content.centuries(problems),
        'solved': sum(1 for p in problems.values() if p.solved),
        'total': len(problems),
        'status': message,
    }, block='content', fragment=True)


@requires('ai:execute')
async def notes_regenerate(request: web.Request) -> web.StreamResponse:
    """``POST /solutions/{n}/notes/regenerate`` — AI-regenerate → the notes block.

    The content tier deliberately cannot reach the Claude API (no key on the
    service uid, no egress off the Squid allowlist, no ``ai`` extra in the
    system venv — the AR-1/AR-2 containment), so this returns the notes block
    with a pointer to the shell path until a brokered backend exists.
    """
    number = _problem_number(request)
    sdir = content.solution_dir(request.app[CONFIG_KEY].repo_root, number)
    try:
        notes = (sdir / 'notes.html').read_text(encoding='utf-8')
    except OSError:
        notes = ''
    return render(request, '_notes.html', {
        'number': number, 'notes': notes,
        'status': ('AI regeneration is not wired to the content service — run '
                   f'claude-api docs {number} in the solver shell'),
        'ok': False,
    })


# ── app wiring ────────────────────────────────────────────────────────────────────────

def build_app(config: SiteConfig) -> web.Application:
    """Build the content-service application for one process."""
    authz = Authorizations.load()
    pin = config.profile

    @web.middleware
    async def identity_middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
        request[SUBJECT_KEY] = _subject_from_headers(request, authz, pin)
        return await handler(request)

    app = web.Application(middlewares=[csp_middleware, identity_middleware],
                          client_max_size=_MAX_BODY)
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
        web.post(r'/solutions/{n:\d+}/notes/regenerate', notes_regenerate),
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
        # 5d — edit routes (writes always answer with a fragment)
        web.get('/edit/solutions', redirect_slash),
        web.get('/edit/solutions/', progress_editor),
        web.post('/edit/solutions/', progress_save),
        web.get(r'/edit/solutions/{n:\d+}/{filename:[^/]+}', file_editor),
        web.post(r'/edit/solutions/{n:\d+}/{filename:[^/]+}', file_save),
        web.delete(r'/edit/solutions/{n:\d+}/{filename:[^/]+}', file_delete),
    ])
    if config.serve_static:
        # Dev only — in production Caddy serves these from /etc/euler/web-content.
        app.router.add_static('/assets', config.static_dir / 'assets')
        app.router.add_static('/vendor', config.static_dir / 'vendor')
    return app
