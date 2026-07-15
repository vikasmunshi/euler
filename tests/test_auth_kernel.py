#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the solver/auth kernel (DD-12, re-simplified): the plain profile
ladder (rank comparison, fail-closed), the users map, and resolve_subject's planes."""
from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from solver.auth import Authorizations, Subject, resolve_subject
from solver.auth.authorizations import AUTHZ_FILE_ENV
from solver.auth.identity import system_slug

_POLICY = {
    'ladder': ['reader', 'contributor', 'maintainer', 'admin'],
    'users': {'Alice@Example.com': 'maintainer', 'bob': 'contributor'},
}


class AuthorizationsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.authz = Authorizations(_POLICY)

    def test_the_ladder_is_a_rank_comparison(self) -> None:
        maintainer = Subject(user='t', slug='t', channel='terminal',
                             auth_method='test', profile='maintainer')
        for floor, held in (('reader', True), ('contributor', True),
                            ('maintainer', True), ('admin', False)):
            self.assertEqual(maintainer.has(floor), held, floor)

    def test_unknown_profile_and_floor_are_failclosed(self) -> None:
        nobody = Subject(user='t', slug='t', channel='terminal',
                         auth_method='test', profile='nobody')
        self.assertFalse(nobody.has('reader'))      # unknown profile holds nothing
        admin = Subject(user='t', slug='t', channel='terminal',
                        auth_method='test', profile='admin')
        self.assertFalse(admin.has('bogus'))        # unknown floor admits no one

    def test_mismatched_ladder_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Authorizations({'ladder': ['admin', 'reader'], 'users': {}})

    def test_user_map_lookup_is_normalised(self) -> None:
        self.assertEqual(self.authz.profile_for('alice@example.com'), 'maintainer')  # lowercased
        self.assertEqual(self.authz.profile_for('  BOB '), 'contributor')            # trimmed
        self.assertIsNone(self.authz.profile_for('stranger'))

    def test_load_prefers_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'authz.json'
            f.write_text(json.dumps(_POLICY))
            with mock.patch.dict(os.environ, {AUTHZ_FILE_ENV: str(f)}):
                loaded = Authorizations.load()
            self.assertEqual(loaded.profile_for('bob'), 'contributor')

    def test_load_falls_back_to_builtin_default(self) -> None:
        # No env, no /etc/euler file in the test env → the bundled template ladder.
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(AUTHZ_FILE_ENV, None)
            loaded = Authorizations.load()
        self.assertEqual(sorted(loaded.known_profiles()),
                         ['admin', 'contributor', 'maintainer', 'reader'])


