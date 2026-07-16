#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Per-user native git verbs: floors, guards, and dispatch.

The per-user model makes git native — a collaborator works in their own clone on
``user/<slug>`` as their own uid — so what the commands must get right is the
**policy shape** (read verbs at ``reader``, write verbs at ``contributor``,
master admin-gated) and the **guards** (never a non-admin push of master, never a
force-push of master, a conflicted merge always aborted). Everything that would
touch a real remote is exercised with ``run_cmdline`` recorded; the real
two-clone flow is covered by the step-6 runtime verification.
"""
from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import MagicMock

from solver.auth import Subject
from solver.config import ExitCodes, config
from solver.shell.command import registry
from solver.utils import scripts
from solver.utils.loader import load_commands


def _subject(profile: str) -> Subject:
    return Subject(user='t@example.com', slug='t-000000', channel='web', auth_method='test',
                   profile=profile)


class PolicyShapeTest(unittest.TestCase):
    """The git floors: read for every rung, write for contributor+, master at admin."""

    def test_floors_of_the_git_commands(self) -> None:
        load_commands()
        expected = {'git-status': 'reader', 'git-sync': 'reader', 'git-filter': 'reader',
                    'git-commit': 'contributor', 'git-push': 'contributor',
                    'git-hooks': 'contributor', 'git-identity': 'contributor',
                    'git-merge': 'admin', 'git-publish': 'admin'}
        for name, floor in expected.items():
            cmd = registry.resolve(name)
            self.assertIsNotNone(cmd, f'{name} not registered')
            assert cmd is not None
            self.assertEqual(cmd.requires, floor, name)

    def test_reader_may_sync_but_not_push(self) -> None:
        reader = _subject('reader')
        self.assertTrue(reader.has('reader'))
        self.assertFalse(reader.has('contributor'))


class _GitCommandCase(unittest.TestCase):
    """Record run_cmdline, pin the branch, and swap the subject."""

    branch: str = 'user/t-000000'

    def setUp(self) -> None:
        self.cmdlines: list[str] = []
        self.rcs: list[int] = []                    # queued rcs; default 0
        self.prs: list[str] = []                    # branches a PR was opened for
        self.pr_rc: int = 0

        def fake_run_cmdline(cmdline: str) -> int:
            self.cmdlines.append(cmdline)
            return self.rcs.pop(0) if self.rcs else 0

        def fake_ensure_pr(branch: str) -> int:
            self.prs.append(branch)
            return self.pr_rc

        self._saved_run = scripts.run_cmdline
        self._saved_branch = scripts._current_branch
        self._saved_pr = scripts._ensure_pull_request
        self._saved_subject = config.subject
        scripts.run_cmdline = fake_run_cmdline      # type: ignore[assignment]
        scripts._current_branch = lambda: self.branch  # type: ignore[assignment]
        # git-push opens a PR, which reaches the GitHub API through `gh` — recorded here
        # like run_cmdline, so no test can touch a real remote (module docstring).
        scripts._ensure_pull_request = fake_ensure_pr  # type: ignore[assignment]

    def tearDown(self) -> None:
        scripts.run_cmdline = self._saved_run       # type: ignore[assignment]
        scripts._current_branch = self._saved_branch  # type: ignore[assignment]
        scripts._ensure_pull_request = self._saved_pr  # type: ignore[assignment]
        config.subject = self._saved_subject

    def as_profile(self, profile: str) -> None:
        config.subject = _subject(profile)


class GitPushGuardTest(_GitCommandCase):
    def test_contributor_pushes_their_own_branch_and_opens_its_pr(self) -> None:
        self.as_profile('contributor')
        self.assertEqual(scripts.git_push(), 0)
        self.assertEqual(self.cmdlines, ['git push -u origin user/t-000000'])
        self.assertEqual(self.prs, ['user/t-000000'])

    def test_force_uses_force_with_lease(self) -> None:
        self.as_profile('contributor')
        self.assertEqual(scripts.git_push(force=True), 0)
        self.assertEqual(self.cmdlines, ['git push -u --force-with-lease origin user/t-000000'])

    def test_no_pr_pushes_and_stops(self) -> None:
        self.as_profile('contributor')
        self.assertEqual(scripts.git_push(pr=False), 0)
        self.assertEqual(self.cmdlines, ['git push -u origin user/t-000000'])
        self.assertEqual(self.prs, [])

    def test_a_failed_push_never_opens_a_pr(self) -> None:
        self.as_profile('contributor')
        self.rcs = [1]
        self.assertNotEqual(scripts.git_push(), 0)
        self.assertEqual(self.prs, [])              # nothing to review — the branch never landed

    def test_a_failed_pr_fails_the_command(self) -> None:
        # The push succeeded, but git-push promises a PR: reporting success would leave
        # the user believing their work is under review when it is not.
        self.as_profile('contributor')
        self.pr_rc = 1
        self.assertNotEqual(scripts.git_push(), 0)

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
        self.assertEqual(self.prs, [])              # master has nothing to merge into itself
        self.cmdlines.clear()
        self.assertEqual(scripts.git_push(force=True), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])

    def test_detached_head_is_refused(self) -> None:
        self.branch = 'HEAD'
        self.as_profile('admin')
        self.assertEqual(scripts.git_push(), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])


class PullRequestTest(unittest.TestCase):
    """`_ensure_pull_request`: idempotent, and never a second PR for one branch.

    `gh` is stubbed at the `run` boundary — the real GitHub API is never reached (module
    docstring), which is exactly the invariant a PR-opening command could quietly break.
    """

    def setUp(self) -> None:
        self.calls: list[list[str]] = []
        self._saved_run = scripts.run

        def fake_run(argv: list[str], **kwargs: Any) -> Any:
            self.calls.append(argv)
            return self.responses.pop(0)

        scripts.run = fake_run                      # type: ignore[assignment]
        self.responses: list[Any] = []
        self.addCleanup(lambda: setattr(scripts, 'run', self._saved_run))

    @staticmethod
    def _result(returncode: int = 0, stdout: str = '', stderr: str = '') -> Any:
        return MagicMock(returncode=returncode, stdout=stdout, stderr=stderr)

    def test_an_open_pr_is_reported_not_duplicated(self) -> None:
        self.responses = [self._result(stdout='https://github.com/o/r/pull/7\n')]
        self.assertEqual(scripts._ensure_pull_request('user/t-000000'), 0)
        self.assertEqual(len(self.calls), 1)                    # the lookup only
        self.assertEqual(self.calls[0][:3], ['gh', 'pr', 'view'])

    def test_no_open_pr_opens_one_onto_master(self) -> None:
        self.responses = [self._result(stdout=''),              # lookup: none open
                          self._result(stdout='https://github.com/o/r/pull/8\n')]
        self.assertEqual(scripts._ensure_pull_request('user/t-000000'), 0)
        created = self.calls[1]
        self.assertEqual(created[:3], ['gh', 'pr', 'create'])
        self.assertEqual(created[created.index('--head') + 1], 'user/t-000000')
        self.assertEqual(created[created.index('--base') + 1], 'master')

    def test_a_refused_create_is_an_error(self) -> None:
        self.responses = [self._result(stdout=''),
                          self._result(returncode=1, stderr='gh: not authenticated')]
        self.assertNotEqual(scripts._ensure_pull_request('user/t-000000'), 0)


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


class GitFilterCommandTest(_GitCommandCase):
    """The explicit wire-the-filter command (the key-reconstruct aftermath)."""

    def setUp(self) -> None:
        super().setUp()
        self._saved_run_proc = scripts.run
        self.dirty = ''

        def fake_run(*_a: Any, **_k: Any) -> Any:
            return MagicMock(returncode=0, stdout=self.dirty)
        scripts.run = fake_run                      # type: ignore[assignment]

    def tearDown(self) -> None:
        scripts.run = self._saved_run_proc          # type: ignore[assignment]
        super().tearDown()

    def test_status_is_a_passthrough(self) -> None:
        self.assertEqual(scripts.git_filter(), 0)
        self.assertEqual(len(self.cmdlines), 1)
        self.assertIn('gitfilter status', self.cmdlines[0])

    def test_install_wires_then_rechecks_out(self) -> None:
        self.assertEqual(scripts.git_filter('install'), 0)
        self.assertEqual(len(self.cmdlines), 2)
        self.assertIn('gitfilter install', self.cmdlines[0])
        self.assertIn('git checkout -- solutions/private', self.cmdlines[1])

    def test_refused_install_stops_before_the_recheckout(self) -> None:
        self.rcs = [1]                              # not key-authorized: install refuses
        self.assertEqual(scripts.git_filter('install'), 1)
        self.assertEqual(len(self.cmdlines), 1)

    def test_local_private_edits_skip_the_recheckout(self) -> None:
        self.dirty = ' M solutions/private/p0101/x.py'
        self.assertEqual(scripts.git_filter('install'), 0)
        self.assertEqual(len(self.cmdlines), 1)     # wired, but nothing clobbered


class EncKeyPullFlowTest(_GitCommandCase):
    """The sync tail: wire the filter exactly when unwired AND key-authorized."""

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
