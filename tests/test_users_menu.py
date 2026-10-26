#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `users` command's account menu and its listing.

The menu offers what the admin CLI takes — the e-mail or the os-login. The roster it used to
read is slug-keyed, and a slug picked off it named no account the admin plane knew: `users
remove` then failed after the choice. The listing keeps its columns aligned whatever the slug
width, including for a local login, which has none.
"""
from __future__ import annotations

import contextlib
import io
import unittest
from unittest import mock

from euler_site.auth import admin
from euler_webshell import users

_ROWS = [{'user': 'alice@example.com', 'slug': 'uff8d9819fc0e12bf', 'profile': 'reader', 'scope': 'web'},
         {'user': 'vikas', 'slug': '', 'profile': 'admin', 'scope': 'local'}]


class AccountChoicesTest(unittest.TestCase):
    def test_the_value_is_the_identity_and_the_slug_is_context(self) -> None:
        with mock.patch.object(users, '_roster', return_value=_ROWS):
            choices = users._account_choices(None, {})
        self.assertEqual([c.value for c in choices], ['alice@example.com', 'vikas'])
        self.assertEqual(choices[0].description, 'uff8d9819fc0e12bf · reader · web')
        self.assertEqual(choices[1].description, 'admin · local')

    def test_an_unreadable_host_offers_nothing(self) -> None:
        with mock.patch.object(users, '_roster', return_value=None):
            self.assertEqual(users._account_choices(None, {}), [])


class ListingTest(unittest.TestCase):
    def test_a_local_login_lines_up_with_the_web_rows(self) -> None:
        """A local login has no slug; its blank must be as wide as the slugs above it."""
        rows = [{**row, 'state': 'registered'} for row in _ROWS]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            admin._print_listing({'roster': rows, 'pending': []})
        web, local = out.getvalue().splitlines()
        self.assertEqual(web.index('reader'), local.index('admin'))


if __name__ == '__main__':
    unittest.main()
