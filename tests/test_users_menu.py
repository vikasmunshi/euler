#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `users` account menu offers what the admin CLI takes: the e-mail or the os-login.

The roster it used to read is slug-keyed, and a slug picked off it named no account the
admin plane knew — `users remove` then failed after the choice.
"""
from __future__ import annotations

import unittest
from unittest import mock

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


if __name__ == '__main__':
    unittest.main()
