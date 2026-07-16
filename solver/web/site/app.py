#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The content service aiohttp app: identity from forward_auth, routes, gating.

``build_app`` wires the shared CSP middleware (:mod:`solver.web.csp`) and an
**identity middleware** that turns Caddy's trusted ``X-User`` / ``X-Profile``
(set by ``forward_auth``; client-supplied copies are stripped at the edge, §4.1)
into a :class:`~solver.auth.subject.Subject`. Routes gate on it with
:func:`requires`, the web counterpart of the shell's ``@register(requires=…)``
(DD-12): the same ``object:permission`` grants, checked against ``X-Profile``.

The route surface is the contract in ``docs/web-server-guide.md`` § The site: the app shell at
``/`` (four fixed regions filling the viewport), read routes rendering into
``#content`` (full page on a direct visit, fragment + out-of-band header chrome
on htmx — :mod:`solver.web.site.render`), canonical trailing-slash 301s, and the
edit routes — file editor, collection-level progress upload, delete, notes
regenerate — each write passing the save gate (:mod:`solver.web.site.validate`)
and always answering with a fragment. Every handler supplies its breadcrumbs and
Actions (§6); the live terminal (Phase 6) lands on the same spine.
"""
from __future__ import annotations

__all__ = ['build_app', 'add_content_routes', 'install_content',
           'CONFIG_KEY', 'READABLE_KEY', '_MAX_BODY']

import asyncio
import html
import logging
from pathlib import Path
from typing import Any, Awaitable, Callable, TypedDict

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
VIEW = 'reader'

#: Request key under which build_app stores its SiteConfig for handlers.
CONFIG_KEY = web.AppKey('site_config', SiteConfig)

#: Repo-relative roots the ``/docs/file/`` view may serve — the ``docs`` + ``about``
#: object trees (declared-readable, DD-12). Computed once from the policy in build_app.
READABLE_KEY = web.AppKey('readable_roots', list)

#: Ceiling on a request body: the progress-page source (~600 KB today) + headroom;
#: solution files are tiny. aiohttp's 1 MB default is already too close.
_MAX_BODY = 4 * 1024 * 1024

#: Only a bare *solution* file may be deleted — never the statement, notes,
#: test cases, results, or resources.
_DELETABLE_SUFFIXES = frozenset({'.py', '.c'})

#: File suffix → the editor language token (drives CodeMirror highlighting in
#: editor.js). An unlisted suffix edits as plain text.
_EDIT_LANGUAGES = {'.py': 'python', '.c': 'c', '.h': 'c', '.json': 'json', '.html': 'html'}

#: A breadcrumb: (label, href) — href None marks the leaf.
_Crumb = tuple[str, str | None]
_HOME: _Crumb = ('home', '/')


class FileEntry(TypedDict):
    """One file-flow entry: the name plus its best-effort git state (§7)."""

    name: str
    git_css: str
    git_title: str


class Action(TypedDict, total=False):
    """One Actions-menu item (§6): a verb the current page offers."""

    label: str
    kind: str      # 'get' | 'post' | 'delete' | 'submit'
    path: str
    target: str
    swap: str
    confirm: str


def _subject(request: web.Request) -> Subject:
    """The resolved Subject — handlers behind ``requires()`` always have one."""
    subject: Subject | None = request.get(SUBJECT_KEY)
    assert subject is not None
    return subject


def _file_entries(repo_root: Path, sdir: Path) -> list[FileEntry]:
    """The problem's files with their git state (clean files carry empty css)."""
    states = content.git_status(repo_root, sdir)
    return [
        FileEntry(name=name,
                  git_css=states.get(name, ('', ''))[0],
                  git_title=states.get(name, ('', 'committed'))[1])
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
                   auth_method='forward-auth', profile=profile)


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
    """301 a slashless GET to its canonical trailing-slash form (web-server-guide § The site)."""
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


# ── handlers: shell + read ──────────────────────────────────────────────────────────

async def healthz(request: web.Request) -> web.Response:
    """Liveness probe (unauthenticated) — Caddy/monitoring only."""
    return web.Response(text='ok')


@requires(VIEW)
async def terminal(request: web.Request) -> web.StreamResponse:
    """``GET /terminal`` — the right pane's own document (decision 14).

    A standalone page in its own browsing context, framed by the shell at
    ``#ws``: xterm.js + the ``/ws`` client (``/assets/terminal.js``), whose
    ``beforeunload`` guard owns the refresh/close confirmation, and which
    forwards the shell's OSC 5379 ``show``/``edit`` sequences to the shell
    document so *it* swaps the left pane (Phase 6).

    Note the socket is **not** this service's: Caddy routes ``/ws`` to the
    per-profile ``euler-ws`` instance (DD-13). Same origin, so the CSP's
    ``connect-src 'self'`` covers the ``wss:`` upgrade.
    """
    return render(request, 'terminal.html')