class ResolveSubjectTest(unittest.TestCase):
    def setUp(self) -> None:
        self.authz = Authorizations(_POLICY)
        self.root = Path('/some/repo')

    def _resolve(self, **env: str) -> Subject:
        with mock.patch.dict(os.environ, env, clear=False):
            os.environ.pop('SOLVER_TICKET', None)     # never inherit the caller's
            os.environ.pop('EULER_USER_SLUG', None)   # ditto the instance pin
            os.environ.pop('EULER_USER_EMAIL', None)  # ditto the instance-identity handoff
            for k, v in env.items():
                os.environ[k] = v
            return resolve_subject(self.root, self.authz)

    def test_owner_uid_floors_to_admin_when_unlisted(self) -> None:
        with mock.patch('solver.auth.identity.getpass.getuser', return_value='vikas'), \
             mock.patch('solver.auth.identity._owns_checkout', return_value=True):
            subj = self._resolve()
        self.assertEqual(subj.profile, 'admin')
        self.assertEqual(subj.channel, 'terminal')
        self.assertEqual(subj.auth_method, 'checkout-owner')
        self.assertTrue(subj.has('admin'))

    def test_explicit_map_entry_wins_over_owner_floor(self) -> None:
        # bob owns the checkout but is mapped contributor → contributor, not admin.
        with mock.patch('solver.auth.identity.getpass.getuser', return_value='bob'), \
             mock.patch('solver.auth.identity._owns_checkout', return_value=True):
            subj = self._resolve()
        self.assertEqual(subj.profile, 'contributor')
        self.assertFalse(subj.has('admin'))

    def test_non_owner_unlisted_login_is_contributor(self) -> None:
        with mock.patch('solver.auth.identity.getpass.getuser', return_value='carol'), \
             mock.patch('solver.auth.identity._owns_checkout', return_value=False):
            subj = self._resolve()
        self.assertEqual(subj.profile, 'contributor')
        self.assertEqual(subj.auth_method, 'os-login')

    def test_service_uid_without_ticket_aborts(self) -> None:
        with mock.patch('solver.auth.identity.getpass.getuser', return_value='euler-ws'), \
             mock.patch('solver.auth.identity._owns_checkout', return_value=False):
            with self.assertRaises(SystemExit):
                self._resolve()

    def test_instance_identity_plane_resolves_a_ticketless_descendant(self) -> None:
        """MT-4: a euler-user-<slug> uid whose ticket has been scrubbed resolves from
        the handed-down e-mail; profile comes from policy (alice → maintainer)."""
        slug = system_slug('alice@example.com')
        with mock.patch('solver.auth.identity.getpass.getuser', return_value=f'euler-user-{slug}'):
            subj = self._resolve(EULER_USER_SLUG=slug, EULER_USER_EMAIL='alice@example.com')
        self.assertEqual(subj.channel, 'web')
        self.assertEqual(subj.auth_method, 'instance-identity')
        self.assertEqual(subj.user, 'alice@example.com')
        self.assertEqual(subj.slug, slug)
        self.assertEqual(subj.profile, 'maintainer')

    def test_instance_identity_unlisted_user_floors_to_the_weakest_rung(self) -> None:
        slug = system_slug('nobody@example.com')
        with mock.patch('solver.auth.identity.getpass.getuser', return_value=f'euler-user-{slug}'):
            subj = self._resolve(EULER_USER_SLUG=slug, EULER_USER_EMAIL='nobody@example.com')
        self.assertEqual(subj.profile, 'reader')          # fail closed low, never admin

    def test_instance_identity_rejects_a_forged_email(self) -> None:
        """A child cannot swap in a different e-mail: its system_slug no longer matches the
        uid's pin, so the plane declines and the service account aborts."""
        pin = system_slug('alice@example.com')
        with mock.patch('solver.auth.identity.getpass.getuser', return_value=f'euler-user-{pin}'):
            with self.assertRaises(SystemExit):
                self._resolve(EULER_USER_SLUG=pin, EULER_USER_EMAIL='attacker@evil.com')

    def test_instance_identity_requires_the_per_user_prefix(self) -> None:
        """A shared service uid (euler-ws) is not a per-user instance even with the env set."""
        slug = system_slug('alice@example.com')
        with mock.patch('solver.auth.identity.getpass.getuser', return_value='euler-ws'), \
             mock.patch('solver.auth.identity._owns_checkout', return_value=False):
            with self.assertRaises(SystemExit):
                self._resolve(EULER_USER_SLUG=slug, EULER_USER_EMAIL='alice@example.com')

    def test_ticket_plane_web_is_not_capped(self) -> None:
        """MT-10a: the per-user model drops the admin→maintainer web cap — an admin
        account keeps full authority over the web, contained by its own uid + SRP."""
        with mock.patch('solver.auth.identity._redeem_ticket', return_value=('x@y.z', 'admin')):
            subj = self._resolve(SOLVER_TICKET='t')
        self.assertEqual(subj.channel, 'web')
        self.assertEqual(subj.profile, 'admin')           # NOT capped (MT-10a)
        self.assertTrue(subj.has('admin'))
        self.assertEqual(subj.auth_method, 'shell-ticket')

    def test_ticket_failure_aborts(self) -> None:
        with mock.patch('solver.auth.identity._redeem_ticket', side_effect=SystemExit('rejected')):
            with self.assertRaises(SystemExit):
                self._resolve(SOLVER_TICKET='bad')

    def test_ticket_user_must_match_the_instance_slug_pin(self) -> None:
        """MT-4/MT-7: the forking instance *is* the user's uid, so a ticket whose e-mail
        maps to a different system slug means misrouting or a bypass — the child aborts."""
        with mock.patch('solver.auth.identity._redeem_ticket', return_value=('x@y.z', 'maintainer')):
            with self.assertRaises(SystemExit):
                self._resolve(SOLVER_TICKET='t', EULER_USER_SLUG='someone-else-000000')

    def test_ticket_matching_the_slug_pin_starts(self) -> None:
        with mock.patch('solver.auth.identity._redeem_ticket', return_value=('x@y.z', 'contributor')):
            subj = self._resolve(SOLVER_TICKET='t', EULER_USER_SLUG=system_slug('x@y.z'))
        self.assertEqual(subj.profile, 'contributor')
        self.assertEqual(subj.slug, system_slug('x@y.z'))

    def test_admin_ticket_matches_its_own_slug_pin(self) -> None:
        """An admin account's PTY child on its own per-user instance resolves as admin."""
        with mock.patch('solver.auth.identity._redeem_ticket', return_value=('boss@y.z', 'admin')):
            subj = self._resolve(SOLVER_TICKET='t', EULER_USER_SLUG=system_slug('boss@y.z'))
        self.assertEqual(subj.profile, 'admin')


class SystemSlugTest(unittest.TestCase):
    """The MT-14 system slug: a ``useradd``-safe name derived from an e-mail identity."""

    #: ``useradd`` NAME_REGEX: start with a letter/underscore, then [a-z0-9_-]; we emit no '_'.
    _USERADD_SAFE = re.compile(r'^[a-z][a-z0-9-]*$')

    def test_slug_is_useradd_safe(self) -> None:
        for email in ('MercAnther@gmail.com', 'a.b+tag@x.co', '123@host', 'x@y.z',
                      'UPPER.CASE@EXAMPLE.COM', 'weird!!name@d.com', '@leading', '_under@d.com'):
            slug = system_slug(email)
            self.assertRegex(slug, self._USERADD_SAFE, f'{email!r} → {slug!r} not useradd-safe')
            self.assertLess(len(f'euler-user-{slug}'), 32, f'{slug!r} too long for a system name')

    def test_slug_has_no_dot(self) -> None:
        # The bug that motivated MT-14: slugify emitted '.', which useradd rejects.
        self.assertNotIn('.', system_slug('merc.anther@gmail.com'))

    def test_slug_is_stable_and_case_insensitive(self) -> None:
        self.assertEqual(system_slug('Alice@Example.com'), system_slug('  alice@example.COM '))

    def test_distinct_emails_do_not_collide(self) -> None:
        # Same sanitised local-part, different domains → the hash keeps them apart.
        a, b = system_slug('sam@one.com'), system_slug('sam@two.com')
        self.assertNotEqual(a, b)
        self.assertTrue(a.startswith('sam-') and b.startswith('sam-'))

    def test_digit_leading_localpart_gets_a_letter_prefix(self) -> None:
        self.assertTrue(system_slug('42@host.com').startswith('u42-'))


if __name__ == '__main__':
    unittest.main()
