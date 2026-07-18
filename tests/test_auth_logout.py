#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Logout contract of the auth service's public app: a browser form post (the
site's user-menu Logout, Accept: text/html) is 303-redirected to home, while a
programmatic caller keeps the JSON reply — both clear the session cookies."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.web.auth.app import AuthService, build_public_app
from solver.web.auth.config import AuthConfig

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

    @unittest_run_loop
    async def test_programmatic_post_keeps_json(self) -> None:
        resp = await self.client.post('/auth/logout', allow_redirects=False,
                                      headers={'Accept': 'application/json'})
        self.assertEqual(resp.status, 200)
        self.assertEqual(await resp.json(), {'ok': True})


if __name__ == '__main__':
    unittest.main()