@requires(VIEW)
async def home(request: web.Request) -> web.StreamResponse:
    """The landing — the default ``#content`` (full shell on a direct visit)."""
    problems = content.load_problems(request.app[CONFIG_KEY].repo_root)
    solved = sum(1 for p in problems.values() if p.solved)
    return render(request, 'home.html', {
        'solved': solved, 'total': len(problems),
        'crumbs': [('home', None)],
    }, block='content')


def _solutions_context(request: web.Request, status: str = '') -> dict[str, Any]:
    """The `/solutions/` view context: grids, counts, crumbs, and its actions."""
    problems = content.load_problems(request.app[CONFIG_KEY].repo_root)
    actions: list[Action] = []
    if _subject(request).has('contributor'):
        actions.append(Action(label='Upload progress', kind='get', path='/edit/solutions/'))
    return {
        'grids': content.centuries(problems),
        'solved': sum(1 for p in problems.values() if p.solved),
        'total': len(problems),
        'status': status,
        'crumbs': [_HOME, ('solutions', None)],
        'actions': actions,
    }


@requires('reader')
async def solutions_index(request: web.Request) -> web.StreamResponse:
    """``GET /solutions/`` — problems.json as 10×10 century grids, two per row."""
    return render(request, 'solutions.html', _solutions_context(request), block='content')


def _problem_context(request: web.Request, number: int) -> dict[str, Any]:
    """The problem-page context (§7 order): statement · test-cases · results ·
    files · notes — shared by the GET view and the post-delete fragment."""
    config = request.app[CONFIG_KEY]
    repo_root = config.repo_root
    info = content.load_problems(repo_root).get(number)
    sdir = content.solution_dir(repo_root, number)
    if info is None and not sdir.is_dir():
        raise web.HTTPNotFound(text=f'problem {number} not found')

    def read_html(name: str) -> str:
        try:
            return (sdir / name).read_text(encoding='utf-8')
        except OSError:
            return ''

    raw_cases = content.load_json(sdir / 'test_cases.json') or []
    test_cases = [{
        'category': tc.get('category', ''),
        'input': '\n'.join(f'{k} = {v}' for k, v in tc.get('input', {}).items())
                 if isinstance(tc.get('input'), dict) else str(tc.get('input', '')),
        'answer': tc.get('answer', ''),
    } for tc in raw_cases if isinstance(tc, dict)]

    # Off-site sources: the problem as projecteuler.net states it, and this
    # problem's directory in the repo (private problems show as ciphertext there
    # — that is the point of the git filter, not a leak). site.js opens both in a
    # new tab, as it does every off-site link.
    github = (f'{config.github_url}/tree/{config.github_branch}/'
              f'{sdir.relative_to(repo_root).as_posix()}' if config.github_url else '')

    # The problem page carries no page-actions (the notes-regenerate stub was
    # dropped — it could not reach the Claude API from the content tier anyway).
    return {
        'number': number,
        'info': info,
        'euler_url': f'https://projecteuler.net/problem={number}',
        'github_url': github,
        'statement': read_html('statement.html'),
        'notes': read_html('notes.html'),
        'files': _file_entries(repo_root, sdir),
        'test_cases': test_cases,
        'results': content.load_json(sdir / 'results.json') or [],
        'crumbs': [_HOME, ('solutions', '/solutions/'), (f'{number:04d}', None)],
        'actions': [],
    }


@requires('reader')
async def problem_page(request: web.Request) -> web.StreamResponse:
    """``GET /solutions/{n}/`` — the solution_dir rendered (§7 order)."""
    number = _problem_number(request)
    return render(request, 'problem.html', _problem_context(request, number),
                  block='content')


@requires('reader')
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

    subject = _subject(request)
    bare = '/' not in filename
    actions: list[Action] = []
    if bare and target.suffix in EDITABLE_SUFFIXES and subject.has('contributor'):
        actions.append(Action(label='Edit', kind='get',
                              path=f'/edit/solutions/{number:04d}/{filename}'))
    if bare and target.suffix in _DELETABLE_SUFFIXES and subject.has('maintainer'):
        actions.append(Action(label='Delete', kind='delete',
                              path=f'/edit/solutions/{number:04d}/{filename}',
                              confirm=f'Delete {filename}?'))
    return render(request, 'file.html', {
        'number': number,
        'filename': filename,
        'text': text,
        'lines': text.count('\n') + 1,
        'crumbs': [_HOME, ('solutions', '/solutions/'),
                   (f'{number:04d}', f'/solutions/{number:04d}/'), (filename, None)],
        'actions': actions,
    }, block='content')


