#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Per-user native git verbs (MT-2): grants, guards, and dispatch.

The per-user model makes git native — a collaborator works in their own clone on
``user/<slug>`` as their own uid — so what the commands must get right is the
**policy shape** (read verbs at ``git:read``/reader, write verbs at
``git:execute``/contributor, master admin-gated) and the **guards** (never a
non-admin push of master, never a force-push of master, a conflicted merge always
aborted). Everything that would touch a real remote is exercised with
``run_cmdline`` recorded; the real two-clone flow is covered by the step-6
runtime verification.
"""
from __future__ import annotations

import json
import unittest
from typing import Any
from unittest.mock import MagicMock

from solver.auth import Authorizations, Subject
from solver.auth.authorizations import DEFAULT_POLICY_FILE
from solver.config import ExitCodes, config
from solver.shell.command import effective_requires, registry
from solver.utils import scripts
from solver.utils.loader import load_commands

_AUTHZ = Authorizations(json.loads(DEFAULT_POLICY_FILE.read_text(encoding='utf-8')))


def _subject(profile: str) -> Subject:
    return Subject(user='t@example.com', slug='t-000000', channel='web', auth_method='test',
                   profile=profile, permissions=_AUTHZ.permissions_for(profile))


class PolicyShapeTest(unittest.TestCase):
    """The template ships the MT-2 ladder: read for every rung, write for contributor+."""

    def test_reader_has_git_read_not_execute(self) -> None:
        reader = _AUTHZ.permissions_for('reader')
        self.assertIn('git:read', reader)
        self.assertNotIn('git:execute', reader)

    def test_contributor_has_git_execute(self) -> None:
        self.assertIn('git:execute', _AUTHZ.permissions_for('contributor'))

    def test_requires_of_the_git_commands(self) -> None:
        load_commands()
        expected = {'git-status': ('git:read',), 'git-sync': ('git:read',),
                    'git-commit': ('git:execute',), 'git-push': ('git:execute',),
                    'git-hooks': ('git:execute',), 'git-identity': ('git:execute',),
                    'git-merge': ('infra:execute',), 'git-publish': ('infra:execute',)}
        for name, requires in expected.items():
            cmd = registry.resolve(name)
            self.assertIsNotNone(cmd, f'{name} not registered')
            assert cmd is not None
            self.assertEqual(effective_requires(cmd.requires), requires, name)


class _GitCommandCase(unittest.TestCase):
    """Record run_cmdline, pin the branch, and swap the subject."""

    branch: str = 'user/t-000000'

    def setUp(self) -> None:
        self.cmdlines: list[str] = []
        self.rcs: list[int] = []                    # queued rcs; default 0

        def fake_run_cmdline(cmdline: str) -> int:
            self.cmdlines.append(cmdline)
            return self.rcs.pop(0) if self.rcs else 0

        self._saved_run = scripts.run_cmdline
        self._saved_branch = scripts._current_branch
        self._saved_subject = config.subject
        scripts.run_cmdline = fake_run_cmdline      # type: ignore[assignment]
        scripts._current_branch = lambda: self.branch  # type: ignore[assignment]

    def tearDown(self) -> None:
        scripts.run_cmdline = self._saved_run       # type: ignore[assignment]
        scripts._current_branch = self._saved_branch  # type: ignore[assignment]
        config.subject = self._saved_subject

    def as_profile(self, profile: str) -> None:
        config.subject = _subject(profile)


class GitPushGuardTest(_GitCommandCase):
    def test_contributor_pushes_their_own_branch(self) -> None:
        self.as_profile('contributor')
        self.assertEqual(scripts.git_push(), 0)
        self.assertEqual(self.cmdlines, ['git push -u origin user/t-000000'])

    def test_force_uses_force_with_lease(self) -> None:
        self.as_profile('contributor')
        self.assertEqual(scripts.git_push(force=True), 0)
        self.assertEqual(self.cmdlines, ['git push -u --force-with-lease origin user/t-000000'])

    def test_non_admin_cannot_push_master(self) -> None:
        self.branch = 'master'
        self.as_profile('contributor')
        self.assertEqual(scripts.git_push(), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])         # refused before any git ran

    def test_admin_may_push_master_but_never_forced(self) -> None:
        self.branch = 'master'
        self.as_profile('admin')
        self.assertEqual(scripts.git_push(), 0)
        self.assertEqual(self.cmdlines, ['git push -u origin master'])
        self.cmdlines.clear()
        self.assertEqual(scripts.git_push(force=True), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])

    def test_detached_head_is_refused(self) -> None:
        self.branch = 'HEAD'
        self.as_profile('admin')
        self.assertEqual(scripts.git_push(), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])


class GitMergeTest(_GitCommandCase):
    branch = 'master'

    def test_bare_slug_means_user_branch(self) -> None:
        self.as_profile('admin')
        self.assertEqual(scripts.git_merge('alice-3f9e97'), 0)
        self.assertEqual(self.cmdlines, [
            'git fetch origin user/alice-3f9e97',
            'git merge --no-ff -m "merge user/alice-3f9e97" origin/user/alice-3f9e97',
            'git push origin master',
        ])

    def test_no_push_flag_skips_the_push(self) -> None:
        self.as_profile('admin')
        self.assertEqual(scripts.git_merge('alice-3f9e97', push=False), 0)
        self.assertNotIn('git push origin master', self.cmdlines)

    def test_off_master_is_refused(self) -> None:
        self.branch = 'user/t-000000'
        self.as_profile('admin')
        self.assertEqual(scripts.git_merge('alice-3f9e97'), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])

    def test_conflicted_merge_is_aborted(self) -> None:
        self.as_profile('admin')
        self.rcs = [0, 1]                           # fetch ok, merge conflicts
        self.assertEqual(scripts.git_merge('alice-3f9e97'), ExitCodes.EXIT_ERROR)
        self.assertIn('git merge --abort', self.cmdlines)
        self.assertNotIn('git push origin master', self.cmdlines)


class EncKeyPullFlowTest(_GitCommandCase):
    """The MT-2 sync tail: wire the filter exactly when unwired AND key-authorized."""

    def setUp(self) -> None:
        super().setUp()
        self._saved_master = scripts.read_master_key
        self._saved_run_proc = scripts.run
        self.master = MagicMock(return_value=b'\x00' * 32)
        self.master.cache_clear = MagicMock()
        scripts.read_master_key = self.master       # type: ignore[assignment]

    def tearDown(self) -> None:
        scripts.read_master_key = self._saved_master  # type: ignore[assignment]
        scripts.run = self._saved_run_proc          # type: ignore[assignment]
        super().tearDown()

    def _wire_state(self, wired: bool) -> None:
        def fake_run(*_a: Any, **_k: Any) -> Any:
            return MagicMock(returncode=0 if wired else 1)
        scripts.run = fake_run                      # type: ignore[assignment]

    def test_already_wired_is_a_silent_noop(self) -> None:
        self._wire_state(wired=True)
        scripts._enc_key_pull_flow()
        self.assertEqual(self.cmdlines, [])
        self.master.assert_not_called()

    def test_unauthorized_is_a_silent_noop(self) -> None:
        self._wire_state(wired=False)
        self.master.side_effect = KeyError('no entry for this public key')
        scripts._enc_key_pull_flow()
        self.assertEqual(self.cmdlines, [])

    def test_newly_authorized_wires_and_rechecks_out(self) -> None:
        self._wire_state(wired=False)
        scripts._enc_key_pull_flow()
        self.master.cache_clear.assert_called_once()    # the pull may have delivered access
        self.assertEqual(len(self.cmdlines), 2)
        self.assertIn('solver.crypto.gitfilter install', self.cmdlines[0])
        self.assertIn('git checkout -- solutions/private', self.cmdlines[1])

    def test_failed_install_skips_the_recheckout(self) -> None:
        self._wire_state(wired=False)
        self.rcs = [1]                              # install refused (key check failed late)
        scripts._enc_key_pull_flow()
        self.assertEqual(len(self.cmdlines), 1)


if __name__ == '__main__':
    unittest.main()
