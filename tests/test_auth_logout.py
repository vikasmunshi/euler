#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Logout contract of the auth service's public app: a browser form post (the
site's user-menu Logout, Accept: text/html) is 303-redirected back to the page it came
from when that page is public, else home, while a programmatic caller keeps the JSON
reply — both clear the session cookies. Plus the `next` allowlist (auth/returnto.py) and
the login page carrying it."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from euler_site.auth.app import AuthService, build_public_app
from euler_site.auth.config import AuthConfig
from euler_site.auth.returnto import return_path

from tests import silence

silence()   # quiet console + filter aiohttp's request-key warning (isolated-run cleanliness)


class LogoutTests(AioHTTPTestCase):
    async def get_application(self):
        state = Path(tempfile.mkdtemp(prefix='euler-auth-test-'))
        self.addCleanup(shutil.rmtree, state, True)
        config = AuthConfig(state_dir=state, socket_path=state / 'auth.sock',
                            admin_socket_path=state / 'admin.sock', socket_group='',
                            admin_socket_group='', admin_token='t',
                            base_url='https://example.test', smtp_relay='127.0.0.1:25',
                            terms_version='test')
        return build_public_app(AuthService(config))

    @unittest_run_loop
    async def test_browser_form_post_redirects_home(self) -> None:
        resp = await self.client.post('/auth/logout', allow_redirects=False,
                                      headers={'Accept': 'text/html,application/xhtml+xml'})
        self.assertEqual(resp.status, 303)
        self.assertEqual(resp.headers['Location'], '/')
        cookies = resp.headers.getall('Set-Cookie', [])
        self.assertTrue(any('Max-Age=0' in c or 'expires' in c.lower() for c in cookies))

    async def logout_from(self, page: str) -> str:
        resp = await self.client.post('/auth/logout', allow_redirects=False, data={'next': page},
                                      headers={'Accept': 'text/html'})
        self.assertEqual(resp.status, 303)
        return resp.headers['Location']

    @unittest_run_loop
    async def test_logout_stays_on_a_public_page(self) -> None:
        self.assertEqual(await self.logout_from('/topics/domain/repeating-decimal'), '/topics/domain/repeating-decimal')
        self.assertEqual(await self.logout_from('/solutions/?status=x'), '/solutions/?status=x')

    @unittest_run_loop
    async def test_logout_from_a_signed_in_only_page_lands_home(self) -> None:
        self.assertEqual(await self.logout_from('/account'), '/')
        self.assertEqual(await self.logout_from('//evil.example/'), '/')

    @unittest_run_loop
    async def test_the_login_page_carries_its_next(self) -> None:
        body = await (await self.client.get('/login?next=/solutions/0042/')).text()
        self.assertIn('data-next="/solutions/0042/"', body)
        body = await (await self.client.get('/login?next=https://evil.example/')).text()
        self.assertIn('data-next="/"', body)

    @unittest_run_loop
    async def test_programmatic_post_keeps_json(self) -> None:
        resp = await self.client.post('/auth/logout', allow_redirects=False,
                                      headers={'Accept': 'application/json'})
        self.assertEqual(resp.status, 200)
        self.assertEqual(await resp.json(), {'ok': True})


class ReturnPathTests(unittest.TestCase):
    def test_the_content_routes_and_home_are_kept(self) -> None:
        for page in ('/', '/solutions/', '/solutions/0042/p0042_s0.py', '/docs/user-guide', '/topics/all',
                     '/topics/domain/x', '/about/license', '/shell', '/docs/?q=1'):
            with self.subTest(page=page):
                self.assertEqual(return_path(page, signed_in=False), page)

    def test_a_session_only_page_only_after_signing_in(self) -> None:
        self.assertEqual(return_path('/account', signed_in=True), '/account')
        self.assertEqual(return_path('/account', signed_in=False), '/')

    def test_anything_else_goes_home(self) -> None:
        for raw in (None, '', 'solutions/', '//evil.example', '/\\evil.example', 'https://evil.example/',
                    '/login', '/auth/logout', '/terminal', '/ws', '/git', '/edit/solutions/', '/internal/status',
                    '/solutionsx', '/topics\\x', '/docs/\nx', '/' + 'a' * 600):
            with self.subTest(raw=raw):
                self.assertEqual(return_path(raw, signed_in=True), '/')


if __name__ == '__main__':
    unittest.main()
