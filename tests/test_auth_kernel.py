#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the solver/auth RBAC kernel (DD-12): the Authorizations policy
(inheritance expansion, user map, fail-closed) and resolve_subject's planes."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from solver.auth import Authorizations, Subject, resolve_subject
from solver.auth.authorizations import AUTHZ_FILE_ENV

_POLICY = {
    'profiles': {
        'reader': {'inherits': None, 'grants': ['solutions:read', 'users:read']},
        'contributor': {'inherits': 'reader', 'grants': ['solutions:write', 'solutions:execute']},
        'maintainer': {'inherits': 'contributor', 'grants': ['solutions:delete', 'ai:execute']},
        'admin': {'inherits': 'maintainer', 'grants': ['shell:execute', 'infra:execute', 'users:write']},
    },
    'users': {'Alice@Example.com': 'maintainer', 'bob': 'contributor'},
    'objects': {'solutions': ['solutions/'], 'shell': ['/bin/bash'], 'infra': []},
}


class AuthorizationsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.authz = Authorizations(_POLICY)

    def test_inheritance_expands_up_the_chain(self) -> None:
        perms = self.authz.permissions_for('maintainer')
        # own + contributor + reader grants, all present
        self.assertIn('solutions:delete', perms)   # own
        self.assertIn('solutions:write', perms)     # contributor
        self.assertIn('solutions:read', perms)      # reader
        self.assertNotIn('infra:execute', perms)    # admin-only, not inherited downward

    def test_admin_has_everything(self) -> None:
        perms = self.authz.permissions_for('admin')
        for p in ('solutions:read', 'solutions:write', 'solutions:delete',
                  'ai:execute', 'shell:execute', 'infra:execute', 'users:write'):
            self.assertIn(p, perms)

    def test_unknown_profile_is_empty_failclosed(self) -> None:
        self.assertEqual(self.authz.permissions_for('nobody'), frozenset())

    def test_user_map_lookup_is_normalised(self) -> None:
        self.assertEqual(self.authz.profile_for('alice@example.com'), 'maintainer')  # lowercased
        self.assertEqual(self.authz.profile_for('  BOB '), 'contributor')            # trimmed
        self.assertIsNone(self.authz.profile_for('stranger'))

    def test_objects_paths(self) -> None:
        self.assertEqual(self.authz.paths_for('solutions'), ['solutions/'])
        self.assertEqual(self.authz.paths_for('infra'), [])
        self.assertEqual(self.authz.paths_for('missing'), [])

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
        self.assertIn('solutions:read', loaded.permissions_for('reader'))
        self.assertIn('infra:execute', loaded.permissions_for('admin'))


class ResolveSubjectTest(unittest.TestCase):
    def setUp(self) -> None:
        self.authz = Authorizations(_POLICY)
        self.root = Path('/some/repo')

    def _resolve(self, **env: str) -> Subject:
        with mock.patch.dict(os.environ, env, clear=False):
            os.environ.pop('SOLVER_TICKET', None)     # never inherit the caller's
            os.environ.pop('EULER_PROFILE', None)     # ditto the instance pin
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
        self.assertTrue(subj.has('infra:execute'))

    def test_explicit_map_entry_wins_over_owner_floor(self) -> None:
        # bob owns the checkout but is mapped contributor → contributor, not admin.
        with mock.patch('solver.auth.identity.getpass.getuser', return_value='bob'), \
             mock.patch('solver.auth.identity._owns_checkout', return_value=True):
            subj = self._resolve()
        self.assertEqual(subj.profile, 'contributor')
        self.assertFalse(subj.has('infra:execute'))

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

    def test_ticket_plane_web_capped_at_maintainer(self) -> None:
        with mock.patch('solver.auth.identity._redeem_ticket', return_value=('x@y.z', 'admin')):
            subj = self._resolve(SOLVER_TICKET='t')
        self.assertEqual(subj.channel, 'web')
        self.assertEqual(subj.profile, 'maintainer')      # admin capped
        self.assertEqual(subj.auth_method, 'shell-ticket')

    def test_ticket_failure_aborts(self) -> None:
        with mock.patch('solver.auth.identity._redeem_ticket', side_effect=SystemExit('rejected')):
            with self.assertRaises(SystemExit):
                self._resolve(SOLVER_TICKET='bad')

    def test_ticket_profile_must_match_the_instance_pin(self) -> None:
        """DD-13: the forking ws instance *is* the rung's uid, so a ticket for another
        rung means misrouting or a bypass — the child refuses to start."""
        with mock.patch('solver.auth.identity._redeem_ticket', return_value=('x@y.z', 'maintainer')):
            with self.assertRaises(SystemExit):
                self._resolve(SOLVER_TICKET='t', EULER_PROFILE='reader')

    def test_ticket_profile_matching_the_pin_starts(self) -> None:
        with mock.patch('solver.auth.identity._redeem_ticket', return_value=('x@y.z', 'contributor')):
            subj = self._resolve(SOLVER_TICKET='t', EULER_PROFILE='contributor')
        self.assertEqual(subj.profile, 'contributor')

    def test_admin_ticket_capped_then_matched_against_a_maintainer_pin(self) -> None:
        """The maintainer cap is applied *before* the pin check, so an (impossible)
        admin ticket on the maintainer instance resolves as maintainer, not an abort."""
        with mock.patch('solver.auth.identity._redeem_ticket', return_value=('x@y.z', 'admin')):
            subj = self._resolve(SOLVER_TICKET='t', EULER_PROFILE='maintainer')
        self.assertEqual(subj.profile, 'maintainer')


if __name__ == '__main__':
    unittest.main()
