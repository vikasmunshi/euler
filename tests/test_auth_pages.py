#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Every auth-tier page renders, and the terms page's way back out.

The plain "does it render" half is the point: these pages all extend base.html,
so a mistake in the shared template breaks the whole signed-out tier at once —
as a footer reading `request.path_qs` did, aiohttp_jinja2 having no request in
the template context until the app registers its request processor. Rendering
each page through the real app is what catches that; a bare Jinja render with a
hand-made context does not.

The other half is the back link the standalone /terms carries (Referrer-Policy is
no-referrer, so the linking page names itself in `?back=`): it must return a
reader to our own pages only, and never anywhere else."""
from __future__ import annotations

import asyncio
import re
import shutil
import tempfile
import time
import unittest
from pathlib import Path

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from euler_site.auth import policy
from euler_site.auth.app import AuthService, build_public_app
from euler_site.auth.config import AuthConfig

from tests import silence

silence()   # quiet console + filter aiohttp's request-key warning (isolated-run cleanliness)

_EMAIL = 'user@example.com'

#: (path, a string the rendered page must contain) — every GET a signed-out
#: visitor can reach, each one an extension of base.html.
_PAGES = [
    ('/login', 'SRP-6a'),                                    # the sign-in window's status bar
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
    async def test_signed_out_pages_are_never_stored(self) -> None:
        """The auth tier is stamped by the same middleware as the content tier (§11.10):
        a login page carries a one-shot handshake, and belongs in no cache at all."""
        for path, _ in _PAGES:
            with self.subTest(path=path):
                resp = await self.client.get(path)
                self.assertEqual(resp.headers.get('Cache-Control'), 'no-store')

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
        self.assertIn('Version&nbsp;test', body)             # the configured terms_version

    @unittest_run_loop
    async def test_htmx_terms_wears_the_shells_chrome(self) -> None:
        """The pane's chrome comes from the content service's own partials — the
        crumbs (house-glyph home → leaf) and an Actions menu that is empty, not
        absent. Rendering them here is what keeps /terms from drifting: an auth
        route, but a page in the shell's pane like any other."""
        _, body = await self._get('/terms', headers={'HX-Request': 'true'})
        self.assertIn('<nav id="crumbs" class="crumbs" aria-label="Breadcrumb" '
                      'hx-swap-oob="true">', body)
        # A house, not the brand figure: the brand already sits in the header, and a
        # trail opening with a second copy of it reads as decoration, not as a step.
        self.assertIn('class="crumb-home"', body)
        self.assertNotIn('brand-glyph', body)
        self.assertIn('<span class="crumb-leaf">terms</span>', body)
        self.assertIn('<div id="actions" class="actions" hx-swap-oob="true">', body)
        self.assertIn('<summary>Actions</summary>', body)
        self.assertIn('No actions here', body)


class ForgotPasswordTests(AuthPageTests):
    """`POST /forgot` cannot be used to keep an owner from resetting, or to spend the mail.

    The mailer is replaced by a recorder (no relay is involved); the account exists unless
    a test says otherwise.
    """

    async def get_application(self):
        app = await super().get_application()
        self.service.users.create(_EMAIL, '00' * 16, 'ab', 'test', 'now')
        self.sent: list[tuple[str, str]] = []

        def record(rcpt: str, token: str, kind: str) -> None:
            self.sent.append((rcpt, token))
        self.service.mailer.send_invite = record                  # type: ignore[method-assign]
        return app

    async def _forgot(self, email: str = _EMAIL) -> int:
        resp = await self.client.post('/forgot', data={'email': email})
        await asyncio.sleep(0.05)                          # let the background send run
        return resp.status

    @unittest_run_loop
    async def test_a_second_request_does_not_kill_the_first_link(self) -> None:
        self.assertEqual(await self._forgot(), 200)
        self.assertEqual(len(self.sent), 1)
        first = self.sent[0][1]
        self.assertEqual(await self._forgot(), 200)        # same page either way…
        self.assertEqual(len(self.sent), 1, 'no second mail inside the cooldown')
        self.assertIsNotNone(self.service.pending.get(first), 'the first link still works')

    @unittest_run_loop
    async def test_daily_cap(self) -> None:
        for _ in range(policy.RESET_DAILY_MAX + 2):
            await self._forgot()
            # step past the cooldown by ageing every record's mint time
            records = self.service.pending._load()
            for rec in records.values():
                rec['minted'] = float(rec['minted']) - policy.RESET_COOLDOWN_SECONDS - 1
            self.service.pending._save(records)
        self.assertEqual(len(self.sent), policy.RESET_DAILY_MAX)

    @unittest_run_loop
    async def test_unknown_address_sends_nothing_and_looks_the_same(self) -> None:
        known = await (await self.client.post('/forgot', data={'email': _EMAIL})).text()
        unknown = await (await self.client.post('/forgot', data={'email': 'nobody@example.test'})).text()
        await asyncio.sleep(0.05)
        self.assertEqual(known, unknown)
        self.assertEqual([email for email, _ in self.sent], [_EMAIL])

    @unittest_run_loop
    async def test_the_answer_does_not_wait_for_the_mail(self) -> None:
        def slow_send(rcpt: str, token: str, kind: str) -> None:
            time.sleep(1.0)
        self.service.mailer.send_invite = slow_send          # type: ignore[method-assign]
        started = time.monotonic()
        await self.client.post('/forgot', data={'email': _EMAIL})
        self.assertLess(time.monotonic() - started, 0.5)

    def test_the_mail_budget_per_recipient(self) -> None:
        allowed = [self.service.mail_allowed('a@example.test')
                   for _ in range(policy.MAIL_PER_RECIPIENT_MAX + 3)]
        self.assertEqual(allowed.count(True), policy.MAIL_PER_RECIPIENT_MAX)
        self.assertTrue(self.service.mail_allowed('b@example.test'), 'another recipient is unaffected')


if __name__ == '__main__':
    unittest.main()
