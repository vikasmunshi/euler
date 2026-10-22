#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the packages/solver/solver/auth kernel (re-simplified): the plain profile
ladder (rank comparison, fail-closed), the users map, and the OS-login identity with its role."""
from __future__ import annotations

import json
import os
import pwd
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from solver.auth import Authorizations, Subject, identity, resolve_subject
from solver.auth.authorizations import AUTHZ_FILE_ENV
from solver.auth.identity import deployed_policy, subject_for, system_slug

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
    """The solver shell's identity: the OS login, its role from the root-owned policy."""

    def setUp(self) -> None:
        self.authz = Authorizations(_POLICY)

    def test_no_policy_owner_is_admin(self) -> None:
        subj = subject_for('vikas', owner=True, policy=None)
        self.assertEqual((subj.profile, subj.channel, subj.auth_method), ('admin', 'terminal', 'checkout-owner'))

    def test_no_policy_non_owner_is_contributor(self) -> None:
        subj = subject_for('carol', owner=False, policy=None)
        self.assertEqual((subj.profile, subj.auth_method), ('contributor', 'os-login'))

    def test_a_listed_login_takes_its_entry_even_as_owner(self) -> None:
        subj = subject_for('bob', owner=True, policy=self.authz)
        self.assertEqual((subj.profile, subj.auth_method), ('contributor', 'policy'))

    def test_with_a_policy_an_unlisted_owner_is_not_admin(self) -> None:
        """Q4: when the policy is deployed it decides — owning a clone grants nothing."""
        subj = subject_for('carol', owner=True, policy=self.authz)
        self.assertEqual(subj.profile, 'reader')

    def test_a_per_user_account_holds_its_emails_rung(self) -> None:
        """A `solver` run under a per-user web uid (named for the e-mail's system slug) is
        that collaborator: their e-mail and rung, with the uid as the slug."""
        slug = system_slug('alice@example.com')
        subj = subject_for(slug, owner=True, policy=self.authz)
        self.assertEqual((subj.user, subj.slug, subj.profile, subj.auth_method),
                         ('alice@example.com', slug, 'maintainer', 'policy-account'))

    def test_resolution_reads_the_uid_not_the_environment(self) -> None:
        """$USER / $LOGNAME are the user's to set; the uid is not."""
        with mock.patch.dict(os.environ, {'USER': 'bob', 'LOGNAME': 'bob'}), \
             mock.patch('solver.auth.identity.deployed_policy', return_value=self.authz):
            subj = resolve_subject(Path('/'))
        self.assertEqual(subj.user, pwd.getpwuid(os.getuid()).pw_name)

    def test_a_policy_the_user_can_write_is_ignored(self) -> None:
        """EULER_AUTHZ_FILE pointing at a user-owned file does not grant a role."""
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / 'authz.json'
            f.write_text(json.dumps({'users': {pwd.getpwuid(os.getuid()).pw_name: 'admin'}}), encoding='utf-8')
            with mock.patch.dict(os.environ, {AUTHZ_FILE_ENV: str(f)}), \
                 mock.patch('solver.auth.identity.DEFAULT_AUTHZ_FILE', str(Path(tmp) / 'absent.json')):
                self.assertIsNone(deployed_policy())

    def test_root_ownership_runs_all_the_way_up(self) -> None:
        self.assertTrue(identity._root_owned(Path('/etc')))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(identity._root_owned(Path(tmp) / 'x.json'))


class SystemSlugTest(unittest.TestCase):
    """The system slug: the `useradd`-safe uid name derived from an e-mail identity.

    It IS the unix account name now (no `euler-user-` prefix), so the shape it must
    hold to is the one `scripts/setup/user.sh` validates: `u` + a hex digest.
    """

    #: What user.sh's valid_slug accepts — and, being letter-led [a-z0-9], also what
    #: `useradd`'s NAME_REGEX accepts.
    _SLUG_SHAPE = re.compile(r'^u[0-9a-f]{6,16}$')

    def test_slug_is_useradd_safe(self) -> None:
        for email in ('MercAnther@gmail.com', 'a.b+tag@x.co', '123@host', 'x@y.z',
                      'UPPER.CASE@EXAMPLE.COM', 'weird!!name@d.com', '@leading', '_under@d.com'):
            slug = system_slug(email)
            self.assertRegex(slug, self._SLUG_SHAPE, f'{email!r} → {slug!r} not a valid uid name')

    def test_slug_carries_no_localpart(self) -> None:
        # The uid, the home path and the branch are public-ish; the e-mail is not.
        self.assertNotIn('merc', system_slug('merc.anther@gmail.com'))
        self.assertNotIn('.', system_slug('merc.anther@gmail.com'))

    def test_slug_is_stable_and_case_insensitive(self) -> None:
        self.assertEqual(system_slug('Alice@Example.com'), system_slug('  alice@example.COM '))

    def test_distinct_emails_do_not_collide(self) -> None:
        # Same local-part, different domains → different digests, different uids.
        self.assertNotEqual(system_slug('sam@one.com'), system_slug('sam@two.com'))

    def test_digit_leading_localpart_still_starts_with_a_letter(self) -> None:
        self.assertTrue(system_slug('42@host.com').startswith('u'))


if __name__ == '__main__':
    unittest.main()
