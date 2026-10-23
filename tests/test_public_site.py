#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the public site (docs/package-guide.md § 4): the packaged content
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

from euler_site.cache import build_fingerprint
from euler_site.site.app import build_public_app
from euler_site.site.config import SiteConfig
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


class FingerprintTests(unittest.TestCase):
    def test_any_change_to_the_build_changes_the_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.md').write_text('one', encoding='utf-8')
            before = build_fingerprint(root)
            self.assertEqual(build_fingerprint(root), before, 'stable while nothing changes')
            (root / 'a.md').write_text('two!', encoding='utf-8')
            self.assertNotEqual(build_fingerprint(root), before)


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
            repo_root=self.tree, static_dir=self.tree / 'packages/site/euler_site/content',
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
        self.assertIn('href="/login?next=/"', body)          # …only the way to one, back to here

    @unittest_run_loop
    async def test_a_page_names_its_assets_by_their_bytes(self) -> None:
        body = await (await self.client.get('/')).text()
        self.assertRegex(body, r'href="/assets/site\.css\?v=[0-9a-f]{12}"')
        self.assertRegex(body, r'src="/vendor/htmx\.min\.js\?v=[0-9a-f]{12}"')

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
    async def test_a_page_is_public_and_revalidated(self) -> None:
        resp = await self.client.get('/solutions/0001/')
        self.assertEqual(resp.headers['Cache-Control'], 'public, no-cache')
        self.assertIn('HX-Request', resp.headers['Vary'])
        etag = resp.headers['ETag']
        again = await self.client.get('/solutions/0001/', headers={'If-None-Match': etag})
        self.assertEqual(again.status, 304)
        self.assertEqual(await again.read(), b'')

    @unittest_run_loop
    async def test_a_fragment_and_a_page_are_different_entries(self) -> None:
        page = await self.client.get('/docs/')
        fragment = await self.client.get('/docs/', headers={'HX-Request': 'true'})
        self.assertNotEqual(page.headers['ETag'], fragment.headers['ETag'])
        stale = await self.client.get('/docs/', headers={'HX-Request': 'true', 'If-None-Match': page.headers['ETag']})
        self.assertEqual(stale.status, 200, "a page's tag does not revalidate the fragment")

    @unittest_run_loop
    async def test_an_error_is_not_kept(self) -> None:
        resp = await self.client.get('/solutions/0101/p0101_s0.py')
        self.assertEqual(resp.status, 404)
        self.assertEqual(resp.headers['Cache-Control'], 'no-store')
        self.assertNotIn('ETag', resp.headers)

    @unittest_run_loop
    async def test_identity_headers_are_ignored(self) -> None:
        """Whatever a request claims, the public site has no subject: no user menu, no Actions."""
        body = await (await self.client.get('/', headers=_ADMIN)).text()
        self.assertNotIn('a@example.com', body)
        self.assertIn('not signed in', body)


if __name__ == '__main__':
    unittest.main()
