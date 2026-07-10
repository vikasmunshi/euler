#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the content service (Phase 5a): identity from forward_auth headers,
the requires-gate, the full-page-vs-block render contract, and the baseline CSP.

Uses aiohttp's stdlib test utilities (no extra dep). The authorization policy is
pinned to the packaged template so profiles/permissions are deterministic."""
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
        self.assertIn('reader', body)                       # profile pill in nav
        self.assertIn('/vendor/htmx.min.js', body)          # htmx wired
        self.assertIn('integrity="sha384-', body)           # with SRI

    @unittest_run_loop
    async def test_home_block_for_htmx(self) -> None:
        resp = await self.client.get('/', headers={**_READER, 'HX-Request': 'true'})
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertNotIn('<!DOCTYPE html>', body)           # fragment only
        self.assertNotIn('<nav', body)                      # no chrome
        self.assertIn('Project', body)                      # just the main block

    @unittest_run_loop
    async def test_shell_placeholder_renders(self) -> None:
        resp = await self.client.get('/shell', headers=_ADMIN)
        self.assertEqual(resp.status, 200)
        self.assertIn('Phase 6', await resp.text())

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