@requires('reader')
async def docs_index(request: web.Request) -> web.StreamResponse:
    """``GET /docs/`` — the guides index (card grid)."""
    return render(request, 'docs.html', {
        'entries': content.list_docs(request.app[CONFIG_KEY].repo_root),
        'crumbs': [_HOME, ('docs', None)],
    }, block='content')


@requires('reader')
async def doc_file(request: web.Request) -> web.StreamResponse:
    """``GET /docs/file/{path}`` — view a doc-referenced repo file.

    Serves a file under the declared-readable content trees (the ``docs`` +
    ``about`` + ``solutions`` roots) — e.g. ``solver/templates/new.py`` linked
    from a guide, or a ``../solutions/…`` file linked from a topic. Text renders in the viewer;
    other bytes are served raw. Anything outside those trees (or a traversal
    attempt) is 404, so the route can never read the wider ``solver/`` source
    or the key material.
    """
    rel = request.match_info['path']
    config = request.app[CONFIG_KEY]
    target = content.resolve_repo_file(config.repo_root, request.app[READABLE_KEY], rel)
    if target is None:
        raise web.HTTPNotFound(text=f'{html.escape(rel)} is not a viewable file')
    if target.suffix not in content.TEXT_SUFFIXES:
        return web.FileResponse(target)
    try:
        text = target.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return web.FileResponse(target)
    return render(request, 'docfile.html', {
        'path': rel,
        'text': text,
        'lines': text.count('\n') + 1,
        'crumbs': [_HOME, ('docs', '/docs/'), (Path(rel).name, None)],
        'actions': [],
    }, block='content')


@requires('reader')
async def doc_page(request: web.Request) -> web.StreamResponse:
    """``GET /docs/{name}`` — one rendered guide (the file may live outside docs/)."""
    name = request.match_info['name']
    text = content.read_doc(request.app[CONFIG_KEY].repo_root, name)
    if text is None:
        raise web.HTTPNotFound(text=f'no guide called {html.escape(name)}')
    # The README links its neighbours at the repo root (LICENSE, Makefile, …), which
    # the file viewer may not serve: repo_base sends those to GitHub (content.py).
    repo_base = content.README_REPO_BASE if name.startswith('readme') else ''
    return render(request, 'doc.html', {
        'name': name,
        'body': content.render_markdown(text, repo_base=repo_base),
        'crumbs': [_HOME, ('docs', '/docs/'), (name, None)],
    }, block='content')


@requires('reader')
async def topics_index(request: web.Request) -> web.StreamResponse:
    """``GET /topics/`` — the topics index (card grid)."""
    return render(request, 'topics.html', {
        'entries': content.list_topics(request.app[CONFIG_KEY].repo_root),
        'crumbs': [_HOME, ('topics', None)],
    }, block='content')


@requires('reader')
async def topic_page(request: web.Request) -> web.StreamResponse:
    """``GET /topics/{name}`` — one rendered topic page."""
    name = request.match_info['name']
    text = content.read_topic(request.app[CONFIG_KEY].repo_root, name)
    if text is None:
        raise web.HTTPNotFound(text=f'no topic called {html.escape(name)}')
    return render(request, 'topic.html', {
        'name': name,
        'body': content.render_markdown(text, route_base='/topics/'),
        'crumbs': [_HOME, ('topics', '/topics/'), (name, None)],
    }, block='content')


@requires('reader')
async def account(request: web.Request) -> web.StreamResponse:
    """``GET /account`` — the signed-in user + profile (from X-User / X-Profile)."""
    return render(request, 'account.html', {
        'crumbs': [_HOME, ('account', None)],
    }, block='content')


@requires('reader')
async def about_page(request: web.Request) -> web.StreamResponse:
    """``GET /about/{name}`` — a footer page: readme · license · acknowledgements."""
    name = request.match_info['name']
    page = content.read_about(request.app[CONFIG_KEY].repo_root, name)
    if page is None:
        raise web.HTTPNotFound(text=f'no page called {html.escape(name)}')
    title, text, is_markdown = page
    return render(request, 'about.html', {
        'title': title,
        'body': content.render_markdown(text) if is_markdown else '',
        'text': '' if is_markdown else text,
        'crumbs': [_HOME, (name, None)],
    }, block='content')


