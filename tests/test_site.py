#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the content service: identity from forward_auth
headers, the requires-gate, the full-page-vs-block render contract, the baseline
CSP, the 5b read routes (solutions grid, problem pages/files, docs, topics,
account) with their canonical trailing-slash redirects, and the 5d edit routes
(file editor through the 5c gate, delete, the progress editor) —
the writes run against a scratch repo tree, never this checkout.

Uses aiohttp's stdlib test utilities (no extra dep). The authorization policy is
pinned to the local fixture so profiles are deterministic."""
from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.web.site import gitstate
from solver.web.site.app import build_app
from solver.web.site.config import SiteConfig
from tests import silence

silence()   # filter aiohttp's request-key warning the handlers trip

_READER = {'X-User': 'r@example.com', 'X-Profile': 'reader'}
_CONTRIBUTOR = {'X-User': 'c@example.com', 'X-Profile': 'contributor'}
_MAINTAINER = {'X-User': 'm@example.com', 'X-Profile': 'maintainer'}
_ADMIN = {'X-User': 'a@example.com', 'X-Profile': 'admin'}
_HTMX = {'HX-Request': 'true'}


#: A deterministic policy for tests: the ladder plus an empty users map. Tests must
#: point EULER_AUTHZ_FILE at this — a host with the real /etc/euler SoR deployed would
#: otherwise leak its own user map into the run.
_AUTHZ_FIXTURE = Path(__file__).parent / 'fixtures' / 'authorizations.json'


def _config(profile: str = '') -> SiteConfig:
    repo = Path(__file__).resolve().parents[1]
    return SiteConfig(repo_root=repo, static_dir=repo / 'solver/web/content',
                      socket_path=Path('/tmp/unused.sock'), socket_group='',
                      tcp_bind='', serve_static=False, profile=profile)


async def _no_git_read(_repo_root, *, fetch: bool = False):
    """A gitstate.read stand-in: no chip, and — crucially — no I/O.

    The read routes use this checkout as their content library, but the header's git
    chip is not under test and its real read would fetch origin/master over the network
    and unwrap the operator's ~/.euler vault — both forbidden in a unit run. Return the
    no-clone state so the middleware stays entirely local.
    """
    return None


def _stub_gitstate(testcase: unittest.TestCase) -> None:
    """Swap gitstate.read for the no-I/O stand-in for the life of *testcase*."""
    saved = gitstate.read
    gitstate.read = _no_git_read                # type: ignore[assignment]
    testcase.addCleanup(setattr, gitstate, 'read', saved)


class ContentServiceTests(AioHTTPTestCase):
    async def get_application(self):
        # Deterministic policy: the ladder + an empty users map (never the host's SoR).
        os.environ['EULER_AUTHZ_FILE'] = str(_AUTHZ_FIXTURE)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)
        _stub_gitstate(self)                    # the chip's read must not fetch or touch the vault
        return build_app(_config())

    @unittest_run_loop
    async def test_healthz_is_open(self) -> None:
        resp = await self.client.get('/healthz')
        self.assertEqual(resp.status, 200)

    @unittest_run_loop
    async def test_home_full_page_for_reader(self) -> None:
        resp = await self.client.get('/', headers=_READER)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('<!DOCTYPE html>', body)              # full page
        self.assertIn('Project', body)                      # content
        self.assertIn('reader', body)                       # profile pill in the user menu
        self.assertIn('id="content"', body)                 # left pane (§1)
        self.assertIn('id="ws"', body)                      # right pane (§1)…
        self.assertIn('src="/terminal"', body)              # …an iframe (decision 14)
        self.assertIn('e<sup>iπ</sup>', body)               # the identity wordmark
        self.assertIn('id="crumbs"', body)                  # chrome placed in the header
        self.assertIn('id="actions"', body)
        self.assertNotIn('theme-toggle', body)              # dark-only: there is no slider
        self.assertIn('data-term-toggle', body)             # the terminal control, in the user menu
        self.assertIn('/auth/logout', body)                 # the user menu
        self.assertIn('hx-get="/about/license"', body)      # footer → left pane…
        self.assertNotIn('/about/readme', body)             # …without readme
        self.assertNotIn('data-dialog', body)               # no modal, no popup
        self.assertNotIn('data-popup', body)
        self.assertIn('>license</a>', body)                 # label, not "MIT license"
        self.assertIn('hx-get="/account"', body)            # account swaps the pane
        # No "Change password" in the menu: it lives on the account page now (an account
        # thing; the menu is for getting places). The route itself still exists.
        self.assertNotIn('hx-get="/password"', body)
        self.assertIn('/vendor/htmx.min.js', body)          # htmx wired
        self.assertIn('integrity="sha384-', body)           # with SRI

    @unittest_run_loop
    async def test_home_block_for_htmx(self) -> None:
        resp = await self.client.get('/', headers={**_READER, **_HTMX})
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertNotIn('<!DOCTYPE html>', body)           # fragment only
        self.assertNotIn('app-header', body)                # no shell chrome re-render
        self.assertNotIn('id="ws"', body)                   # the terminal pane is untouched
        self.assertIn('Project', body)                      # the content block…
        self.assertIn('hx-swap-oob', body)                  # …plus the OOB header chrome (§6)

    @unittest_run_loop
    async def test_about_pages_for_reader(self) -> None:
        for name, marker in (('readme', 'Project Euler'), ('license', 'MIT License'),
                             ('acknowledgements', 'htmx')):
            resp = await self.client.get(f'/about/{name}', headers=_READER)
            self.assertEqual(resp.status, 200, name)
            self.assertIn(marker, await resp.text())
        resp = await self.client.get('/about/no-such-page', headers=_READER)
        self.assertEqual(resp.status, 404)

    @unittest_run_loop
    async def test_terminal_is_a_standalone_document(self) -> None:
        resp = await self.client.get('/terminal', headers=_READER)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('terminal-doc', body)                  # its own page…
        self.assertNotIn('app-header', body)                 # …not the shell
        self.assertNotIn('id="content"', body)
        resp = await self.client.get('/terminal')            # still gated
        self.assertEqual(resp.status, 401)

    @unittest_run_loop
    async def test_footer_and_account_swap_into_the_pane(self) -> None:
        # htmx fetch of a footer/account route → the #content fragment + OOB chrome
        # The account marker is the ladder, not the word "Account": the page's own
        # heading is the reader's email, and its subject is where they stand on the rungs.
        for path, marker in (('/about/license', 'MIT License'),
                             ('/about/acknowledgements', 'htmx'),
                             ('/account', 'class="ladder"')):
            resp = await self.client.get(path, headers={**_ADMIN, **_HTMX})
            self.assertEqual(resp.status, 200, path)
            body = await resp.text()
            self.assertIn(marker, body, path)
            self.assertNotIn('<!DOCTYPE html>', body, path)  # a fragment, not the shell
            self.assertIn('hx-swap-oob', body, path)         # with the header chrome

    @unittest_run_loop
    async def test_no_profile_is_unauthorized(self) -> None:
        resp = await self.client.get('/')                   # no forward_auth headers
        self.assertEqual(resp.status, 401)

    @unittest_run_loop
    async def test_unknown_profile_is_unauthorized(self) -> None:
        resp = await self.client.get('/', headers={'X-User': 'x', 'X-Profile': 'root'})
        self.assertEqual(resp.status, 401)

    @unittest_run_loop
    async def test_baseline_csp_header(self) -> None:
        resp = await self.client.get('/', headers=_READER)
        csp = resp.headers.get('Content-Security-Policy', '')
        self.assertIn("default-src 'self'", csp)
        # 'self', not 'none': the shell frames its own /terminal (decision 14);
        # cross-origin embedding stays blocked.
        self.assertIn("frame-ancestors 'self'", csp)
        # Scripts stay strict — no inline execution, ever. Styles carry the
        # recorded 'unsafe-inline' exception for MathJax/htmx runtime styles (§4.7).
        self.assertRegex(csp, r"script-src 'self' 'nonce-[^']+'")
        self.assertNotIn("script-src 'self' 'unsafe-inline'", csp)
        self.assertIn("style-src 'self' 'unsafe-inline'", csp)
        self.assertNotIn('unsafe-eval', csp)

    # ── 5b: solutions ────────────────────────────────────────────────────────

    @unittest_run_loop
    async def test_solutions_index_renders_grids(self) -> None:
        resp = await self.client.get('/solutions/', headers=_READER)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('century-grid', body)
        self.assertIn('/solutions/0042/', body)

    @unittest_run_loop
    async def test_slashless_get_301s_to_canonical(self) -> None:
        for path in ('/solutions', '/docs', '/topics', '/solutions/0042'):
            resp = await self.client.get(path, headers=_READER, allow_redirects=False)
            self.assertEqual(resp.status, 301, path)
            self.assertEqual(resp.headers['Location'], path + '/')

    @unittest_run_loop
    async def test_unpadded_problem_number_301s(self) -> None:
        resp = await self.client.get('/solutions/42/', headers=_READER, allow_redirects=False)
        self.assertEqual(resp.status, 301)
        self.assertEqual(resp.headers['Location'], '/solutions/0042/')

    @unittest_run_loop
    async def test_problem_page(self) -> None:
        resp = await self.client.get('/solutions/0042/', headers=_READER)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('Problem 42', body)
        self.assertIn('triangle', body)                     # the cached statement
        self.assertIn('p0042_s0.py', body)                  # the file flow
        self.assertIn('test-cases', body)                   # test cases as a table (§7)
        self.assertLess(body.index('test-cases'), body.index('file-flow'))
        self.assertLess(body.index('class="results"'), body.index('file-flow'))

    @unittest_run_loop
    async def test_problem_page_tags_and_topics(self) -> None:
        """A: the header chip row, facet-classed, each chip linking to its tag page.
        B: the workbench panel with per-index techniques and a curated topic card."""
        body = await (await self.client.get('/solutions/0007/', headers=_READER)).text()
        # A — header chips
        self.assertIn('class="tagbar"', body)
        self.assertIn('tag-chip domain', body)
        self.assertIn('tag-chip takeaway', body)
        self.assertIn('href="/topics/technique/sieve-of-eratosthenes"', body)
        # B — workbench panel: per-index technique row + curated topic (not a per-tag skeleton)
        self.assertIn('Tags &amp; topics', body)
        self.assertIn('<span class="idx">s0</span>', body)
        self.assertIn('/topics/number-theory/primes', body)
        self.assertIn('Generating and testing primes', body)

    @unittest_run_loop
    async def test_problem_page_off_site_links(self) -> None:
        """The meta line links out to the problem and to its directory on GitHub.

        No target/rel here by design — site.js stamps those on *every* off-site
        link (including the ones inside the cached statement, which we do not author).
        """
        resp = await self.client.get('/solutions/0042/', headers=_READER)
        body = await resp.text()
        self.assertIn('https://projecteuler.net/problem=42', body)
        self.assertIn('https://github.com/vikasmunshi/euler/tree/master/'
                      'solutions/public/p0042', body)

    @unittest_run_loop
    async def test_problem_file_view_and_traversal_guard(self) -> None:
        resp = await self.client.get('/solutions/0042/p0042_s0.py', headers=_READER)
        self.assertEqual(resp.status, 200)
        self.assertIn('solve', await resp.text())
        for path in ('/solutions/0042/../../keys/enc-key.json',
                     '/solutions/0042/%2e%2e/%2e%2e/keys/enc-key.json',
                     '/solutions/0042/no_such_file.py'):
            resp = await self.client.get(path, headers=_READER)
            self.assertEqual(resp.status, 404, path)

    @unittest_run_loop
    async def test_unknown_problem_404s(self) -> None:
        resp = await self.client.get('/solutions/9999/', headers=_READER)
        self.assertEqual(resp.status, 404)

    # ── 5b: docs · topics · account ──────────────────────────────────────────

    @unittest_run_loop
    async def test_docs_index_and_page(self) -> None:
        resp = await self.client.get('/docs/', headers=_READER)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('/docs/user-guide', body)
        self.assertIn('/docs/ai', body)                     # the composed reference
        # card line 1 = the filename title-cased; line 2 = the markdown title
        self.assertIn('>User Guide<', body)
        self.assertLess(body.index('/docs/commands-index'),  # sorted by filename…
                        body.index('/docs/user-guide'))      # …commands- before user-
        resp = await self.client.get('/docs/user-guide', headers=_READER)
        self.assertEqual(resp.status, 200)
        page = await resp.text()
        self.assertIn('<h1', page)                          # rendered markdown
        self.assertNotIn('href="user-guide.md', page)       # .md cross-links rewired

    @unittest_run_loop
    async def test_header_carries_the_back_arrow(self) -> None:
        """The pane's back arrow sits between Actions and the breadcrumbs, and ships
        as a plain href (site.js turns it into a swap): the browser's own back would
        reload the document and tear down the terminal with it."""
        page = await (await self.client.get('/', headers=_READER)).text()
        self.assertIn('id="nav-back"', page)
        self.assertLess(page.index('id="actions"'), page.index('id="nav-back"'))
        self.assertLess(page.index('id="nav-back"'), page.index('id="crumbs"'))
        self.assertRegex(page, r'id="nav-back"[^>]*href="/"')     # a real link with no JS
        self.assertNotRegex(page, r'id="nav-back"[^>]*hx-get')    # …and never an htmx binding

    @unittest_run_loop
    async def test_docs_index_leads_with_the_readme(self) -> None:
        resp = await self.client.get('/docs/', headers=_READER)
        body = await resp.text()
        self.assertIn('/docs/readme', body)
        self.assertIn('>README<', body)                      # the card's first line
        self.assertLess(body.index('/docs/readme'),          # ahead of the sorted guides
                        body.index('/docs/authorizations'))

    @unittest_run_loop
    async def test_readme_page_links_resolve(self) -> None:
        """The README lives at the repo root and links its neighbours with no `../`
        to mark them: guides route into the pane, readable trees reach the viewer,
        and what the viewer may not serve (LICENSE, Makefile) leaves for GitHub —
        nothing stays a bare relative link, which in the pane would 404."""
        resp = await self.client.get('/docs/readme', headers=_READER)
        self.assertEqual(resp.status, 200)
        page = await resp.text()
        self.assertIn('Project Euler', page)
        self.assertIn('href="/docs/user-guide#7-key-exchange"', page)   # docs/*.md → route
        self.assertIn('href="/docs/"', page)                            # docs/ → the index
        self.assertIn('src="/docs/file/docs/screenshot.png"', page)     # readable tree → viewer
        for name in ('LICENSE', 'Makefile', 'pyproject.toml'):          # not readable → GitHub
            self.assertIn(f'href="https://github.com/vikasmunshi/euler/blob/master/{name}"', page)
        # no repo-relative link survives the rewrite (each would 404 in the pane)
        self.assertNotRegex(page, r'(?:href|src)="(?!\w+:|/|#)')

    @unittest_run_loop
    async def test_readme_images_are_same_origin(self) -> None:
        """Every image the README shows must load under ``img-src 'self' data:``
        (csp.py) — so the badges are vendored in-repo and served by the viewer,
        not fetched from img.shields.io, which the policy blocks outright."""
        page = await (await self.client.get('/docs/readme', headers=_READER)).text()
        sources = re.findall(r'<img[^>]*\bsrc="([^"]+)"', page)
        self.assertTrue(sources)
        for src in sources:
            self.assertRegex(src, r'^(?:/|data:)', f'{src} is not same-origin')
        for src in ('/docs/file/docs/badges/python.svg', '/docs/file/docs/badges/license.svg'):
            resp = await self.client.get(src, headers=_READER)
            self.assertEqual(resp.status, 200, src)
            self.assertEqual(resp.content_type, 'image/svg+xml')

    @unittest_run_loop
    async def test_doc_body_links_rewired_and_boosted(self) -> None:
        # authorizations.md links web-server-guide.md — the .md → route rewrite.
        resp = await self.client.get('/docs/authorizations', headers=_READER)
        page = await resp.text()
        self.assertIn('href="/docs/web-server-guide"', page)
        # gitfilter-guide.md links ../solver/crypto/gitfilter.py — the repo-relative
        # rewrite, which resolves natively on GitHub and via /docs/file/ in the app.
        resp = await self.client.get('/docs/gitfilter-guide', headers=_READER)
        page = await resp.text()
        self.assertIn('href="/docs/file/solver/crypto/gitfilter.py"', page)
        self.assertNotIn('href="../solver', page)            # no dangling repo-relative link
        # internal links are boosted (swap #content), externals are left alone
        self.assertRegex(page, r'href="/docs/file/[^"]+" hx-get="/docs/file/')

    @unittest_run_loop
    async def test_doc_file_view_and_scope(self) -> None:
        # a doc-referenced template file renders in the viewer…
        resp = await self.client.get('/docs/file/solver/templates/new.py', headers=_READER)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('runner', body)                        # the source (escaped) in a code block
        self.assertIn('solve', body)
        self.assertIn('solver/templates/new.py', body)
        # …and a solution file (the solutions object tree — e.g. a topic linking
        # ../solutions/…) and an about file (README) view through the same route…
        for path in ('/docs/file/solutions/public/p0042/p0042_s0.py',
                     '/docs/file/README.md'):
            resp = await self.client.get(path, headers=_READER)
            self.assertEqual(resp.status, 200, path)
        # …but nothing outside the declared-readable trees, and no traversal
        for path in ('/docs/file/solver/config.py',          # solver source, not readable
                     '/docs/file/keys/enc-key.json',         # the key material
                     '/docs/file/solver/templates/../config.py',
                     '/docs/file/../README.md'):
            resp = await self.client.get(path, headers=_READER)
            self.assertEqual(resp.status, 404, path)

    @unittest_run_loop
    async def test_composed_ai_doc(self) -> None:
        resp = await self.client.get('/docs/ai', headers=_READER)
        self.assertEqual(resp.status, 200)
        self.assertIn('claude-euler-solver', await resp.text())

    @unittest_run_loop
    async def test_missing_doc_404s(self) -> None:
        for name in ('no-such-guide', '..%2Fsolver%2Fconfig'):
            resp = await self.client.get(f'/docs/{name}', headers=_READER)
            self.assertEqual(resp.status, 404, name)

    @unittest_run_loop
    async def test_topics_index_and_page(self) -> None:
        resp = await self.client.get('/topics/', headers=_READER)
        self.assertEqual(resp.status, 200)
        self.assertIn('/topics/technique/sieve-of-eratosthenes', await resp.text())
        resp = await self.client.get('/topics/technique/sieve-of-eratosthenes', headers=_READER)
        self.assertEqual(resp.status, 200)
        self.assertIn('Sieve of Eratosthenes', await resp.text())

    @unittest_run_loop
    async def test_topics_nested_folder(self) -> None:
        """A `topics/<folder>/<page>.md` is listed with its folder-qualified name and
        served at the nested route; the folder trail is the card heading."""
        index = await (await self.client.get('/topics/', headers=_READER)).text()
        self.assertIn('/topics/number-theory/primes', index)
        self.assertIn('Number Theory / Primes', index)             # folder-trail heading
        resp = await self.client.get('/topics/number-theory/primes', headers=_READER)
        self.assertEqual(resp.status, 200)
        self.assertIn('Generating and testing primes', await resp.text())
        # a missing nested page is a 404, not a stray match
        missing = await self.client.get('/topics/number-theory/no-such-page', headers=_READER)
        self.assertEqual(missing.status, 404)

    @unittest_run_loop
    async def test_account_page(self) -> None:
        resp = await self.client.get('/account', headers=_ADMIN)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('a@example.com', body)
        self.assertIn('pill-admin', body)                   # the profile rung, the whole story now


_PY_OK = 'def solve() -> str:\n    return str(42)\n'
_PY_BAD = 'def solve() -> str:\n    return str(missing_name)\n'
_PY_FIXABLE = 'import os\n\n\ndef solve() -> str:\n    return str(42)\n'

#: A minimal projecteuler.net progress-page extract the parser accepts.
_PROGRESS_OK = '''<table><tr>
<td class="tooltip problem_solved t_3"><a href="problem=9">9
<span class="tooltiptext_narrow"><div>"Special Pythagorean Triplet"</div>
<div>Difficulty: [30%]</div><div>Completed on Mon, 1 Jan 2024, 00:00</div></span></a></td>
</tr></table>'''


class EditRouteTests(AioHTTPTestCase):
    """The 5d edit routes, against a scratch repo tree (web-server-guide § The site):
    every write passes the 5c gate and answers with a fragment."""

    async def get_application(self):
        os.environ['EULER_AUTHZ_FILE'] = str(_AUTHZ_FIXTURE)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)
        scratch = Path(tempfile.mkdtemp(prefix='euler-site-test-'))
        self.addCleanup(shutil.rmtree, scratch, True)
        self.pdir = scratch / 'solutions' / 'public' / 'p0009'
        self.pdir.mkdir(parents=True)
        (self.pdir / 'p0009_s0.py').write_text(_PY_OK)
        (self.pdir / 'test_cases.json').write_text('[{"category": "main", "answer": 31875000}]')
        (scratch / 'solutions' / 'problems.json').write_text(
            json.dumps({'9': {'title': 'T', 'level': 1, 'pct': 30, 'solved': True, 'date': ''}}))
        self.scratch = scratch
        return build_app(SiteConfig(
            repo_root=scratch, static_dir=scratch, socket_path=Path('/tmp/unused.sock'),
            socket_group='', tcp_bind='', serve_static=False, profile=''))

    # ── file editor ──────────────────────────────────────────────────────────

    @unittest_run_loop
    async def test_editor_page_for_contributor(self) -> None:
        resp = await self.client.get('/edit/solutions/0009/p0009_s0.py', headers=_CONTRIBUTOR)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('editor-buffer', body)
        self.assertIn('return str(42)', body)
        # the textarea is the CodeMirror mount + no-JS submit source (data-cm),
        # tagged with the file language for highlighting
        self.assertIn('data-cm', body)
        self.assertIn('data-language="python"', body)

    @unittest_run_loop
    async def test_editor_gated_from_reader(self) -> None:
        for method, path in (('GET', '/edit/solutions/0009/p0009_s0.py'),
                             ('POST', '/edit/solutions/0009/p0009_s0.py'),
                             ('GET', '/edit/solutions/'),
                             ('POST', '/edit/solutions/')):
            resp = await self.client.request(method, path, headers=_READER)
            self.assertEqual(resp.status, 403, f'{method} {path}')

    @unittest_run_loop
    async def test_editor_404_for_missing_or_uneditable(self) -> None:
        for path in ('/edit/solutions/0009/nope.py',       # editor edits; `new` creates
                     '/edit/solutions/0009/data.txt'):     # not an editable suffix
            (self.pdir / 'data.txt').write_text('x')
            resp = await self.client.get(path, headers=_CONTRIBUTOR)
            self.assertEqual(resp.status, 404, path)

    @unittest_run_loop
    async def test_save_writes_canonical_content(self) -> None:
        resp = await self.client.post('/edit/solutions/0009/p0009_s0.py',
                                      data={'content': _PY_FIXABLE}, headers=_CONTRIBUTOR)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertNotIn('<!DOCTYPE html>', body)                    # writes answer fragments
        self.assertIn('canonicalised', body)                         # submitted ≠ stored note
        self.assertNotIn('import os', (self.pdir / 'p0009_s0.py').read_text())

    @unittest_run_loop
    async def test_rejected_save_leaves_file_untouched(self) -> None:
        resp = await self.client.post('/edit/solutions/0009/p0009_s0.py',
                                      data={'content': _PY_BAD}, headers=_CONTRIBUTOR)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('F821', body)                                  # the gate's diagnostics
        self.assertIn('diag-error', body)
        self.assertEqual((self.pdir / 'p0009_s0.py').read_text(), _PY_OK)

    # ── delete ───────────────────────────────────────────────────────────────

    @unittest_run_loop
    async def test_delete_gated_from_contributor(self) -> None:
        resp = await self.client.delete('/edit/solutions/0009/p0009_s0.py', headers=_CONTRIBUTOR)
        self.assertEqual(resp.status, 403)
        self.assertTrue((self.pdir / 'p0009_s0.py').exists())

    @unittest_run_loop
    async def test_delete_removes_file_and_returns_problem_page(self) -> None:
        resp = await self.client.delete('/edit/solutions/0009/p0009_s0.py', headers=_MAINTAINER)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertNotIn('<!DOCTYPE html>', body)                    # a fragment…
        self.assertIn('Problem 9', body)                             # …of the problem page (§8d)
        self.assertIn('deleted p0009_s0.py', body)
        self.assertNotIn('p0009_s0.py</code>', body)
        self.assertEqual(resp.headers.get('HX-Push-Url'), '/solutions/0009/')
        self.assertFalse((self.pdir / 'p0009_s0.py').exists())

    @unittest_run_loop
    async def test_only_solution_files_are_deletable(self) -> None:
        resp = await self.client.delete('/edit/solutions/0009/test_cases.json', headers=_MAINTAINER)
        self.assertEqual(resp.status, 400)
        self.assertTrue((self.pdir / 'test_cases.json').exists())

    # ── progress editor ──────────────────────────────────────────────────────

    @unittest_run_loop
    async def test_progress_upload_starts_empty(self) -> None:
        (self.scratch / 'solutions' / '.progress.html').write_text('<p>PREVIOUS-UPLOAD</p>')
        resp = await self.client.get('/edit/solutions/', headers=_CONTRIBUTOR)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('projecteuler.net/progress', body)
        self.assertNotIn('PREVIOUS-UPLOAD', body)            # upload-replace, never round-tripped

    @unittest_run_loop
    async def test_progress_slashless_301s(self) -> None:
        resp = await self.client.get('/edit/solutions', headers=_CONTRIBUTOR, allow_redirects=False)
        self.assertEqual(resp.status, 301)
        self.assertEqual(resp.headers['Location'], '/edit/solutions/')

    @unittest_run_loop
    async def test_progress_save_rederives_problems_json(self) -> None:
        resp = await self.client.post('/edit/solutions/', data={'content': _PROGRESS_OK},
                                      headers=_CONTRIBUTOR)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('century-grid', body)                          # the grid block + status
        self.assertIn('saved progress', body)
        derived = json.loads((self.scratch / 'solutions' / 'problems.json').read_text())
        self.assertEqual(derived['9']['pct'], 30)
        self.assertEqual(derived['9']['level'], 3)                   # from the t_3 class
        self.assertTrue(derived['9']['solved'])
        self.assertTrue((self.scratch / 'solutions' / '.progress.html').exists())

    @unittest_run_loop
    async def test_broken_progress_paste_never_lands(self) -> None:
        resp = await self.client.post('/edit/solutions/', data={'content': '<p>not a progress page</p>'},
                                      headers=_CONTRIBUTOR)
        self.assertEqual(resp.status, 200)
        self.assertIn('no problems parsed', await resp.text())
        self.assertFalse((self.scratch / 'solutions' / '.progress.html').exists())

    # ── the Actions menu follows the profile (§6: hiding is UX, the gate is the boundary) ──

    @unittest_run_loop
    async def test_actions_menu_always_present(self) -> None:
        # The problem page carries no actions — the menu is still shown (muted,
        # "No actions here"), never hidden, and never regenerate.
        page = await (await self.client.get('/solutions/0009/', headers=_MAINTAINER)).text()
        self.assertIn('>Actions</summary>', page)
        self.assertIn('No actions here', page)
        self.assertNotIn('Regenerate', page)

    @unittest_run_loop
    async def test_actions_follow_the_profile(self) -> None:
        # file view: Edit needs write, Delete needs delete
        page = await (await self.client.get('/solutions/0009/p0009_s0.py', headers=_READER)).text()
        self.assertNotIn('hx-delete', page)
        page = await (await self.client.get('/solutions/0009/p0009_s0.py', headers=_CONTRIBUTOR)).text()
        self.assertIn('>Edit</a>', page)
        self.assertNotIn('hx-delete', page)
        page = await (await self.client.get('/solutions/0009/p0009_s0.py', headers=_MAINTAINER)).text()
        self.assertIn('hx-delete', page)
        # solutions index: Upload progress is contributor+
        page = await (await self.client.get('/solutions/', headers=_READER)).text()
        self.assertNotIn('Upload progress', page)
        page = await (await self.client.get('/solutions/', headers=_CONTRIBUTOR)).text()
        self.assertIn('Upload progress', page)

    @unittest_run_loop
    async def test_fragment_carries_oob_chrome(self) -> None:
        resp = await self.client.get('/solutions/0009/', headers={**_MAINTAINER, **_HTMX})
        body = await resp.text()
        self.assertNotIn('<!DOCTYPE html>', body)
        self.assertIn('id="crumbs" class="crumbs" aria-label="Breadcrumb" hx-swap-oob="true"', body)
        self.assertIn('id="actions" class="actions" hx-swap-oob="true"', body)
        self.assertIn('0009', body)                          # the crumb leaf


class GitStatusTests(unittest.TestCase):
    """content.git_status: the three porcelain states, and graceful degradation
    outside a git checkout (the deployed posture — .git unreadable)."""

    def test_states_and_degradation(self) -> None:
        import subprocess
        from solver.web.site import content as site_content
        scratch = Path(tempfile.mkdtemp(prefix='euler-git-test-'))
        self.addCleanup(shutil.rmtree, scratch, True)
        pdir = scratch / 'solutions' / 'public' / 'p0009'
        pdir.mkdir(parents=True)
        self.assertEqual(site_content.git_status(scratch, pdir), {})   # no .git → plain
        subprocess.run(['git', 'init', '-q', str(scratch)], check=True)
        subprocess.run(['git', '-C', str(scratch), 'config', 'user.email', 't@t'], check=True)
        subprocess.run(['git', '-C', str(scratch), 'config', 'user.name', 't'], check=True)
        (pdir / 'committed.py').write_text('x = 1\n')
        subprocess.run(['git', '-C', str(scratch), 'add', '-A'], check=True)
        subprocess.run(['git', '-C', str(scratch), 'commit', '-qm', 'init'], check=True)
        (pdir / 'committed.py').write_text('x = 2\n')                  # modified
        (pdir / 'staged.py').write_text('y = 1\n')
        subprocess.run(['git', '-C', str(scratch), 'add', str(pdir / 'staged.py')], check=True)
        (pdir / 'new.py').write_text('z = 1\n')                        # untracked
        states = site_content.git_status(scratch, pdir)
        self.assertEqual(states['committed.py'][0], 'modified')
        self.assertEqual(states['staged.py'][0], 'staged')
        self.assertEqual(states['new.py'][0], 'untracked')


class PinnedInstanceTests(AioHTTPTestCase):
    """A per-profile instance (EULER_PROFILE set) serves only its own profile —
    the code-side backstop to Caddy's per-profile routing."""

    async def get_application(self):
        os.environ['EULER_AUTHZ_FILE'] = str(_AUTHZ_FIXTURE)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)
        _stub_gitstate(self)                    # the chip's read must not fetch or touch the vault
        return build_app(_config(profile='reader'))

    @unittest_run_loop
    async def test_matching_profile_is_served(self) -> None:
        resp = await self.client.get('/', headers=_READER)
        self.assertEqual(resp.status, 200)

    @unittest_run_loop
    async def test_mismatched_profile_is_refused(self) -> None:
        # A maintainer request that reached the reader instance = misrouting/bypass.
        headers = {'X-User': 'm@example.com', 'X-Profile': 'maintainer'}
        resp = await self.client.get('/', headers=headers)
        self.assertEqual(resp.status, 401)


if __name__ == '__main__':
    unittest.main()
