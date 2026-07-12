#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Every auth-tier page renders (DD-7), and the terms page's way back out.

The plain "does it render" half is the point: these pages all extend base.html,
so a mistake in the shared template breaks the whole signed-out tier at once —
as a footer reading ``request.path_qs`` did, aiohttp_jinja2 having no request in
the template context until the app registers its request processor. Rendering
each page through the real app is what catches that; a bare Jinja render with a
hand-made context does not.

The other half is the back link the standalone /terms carries (Referrer-Policy is
no-referrer, so the linking page names itself in ``?back=``): it must return a
reader to our own pages only, and never anywhere else."""
from __future__ import annotations

import re
import shutil
import tempfile
import unittest
from pathlib import Path

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.web.auth import policy
from solver.web.auth.app import AuthService, build_public_app
from solver.web.auth.config import AuthConfig

_EMAIL = 'user@example.com'

#: (path, a string the rendered page must contain) — every GET a signed-out
#: visitor can reach, each one an extension of base.html.
_PAGES = [
    ('/login', 'Sign in'),
    ('/login?reset=1', 'Password updated'),                  # the flash banners
    ('/login?registered=1', 'Registration complete'),
    ('/forgot', 'email'),
    ('/terms', 'Terms of use'),
    ('/register?token=bogus', 'This link is not valid'),     # the generic bad-link page
    ('/reset?token=bogus', 'This link is not valid'),
]


def _back_link(body: str) -> tuple[str, str] | None:
    """The (href, label) of the page's back link, or None when it carries none."""
    match = re.search(r'<a class="back-link" href="([^"]+)">[^<]*?&nbsp;([^<]+)</a>', body)
    return (match.group(1), match.group(2).strip()) if match else None


class AuthPageTests(AioHTTPTestCase):
    async def get_application(self):
        state = Path(tempfile.mkdtemp(prefix='euler-auth-pages-'))
        self.addCleanup(shutil.rmtree, state, True)
        config = AuthConfig(state_dir=state, socket_path=state / 'auth.sock',
                            admin_socket_path=state / 'admin.sock', socket_group='',
                            admin_socket_group='', admin_token='t',
                            base_url='https://example.test', smtp_relay='127.0.0.1:25',
                            terms_version='test')
        self.service = AuthService(config)
        return build_public_app(self.service)

    async def _get(self, path: str, **kwargs) -> tuple[int, str]:
        resp = await self.client.get(path, **kwargs)
        return resp.status, await resp.text()

    # ── the pages render ──────────────────────────────────────────────────────────

    @unittest_run_loop
    async def test_every_signed_out_page_renders(self) -> None:
        for path, expected in _PAGES:
            with self.subTest(path=path):
                status, body = await self._get(path)
                self.assertEqual(status, 200)
                self.assertIn(expected, body)
                self.assertIn('</html>', body)               # a whole page, not a fragment

    @unittest_run_loop
    async def test_invite_token_renders_the_terms_stage(self) -> None:
        token = self.service.pending.mint(_EMAIL, 'reader', 'register')
        status, body = await self._get(f'/register?token={token}')
        self.assertEqual(status, 200)
        self.assertIn('I have read and accept these Terms of use', body)
        self.assertIn(_EMAIL, body)

    @unittest_run_loop
    async def test_change_password_page_needs_a_session(self) -> None:
        resp = await self.client.get('/password', allow_redirects=False)
        self.assertEqual(resp.status, 302)
        self.assertEqual(resp.headers['Location'], '/login')
        session = self.service.sessions.create(_EMAIL, 'reader')
        status, body = await self._get('/password',
                                       cookies={policy.SESSION_COOKIE: session})
        self.assertEqual(status, 200)
        self.assertIn('</html>', body)

    # ── the footer names the page it is on, so /terms can send the reader back ────

    @unittest_run_loop
    async def test_footer_carries_the_current_path(self) -> None:
        for path, back in [('/login', '/login'), ('/forgot', '/forgot'),
                           ('/login?reset=1', '/login%3Freset%3D1')]:
            with self.subTest(path=path):
                _, body = await self._get(path)
                self.assertIn(f'<a href="/terms?back={back}">terms of use</a>', body)

    @unittest_run_loop
    async def test_terms_page_does_not_link_itself(self) -> None:
        _, body = await self._get('/terms')
        self.assertNotIn('terms of use</a>', body)           # the footer's self-link is dropped

    # ── the back link: our own pages, and nowhere else ────────────────────────────

    @unittest_run_loop
    async def test_back_link_returns_to_the_linking_page(self) -> None:
        cases = [
            ('/terms?back=/login', ('/login', 'sign in')),
            ('/terms?back=/forgot', ('/forgot', 'password reset')),
            ('/terms?back=/password', ('/password', 'change password')),
            # the query survives: a half-finished registration keeps its token
            ('/terms?back=%2Fregister%3Ftoken%3Dabc', ('/register?token=abc', 'registration')),
        ]
        for path, expected in cases:
            with self.subTest(path=path):
                status, body = await self._get(path)
                self.assertEqual(status, 200)
                self.assertEqual(_back_link(body), expected)

    @unittest_run_loop
    async def test_back_link_refuses_anywhere_but_our_own_pages(self) -> None:
        for back in ['', '//evil.example/x', 'https://evil.example/',
                     'javascript:alert(1)', '/evil', 'login']:
            with self.subTest(back=back):
                status, body = await self._get(f'/terms?back={back}')
                self.assertEqual(status, 200)
                self.assertEqual(_back_link(body), ('/login', 'sign in'))

    # ── the shell's fragment is a fragment (its own crumbs lead back) ─────────────

    @unittest_run_loop
    async def test_htmx_terms_is_a_bare_fragment(self) -> None:
        status, body = await self._get('/terms', headers={'HX-Request': 'true'})
        self.assertEqual(status, 200)
        self.assertNotIn('</html>', body)
        self.assertIsNone(_back_link(body))
        self.assertIn('id="crumbs"', body)
        self.assertIn('Version&nbsp;test', body)             # the configured terms_version


if __name__ == '__main__':
    unittest.main()