# ── handlers: edit — every write passes the save gate, every response is a fragment ──

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


def _editor_context(request: web.Request, number: int, filename: str, text: str,
                    status: str = '', ok: bool = True,
                    diagnostics: list[Any] | None = None) -> dict[str, Any]:
    """The file-editor view context, shared by GET / save-ok / save-refused."""
    actions: list[Action] = [Action(label='Save', kind='submit')]
    if Path(filename).suffix in _DELETABLE_SUFFIXES and _subject(request).has('maintainer'):
        actions.append(Action(label='Delete', kind='delete',
                              path=f'/edit/solutions/{number:04d}/{filename}',
                              confirm=f'Delete {filename}?'))
    return {
        'number': number, 'filename': filename, 'text': text,
        'language': _EDIT_LANGUAGES.get(Path(filename).suffix, ''),
        'status': status, 'ok': ok, 'diagnostics': diagnostics or [],
        'crumbs': [_HOME, ('solutions', '/solutions/'),
                   (f'{number:04d}', f'/solutions/{number:04d}/'),
                   (filename, f'/solutions/{number:04d}/{filename}'), ('edit', None)],
        'actions': actions,
    }


@requires('contributor')
async def file_editor(request: web.Request) -> web.StreamResponse:
    """``GET /edit/solutions/{n}/{filename}`` — the code editor for the file."""
    number, filename, target = _editor_target(request)
    text = target.read_text(encoding='utf-8', errors='replace')
    return render(request, 'edit_file.html',
                  _editor_context(request, number, filename, text), block='content')


