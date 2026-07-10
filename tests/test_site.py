#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the content service (Phase 5a/5b): identity from forward_auth headers,
the requires-gate, the full-page-vs-block render contract, the baseline CSP, and
the 5b read routes (solutions grid, problem pages/files, docs, topics, account)
with their canonical trailing-slash redirects.

Uses aiohttp's stdlib test utilities (no extra dep). The authorization policy is
pinned to the packaged template so profiles/permissions are deterministic; the
content routes read this repo's own working tree."""
from __future__ import annotations

import os
import unittest
from pathlib import Path

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.auth.authorizations import DEFAULT_POLICY_FILE
from solver.web.site.app import build_app
from solver.web.site.config import SiteConfig

_READER = {'X-User': 'r@example.com', 'X-Profile': 'reader'}
_ADMIN = {'X-User': 'a@example.com', 'X-Profile': 'admin'}
_HTMX = {'HX-Request': 'true'}


def _config(profile: str = '') -> SiteConfig:
    repo = Path(__file__).resolve().parents[1]
    return SiteConfig(repo_root=repo, static_dir=repo / 'solver/web/content',
                      socket_path=Path('/tmp/unused.sock'), socket_group='',
                      tcp_bind='', serve_static=False, profile=profile)


class ContentServiceTests(AioHTTPTestCase):
    async def get_application(self):
        # Deterministic policy: the bundled ladder (reader/contributor/maintainer/admin).
        os.environ['EULER_AUTHZ_FILE'] = str(DEFAULT_POLICY_FILE)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)
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
        self.assertIn('reader', body)                       # profile pill in header
        self.assertIn('id="content"', body)                 # left pane (§1)
        self.assertIn('id="ws"', body)                      # right pane (§1)
        self.assertIn('&sigmaf;', body)                     # the ς brand glyph
        self.assertIn('/vendor/htmx.min.js', body)          # htmx wired
        self.assertIn('integrity="sha384-', body)           # with SRI

    @unittest_run_loop
    async def test_home_block_for_htmx(self) -> None:
        resp = await self.client.get('/', headers={**_READER, **_HTMX})
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertNotIn('<!DOCTYPE html>', body)           # fragment only
        self.assertNotIn('<nav', body)                      # no chrome
        self.assertNotIn('id="ws"', body)                   # the terminal pane is untouched
        self.assertIn('Project', body)                      # just the content block

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
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertNotIn('unsafe-inline', csp)

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
        self.assertIn('p0042_s0.py', body)                  # the file list

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
        resp = await self.client.get('/docs/user-guide', headers=_READER)
        self.assertEqual(resp.status, 200)
        page = await resp.text()
        self.assertIn('<h1', page)                          # rendered markdown
        self.assertNotIn('href="user-guide.md', page)       # .md cross-links rewired

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
        self.assertIn('/topics/prime-numbers', await resp.text())
        resp = await self.client.get('/topics/prime-numbers', headers=_READER)
        self.assertEqual(resp.status, 200)
        self.assertIn('Eratosthenes', await resp.text())

    @unittest_run_loop
    async def test_account_page(self) -> None:
        resp = await self.client.get('/account', headers=_ADMIN)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('a@example.com', body)
        self.assertIn('users:read', body)                   # the expanded grant set


class PinnedInstanceTests(AioHTTPTestCase):
    """A per-profile instance (EULER_PROFILE set) serves only its own profile —
    the code-side backstop to Caddy's per-profile routing (DD-12)."""

    async def get_application(self):
        os.environ['EULER_AUTHZ_FILE'] = str(DEFAULT_POLICY_FILE)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)
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
