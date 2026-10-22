#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the public site (docs/package-split.md § 3.4): the packaged content
(`scripts/content/stage.py` → euler-content) served by `build_public_app` to visitors who
are not signed in — read routes only, no identity, and no private tree anywhere."""
from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.web.site.app import build_public_app
from solver.web.site.config import SiteConfig
from tests import silence

silence()

_REPO = Path(__file__).resolve().parents[1]
_STAGE = _REPO / 'scripts' / 'content' / 'stage.py'
_ADMIN = {'X-User': 'a@example.com', 'X-Profile': 'admin', 'X-User-Slug': 'u000000'}


def _load_stage() -> ModuleType:
    spec = importlib.util.spec_from_file_location('stage', _STAGE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stage = _load_stage()


class StageTests(unittest.TestCase):
    def test_the_public_roots_hold_nothing_private(self) -> None:
        files = stage.public_files()
        self.assertTrue(files)
        self.assertFalse([f for f in files if 'private' in f.split('/')])

    def test_a_root_that_would_take_in_the_private_tree_is_refused(self) -> None:
        with patch.object(stage, 'PUBLIC', ('solutions/',)), self.assertRaises(SystemExit):
            stage.public_files()

    def test_the_content_version_is_the_codes(self) -> None:
        from solver.version import __version__
        self.assertEqual(stage.version(), __version__)


class PublicSiteTests(AioHTTPTestCase):
    """Against a staged copy of the real public tree — what the wheel would install."""

    tree: Path
    _tmp: tempfile.TemporaryDirectory[str]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._tmp = tempfile.TemporaryDirectory()
        out = Path(cls._tmp.name) / 'content'
        stage.stage(out)
        cls.tree = out / 'euler_content' / 'tree'

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls._tmp.name, ignore_errors=True)
        super().tearDownClass()

    async def get_application(self):  # type: ignore[no-untyped-def]
        return build_public_app(SiteConfig(
            repo_root=self.tree, static_dir=self.tree / 'solver/web/content',
            socket_path=Path('/tmp/unused.sock'), socket_group='', tcp_bind='',
            serve_static=False, profile='', public=True))

    def test_the_tree_has_no_private_solutions(self) -> None:
        self.assertTrue((self.tree / 'solutions' / 'public').is_dir())
        self.assertFalse((self.tree / 'solutions' / 'private').exists())

    @unittest_run_loop
    async def test_a_visitor_can_browse_without_signing_in(self) -> None:
        for path in ('/', '/solutions/', '/solutions/0001/', '/docs/', '/topics/', '/shell'):
            with self.subTest(path=path):
                resp = await self.client.get(path)
                self.assertEqual(resp.status, 200, path)

    @unittest_run_loop
    async def test_the_navigation_is_live_and_the_terminal_is_a_way_in(self) -> None:
        body = await (await self.client.get('/')).text()
        self.assertIn('hx-get="/solutions/"', body)          # the nav is live…
        self.assertNotIn('src="/terminal"', body)             # …there is no terminal…
        self.assertIn('href="/login"', body)                  # …only the way to one

    @unittest_run_loop
    async def test_a_public_solution_file_is_served(self) -> None:
        name = sorted(p.name for p in (self.tree / 'solutions/public/p0001').glob('p0001_s*.py'))[0]
        resp = await self.client.get(f'/solutions/0001/{name}')
        self.assertEqual(resp.status, 200)

    @unittest_run_loop
    async def test_a_private_problems_files_do_not_exist_here(self) -> None:
        resp = await self.client.get('/solutions/0101/p0101_s0.py')
        self.assertEqual(resp.status, 404)
        resp = await self.client.get('/docs/file/solutions/private/p0100_0199/p0101/p0101_s0.py')
        self.assertEqual(resp.status, 404)

    @unittest_run_loop
    async def test_there_is_no_write_terminal_or_account_surface(self) -> None:
        for method, path in (('GET', '/terminal'), ('GET', '/git'), ('GET', '/account'),
                             ('GET', '/edit/solutions/'), ('POST', '/edit/solutions/'),
                             ('GET', '/edit/solutions/0001/p0001_s0.py'),
                             ('DELETE', '/edit/solutions/0001/p0001_s0.py'), ('GET', '/ws')):
            with self.subTest(method=method, path=path):
                resp = await self.client.request(method, path, headers=_ADMIN)
                self.assertIn(resp.status, (404, 405), f'{method} {path}')

    @unittest_run_loop
    async def test_identity_headers_are_ignored(self) -> None:
        """Whatever a request claims, the public site has no subject: no user menu, no Actions."""
        body = await (await self.client.get('/', headers=_ADMIN)).text()
        self.assertNotIn('a@example.com', body)
        self.assertIn('not signed in', body)


if __name__ == '__main__':
    unittest.main()