@requires('contributor')
async def file_save(request: web.Request) -> web.StreamResponse:
    """``POST /edit/solutions/{n}/{filename}`` — gate, write, editor block.

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
        return render(request, 'edit_file.html',
                      _editor_context(request, number, filename, submitted,
                                      status=result.message, ok=False,
                                      diagnostics=list(result.diagnostics)),
                      block='content', fragment=True)
    stored = result.content.decode('utf-8', errors='replace')
    message = result.message
    if stored != submitted:
        message += ' — stored content was canonicalised (shown below)'
    try:
        target.write_bytes(result.content)
    except OSError as exc:
        return render(request, 'edit_file.html',
                      _editor_context(request, number, filename, submitted,
                                      status=f'could not write {filename}: {exc}', ok=False),
                      block='content', fragment=True)
    return render(request, 'edit_file.html',
                  _editor_context(request, number, filename, stored,
                                  status=message, ok=True),
                  block='content', fragment=True)


@requires('maintainer')
async def file_delete(request: web.Request) -> web.StreamResponse:
    """``DELETE /edit/solutions/{n}/{filename}`` — delete → the problem fragment.

    Only a bare ``.py``/``.c`` *solution* file is deletable — never the
    statement, notes, test cases, results, or resources. The response swaps the
    problem page back into ``#content`` (the deleted file has no page to stay on).
    """
    number = _problem_number(request)
    filename = request.match_info['filename']
    sdir = content.solution_dir(request.app[CONFIG_KEY].repo_root, number)
    if Path(filename).suffix not in _DELETABLE_SUFFIXES:
        raise web.HTTPBadRequest(text=f'{filename} is not a deletable solution file')
    (sdir / filename).unlink(missing_ok=True)
    ctx = _problem_context(request, number)
    ctx['status'] = f'deleted {filename}'
    response = render(request, 'problem.html', ctx, block='content', fragment=True)
    # The pane now shows the problem page — move the address bar with it.
    response.headers['HX-Push-Url'] = f'/solutions/{number:04d}/'
    return response


@requires('contributor')
async def progress_editor(request: web.Request) -> web.StreamResponse:
    """``GET /edit/solutions/`` — the progress upload: an **empty** paste buffer.

    Upload-replace, not edit (web-server-guide § The site): the paste supersedes
    ``solutions/.progress.html`` wholesale, so the current content is never
    shipped into the page.
    """
    return render(request, 'edit_progress.html', {
        'status': '', 'ok': True,
        'crumbs': [_HOME, ('solutions', '/solutions/'), ('upload', None)],
        'actions': [Action(label='Save', kind='submit')],
    }, block='content')


@requires('contributor')
async def progress_save(request: web.Request) -> web.StreamResponse:
    """``POST /edit/solutions/`` — save progress → the grid block + status.

    Parse-or-reject: the paste must yield at least one problem before
    ``solutions/.progress.html`` and the re-derived ``problems.json`` are
    written; a broken paste never lands. Success renders the refreshed
    century grids, failure re-renders the upload with the reason.
    """
    repo_root = request.app[CONFIG_KEY].repo_root
    form = await request.post()
    submitted = str(form.get('content', ''))
    ok, message = await asyncio.get_running_loop().run_in_executor(
        None, content.save_progress, repo_root, submitted.encode('utf-8'))
    if not ok:
        return render(request, 'edit_progress.html', {
            'status': message, 'ok': False,
            'crumbs': [_HOME, ('solutions', '/solutions/'), ('upload', None)],
            'actions': [Action(label='Save', kind='submit')],
        }, block='content', fragment=True)
    response = render(request, 'solutions.html', _solutions_context(request, status=message),
                      block='content', fragment=True)
    response.headers['HX-Push-Url'] = '/solutions/'
    return response


# ── app wiring ────────────────────────────────────────────────────────────────────────

def add_content_routes(app: web.Application) -> None:
    """Register the content route surface (the web-server-guide § The site contract) on *app*.

    Shared by :func:`build_app` (the per-profile content service) and the per-user
    service (:mod:`solver.web.user`), which folds these routes together with ``/ws`` —
    so the one route table has a single definition and the two tiers cannot drift.
    """
    app.add_routes([
        web.get('/healthz', healthz),
        web.get('/', home),
        web.get('/terminal', terminal),
        # solutions — canonical with the trailing slash (web-server-guide § The site)
        web.get('/solutions', redirect_slash),
        web.get('/solutions/', solutions_index),
        web.get(r'/solutions/{n:\d+}', redirect_slash),
        web.get(r'/solutions/{n:\d+}/', problem_page),
        web.get(r'/solutions/{n:\d+}/{filename:.+}', problem_file),
        # docs + topics + about
        web.get('/docs', redirect_slash),
        web.get('/docs/', docs_index),
        web.get(r'/docs/file/{path:.+}', doc_file),   # before {name}: a multi-segment view
        web.get(r'/docs/{name}', doc_page),
        web.get('/topics', redirect_slash),
        web.get('/topics/', topics_index),
        web.get(r'/topics/{name}', topic_page),
        web.get(r'/about/{name}', about_page),
        # account
        web.get('/account', account),
        # edit routes (writes always answer with a fragment)
        web.get('/edit/solutions', redirect_slash),
        web.get('/edit/solutions/', progress_editor),
        web.post('/edit/solutions/', progress_save),
        web.get(r'/edit/solutions/{n:\d+}/{filename:[^/]+}', file_editor),
        web.post(r'/edit/solutions/{n:\d+}/{filename:[^/]+}', file_save),
        web.delete(r'/edit/solutions/{n:\d+}/{filename:[^/]+}', file_delete),
    ])


def install_content(app: web.Application, config: SiteConfig, authz: Authorizations) -> None:
    """Wire the content surface (config, readable roots, jinja, routes, static) onto *app*.

    The caller owns app creation + the middleware chain (the identity middleware differs
    between the per-profile and per-user tiers); this installs everything else.
    """
    app[CONFIG_KEY] = config
    # The /docs/file/ view may serve only these content trees — every one a
    # reader-floor read. These used to come from the policy's objects→paths map;
    # with the plain-profile re-simplification they are the service's own roots
    # (structure, not policy).
    app[READABLE_KEY] = ['docs/', 'topics/', 'solver/templates/', 'solutions/',
                         'README.md', 'LICENSE', 'solver/web/content/vendor/README.md']
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(_TEMPLATES)),
                         autoescape=jinja2.select_autoescape(['html', 'xml']))
    add_content_routes(app)
    if config.serve_static:
        # Dev only — in production Caddy serves these from /etc/euler/web-content.
        app.router.add_static('/assets', config.static_dir / 'assets')
        app.router.add_static('/vendor', config.static_dir / 'vendor')


def build_app(config: SiteConfig) -> web.Application:
    """Build the (per-profile) content-service application for one process."""
    authz = Authorizations.load()
    pin = config.profile

    @web.middleware
    async def identity_middleware(request: web.Request, handler: _Handler) -> web.StreamResponse:
        request[SUBJECT_KEY] = _subject_from_headers(request, authz, pin)
        return await handler(request)

    app = web.Application(middlewares=[csp_middleware, identity_middleware],
                          client_max_size=_MAX_BODY)
    install_content(app, config, authz)
    return app
