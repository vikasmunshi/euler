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

    def test_an_unreadable_policy_is_deployed_with_no_names(self) -> None:
        """A per-user uid may not read the map (root:euler-authz 0640). That must read as a
        deployed policy with nobody in it — never as no policy, which would make the owner of
        any checkout `admin`."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'authz.json'
            f.write_text(json.dumps(_POLICY))
            with mock.patch.object(Path, 'read_text', side_effect=PermissionError):
                policy = Authorizations.read(f)
        self.assertIsNotNone(policy)
        assert policy is not None
        self.assertEqual(policy.all_users(), {}, 'no names leak through')
        subj = subject_for(system_slug('alice@example.com'), owner=True, policy=policy)
        self.assertEqual(subj.profile, 'reader', 'the checkout owner gains nothing')

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

    def _unreadable_map(self, tmp: str, rung: dict[str, object] | None,
                        trusted: bool = True) -> Authorizations | None:
        """deployed_policy() as uid *alice's slug* sees it: the map is there, root's and
        unreadable; *rung* is that uid's published row (None: none published); *trusted* says
        whether that row is root-owned all the way up."""
        policy = Path(tmp) / 'authz.json'
        policy.write_text(json.dumps(_POLICY))
        slug = system_slug('alice@example.com')
        own = Path(tmp) / 'profiles' / slug
        if rung is not None:
            own.parent.mkdir()
            own.write_text(json.dumps(rung))
        with mock.patch.dict(os.environ, {AUTHZ_FILE_ENV: str(policy)}), \
             mock.patch('solver.auth.identity.DEFAULT_AUTHZ_FILE', str(policy)), \
             mock.patch('solver.auth.identity.os_login', return_value=slug), \
             mock.patch('solver.auth.identity._root_owned', side_effect=lambda p: trusted or p != own), \
             mock.patch('solver.auth.identity.os.access', side_effect=lambda p, m: Path(p) != policy):
            return deployed_policy()

    def test_a_per_user_account_reads_its_rung_from_its_own_row(self) -> None:
        """The map is closed to a per-user uid (root:euler-authz 0640); its own published row is
        what lets a `solver` it runs — claude-solve's headless Claude — hold its owner's rung."""
        with tempfile.TemporaryDirectory() as tmp:
            policy = self._unreadable_map(tmp, {'users': {'alice@example.com': 'maintainer'}})
        assert policy is not None
        self.assertEqual(policy.all_users(), {'alice@example.com': 'maintainer'}, 'its own row, no one else')
        subj = subject_for(system_slug('alice@example.com'), owner=True, policy=policy)
        self.assertEqual((subj.user, subj.profile, subj.auth_method),
                         ('alice@example.com', 'maintainer', 'policy-account'))

    def test_without_its_row_a_per_user_account_is_a_reader(self) -> None:
        """No row published (not provisioned yet): still a deployed policy, with nobody in it."""
        with tempfile.TemporaryDirectory() as tmp:
            policy = self._unreadable_map(tmp, None)
        assert policy is not None
        self.assertEqual(subject_for(system_slug('alice@example.com'), owner=True, policy=policy).profile,
                         'reader')

    def test_a_row_the_user_can_write_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            policy = self._unreadable_map(tmp, {'users': {'alice@example.com': 'maintainer'}}, trusted=False)
        assert policy is not None
        self.assertEqual(policy.all_users(), {})

    def test_root_ownership_runs_all_the_way_up(self) -> None:
        self.assertTrue(identity._root_owned(Path('/etc')))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(identity._root_owned(Path(tmp) / 'x.json'))


class SystemSlugTest(unittest.TestCase):
    """The system slug: the `useradd`-safe uid name derived from an e-mail identity.

    It IS the unix account name, so the shape it must hold to is the one
    `scripts/setup/user.sh` validates: `u` + 16 hex digits.
    """

    #: What user.sh's valid_slug accepts — and, being letter-led [a-z0-9], also what
    #: `useradd`'s NAME_REGEX accepts.
    _SLUG_SHAPE = re.compile(r'^u[0-9a-f]{16}$')

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

    def test_the_slug_is_wide(self) -> None:
        """The slug is the routing key and the uid: an address that hashed to someone else's
        would be their instance. 64 bits puts finding one out of reach (24 took under a second)."""
        self.assertEqual(system_slug('alice@example.com'), 'uff8d9819fc0e12bf')
        self.assertEqual(len(system_slug('x@y.z')), 17)


if __name__ == '__main__':
    unittest.main()
