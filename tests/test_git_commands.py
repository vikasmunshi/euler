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
from solver.core import git
from solver.utils.loader import load_commands
from tests import silence

silence()   # the command tests drive console error/progress paths on purpose


def _subject(profile: str) -> Subject:
    return Subject(user='t@example.com', slug='t-000000', channel='web', auth_method='test',
                   profile=profile)


class PolicyShapeTest(unittest.TestCase):
    """The git floors: read for every rung, write for contributor+, master at admin."""

    def test_floors_of_the_git_commands(self) -> None:
        load_commands()
        expected = {'git-status': 'reader', 'git-sync': 'reader', 'git-filter': 'reader',
                    'git-commit': 'contributor', 'git-commit-amend': 'contributor',
                    'git-reset': 'contributor',
                    'git-push': 'contributor', 'git-hooks': 'contributor',
                    'git-identity': 'contributor', 'gh-merge': 'maintainer',
                    'git-commit-docs': 'maintainer', 'gh-merge-docs': 'maintainer',
                    'git-publish': 'admin'}
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

        self._saved_run = git.run_cmdline
        self._saved_branch = git._current_branch
        self._saved_pr = git._ensure_pull_request
        self._saved_subject = config.subject
        self._saved_emit = git.osc.emit
        git.run_cmdline = fake_run_cmdline      # type: ignore[assignment]
        git._current_branch = lambda: self.branch  # type: ignore[assignment]
        # git-push opens a PR, which reaches the GitHub API through `gh` — recorded here
        # like run_cmdline, so no test can touch a real remote (module docstring).
        git._ensure_pull_request = fake_ensure_pr  # type: ignore[assignment]
        # The subject is web-channel, so the commands' osc.git_changed() nudges would
        # write raw OSC 5379 escape sequences to the test's stdout. This suite is not
        # the OSC wire's test (that is test_web_channel) — swallow the emit.
        git.osc.emit = lambda *a, **k: None     # type: ignore[assignment]

    def tearDown(self) -> None:
        git.run_cmdline = self._saved_run       # type: ignore[assignment]
        git._current_branch = self._saved_branch  # type: ignore[assignment]
        git._ensure_pull_request = self._saved_pr  # type: ignore[assignment]
        git.osc.emit = self._saved_emit         # type: ignore[assignment]
        config.subject = self._saved_subject

    def as_profile(self, profile: str) -> None:
        config.subject = _subject(profile)


class GitPushGuardTest(_GitCommandCase):
    def test_contributor_pushes_their_own_branch_and_opens_its_pr(self) -> None:
        self.as_profile('contributor')
        self.assertEqual(git.git_push(), 0)
        self.assertEqual(self.cmdlines, ['git push -u origin user/t-000000'])
        self.assertEqual(self.prs, ['user/t-000000'])

    def test_force_uses_force_with_lease(self) -> None:
        self.as_profile('contributor')
        self.assertEqual(git.git_push(force=True), 0)
        self.assertEqual(self.cmdlines, ['git push -u --force-with-lease origin user/t-000000'])

    def test_no_pr_pushes_and_stops(self) -> None:
        self.as_profile('contributor')
        self.assertEqual(git.git_push(pr=False), 0)
        self.assertEqual(self.cmdlines, ['git push -u origin user/t-000000'])
        self.assertEqual(self.prs, [])

    def test_a_failed_push_never_opens_a_pr(self) -> None:
        self.as_profile('contributor')
        self.rcs = [1]
        self.assertNotEqual(git.git_push(), 0)
        self.assertEqual(self.prs, [])              # nothing to review — the branch never landed

    def test_a_failed_pr_fails_the_command(self) -> None:
        # The push succeeded, but git-push promises a PR: reporting success would leave
        # the user believing their work is under review when it is not.
        self.as_profile('contributor')
        self.pr_rc = 1
        self.assertNotEqual(git.git_push(), 0)

    def test_non_admin_cannot_push_master(self) -> None:
        self.branch = 'master'
        self.as_profile('contributor')
        self.assertEqual(git.git_push(), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])         # refused before any git ran

    def test_admin_may_push_master_but_never_forced(self) -> None:
        self.branch = 'master'
        self.as_profile('admin')
        self.assertEqual(git.git_push(), 0)
        self.assertEqual(self.cmdlines, ['git push -u origin master'])
        self.assertEqual(self.prs, [])              # master has nothing to merge into itself
        self.cmdlines.clear()
        self.assertEqual(git.git_push(force=True), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])

    def test_detached_head_is_refused(self) -> None:
        self.branch = 'HEAD'
        self.as_profile('admin')
        self.assertEqual(git.git_push(), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])


class GitResetTest(_GitCommandCase):
    """git-reset: a soft reset to origin/master — un-commit, keep the changes, no commit.

    The count that sizes the report is faked at the `run` boundary; the reset itself is
    recorded through run_cmdline like every other verb, so no test touches the repo.
    """

    def setUp(self) -> None:
        super().setUp()
        self.ahead: str = '2\n'                     # commits `git rev-list --count` reports
        self._saved_run_proc = git.run

        def fake_run(argv: list[str], **kwargs: Any) -> Any:
            return MagicMock(returncode=0, stdout=self.ahead)

        git.run = fake_run                          # type: ignore[assignment]
        self.addCleanup(lambda: setattr(git, 'run', self._saved_run_proc))
        self.as_profile('contributor')

    def test_it_soft_resets_to_origin_master(self) -> None:
        self.assertEqual(git.git_reset(), 0)
        self.assertEqual(self.cmdlines, ['git reset --soft origin/master'])

    def test_it_makes_no_commit(self) -> None:
        """The whole point vs `git-commit --reset`: one command, and it is the reset."""
        git.git_reset()
        self.assertEqual(len(self.cmdlines), 1)
        self.assertNotIn('commit', self.cmdlines[0])

    def test_a_level_branch_is_a_clean_noop(self) -> None:
        # Zero commits ahead: the reset still runs (a no-op in git) and exits 0.
        self.ahead = '0\n'
        self.assertEqual(git.git_reset(), 0)
        self.assertEqual(self.cmdlines, ['git reset --soft origin/master'])

    def test_an_unreadable_count_does_not_break_the_reset(self) -> None:
        # _commits_ahead_of_master returns 0 on any failure; the reset is unaffected.
        self.ahead = 'not-a-number'
        self.assertEqual(git.git_reset(), 0)
        self.assertEqual(self.cmdlines, ['git reset --soft origin/master'])

    def test_a_failed_reset_is_reported(self) -> None:
        self.rcs = [1]
        self.assertNotEqual(git.git_reset(), 0)


class PullRequestTest(unittest.TestCase):
    """`_ensure_pull_request`: idempotent, and never a second PR for one branch.

    `gh` is stubbed at the `run` boundary — the real GitHub API is never reached (module
    docstring), which is exactly the invariant a PR-opening command could quietly break.
    """

    def setUp(self) -> None:
        self.calls: list[list[str]] = []
        self._saved_run = git.run

        def fake_run(argv: list[str], **kwargs: Any) -> Any:
            self.calls.append(argv)
            return self.responses.pop(0)

        git.run = fake_run                      # type: ignore[assignment]
        self.responses: list[Any] = []
        self.addCleanup(lambda: setattr(git, 'run', self._saved_run))

    @staticmethod
    def _result(returncode: int = 0, stdout: str = '', stderr: str = '') -> Any:
        return MagicMock(returncode=returncode, stdout=stdout, stderr=stderr)

    # Every response queue starts with the `git rev-list --count` that `_commits_ahead`
    # runs first: a branch level with origin/master gets no pull request at all.
    def test_an_open_pr_is_reported_not_duplicated(self) -> None:
        self.responses = [self._result(stdout='2\n'),           # 2 commits beyond master
                          self._result(stdout='https://github.com/o/r/pull/7\n')]
        self.assertEqual(git._ensure_pull_request('user/t-000000'), 0)
        self.assertEqual(len(self.calls), 2)                    # the count and the lookup
        self.assertEqual(self.calls[1][:3], ['gh', 'pr', 'view'])

    def test_no_open_pr_opens_one_onto_master(self) -> None:
        self.responses = [self._result(stdout='1\n'),           # 1 commit beyond master
                          self._result(stdout=''),              # lookup: none open
                          self._result(stdout='https://github.com/o/r/pull/8\n')]
        self.assertEqual(git._ensure_pull_request('user/t-000000'), 0)
        created = self.calls[2]
        self.assertEqual(created[:3], ['gh', 'pr', 'create'])
        self.assertEqual(created[created.index('--head') + 1], 'user/t-000000')
        self.assertEqual(created[created.index('--base') + 1], 'master')

    def test_a_refused_create_is_an_error(self) -> None:
        self.responses = [self._result(stdout='1\n'),
                          self._result(stdout=''),
                          self._result(returncode=1, stderr='gh: not authenticated')]
        self.assertNotEqual(git._ensure_pull_request('user/t-000000'), 0)

    def test_a_branch_level_with_master_is_never_asked_to_be_reviewed(self) -> None:
        # Nothing to review, and GitHub refuses such a PR outright ("No commits
        # between ..."): a no-op, not a failure — and gh is never reached.
        self.responses = [self._result(stdout='0\n')]
        self.assertEqual(git._ensure_pull_request('user/t-000000'), 0)
        self.assertEqual(len(self.calls), 1)

    def test_an_unknown_ahead_count_still_tries_the_pr(self) -> None:
        # `_commits_ahead` returns None when it cannot compare (no origin/master, or
        # the branch never reached origin). That is not "nothing to review": refusing
        # here would silently drop the PR for a branch that has work on it.
        self.responses = [self._result(returncode=1),           # rev-list: cannot tell
                          self._result(stdout=''),              # lookup: none open
                          self._result(stdout='https://github.com/o/r/pull/9\n')]
        self.assertEqual(git._ensure_pull_request('user/t-000000'), 0)
        self.assertEqual(self.calls[2][:3], ['gh', 'pr', 'create'])


class GhPrTest(_GitCommandCase):
    """The gate to master: a maintainer merges a pull request, and only a
    solutions-only one. The file list is what is judged, so it is what is faked.
    `merge` itself walks the open PRs interactively (like `users process-requests`):
    the queue and the keypresses are faked so no test touches a real remote or stdin."""

    def setUp(self) -> None:
        super().setUp()
        self.files: list[str] | None = ['solutions/private/p0200_0299/p0217/p0217_s0.py',
                                        'solutions/problems.json']
        self.open_prs: list[dict[str, object]] | None = [
            {'number': 12, 'title': 'Publish user/x', 'headRefName': 'user/x'}]
        self.answers: list[str] = []
        self._saved_pr_files = git._pr_files
        self._saved_open_prs = git._open_prs
        self._saved_input = git.console.input
        git._pr_files = lambda number: self.files  # type: ignore[assignment]
        git._open_prs = lambda: self.open_prs      # type: ignore[assignment]
        # Each prompt consumes the next queued keypress; an empty queue quits the walk.
        git.console.input = lambda *a, **k: self.answers.pop(0) if self.answers else 'q'  # type: ignore[assignment]

    def tearDown(self) -> None:
        git._pr_files = self._saved_pr_files    # type: ignore[assignment]
        git._open_prs = self._saved_open_prs    # type: ignore[assignment]
        git.console.input = self._saved_input   # type: ignore[assignment]
        super().tearDown()

    def test_list_is_the_default_action(self) -> None:
        self.as_profile('maintainer')
        self.assertEqual(git.gh_merge(), 0)
        self.assertEqual(self.cmdlines, ['gh pr list'])

    # ── the file gate (_merge_pr), judged on the PR's file list ──
    def test_a_solutions_only_pr_is_rebase_merged(self) -> None:
        self.as_profile('maintainer')
        self.assertEqual(git._merge_pr(12), 0)
        self.assertEqual(self.cmdlines, ['gh pr merge 12 --rebase --admin'])

    def test_a_pr_touching_anything_else_is_refused(self) -> None:
        self.as_profile('maintainer')
        self.files = ['solutions/public/p0042/p0042_s0.py', 'solver/utils/scripts.py']
        self.assertEqual(git._merge_pr(12), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])         # refused before gh ran

    def test_a_topics_only_pr_is_rebase_merged_too(self) -> None:
        """Topic articles are the other content tree a collaborator authors (PR_SCOPE)."""
        self.as_profile('maintainer')
        self.files = ['topics/technique/sieve-of-eratosthenes.md', 'topics/articles.json']
        self.assertEqual(git._merge_pr(12), 0)
        self.assertEqual(self.cmdlines, ['gh pr merge 12 --rebase --admin'])

    def test_a_pr_spanning_both_trees_is_refused(self) -> None:
        """Either tree, never both: solving a problem and writing an article are two reviews."""
        self.as_profile('maintainer')
        self.files = ['solutions/public/p0042/p0042_s0.py', 'topics/technique/memoization.md']
        self.assertEqual(git._merge_pr(12), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])         # refused before gh ran

    def test_a_lookalike_path_does_not_pass_for_solutions(self) -> None:
        # 'solutions-of-mine/x' starts with 'solutions' but is not under solutions/;
        # likewise 'topics.md' for topics/ — the scope is prefixes, not name stems.
        self.as_profile('maintainer')
        self.files = ['solutions-of-mine/x.py']
        self.assertEqual(git._merge_pr(12), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])
        self.files = ['topics.md']
        self.assertEqual(git._merge_pr(12), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])

    def test_an_unreadable_file_list_is_never_read_as_empty(self) -> None:
        # None is 'gh could not tell us', not 'touches nothing outside solutions/'.
        self.as_profile('maintainer')
        self.files = None
        self.assertEqual(git._merge_pr(12), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])

    def test_an_empty_file_list_is_refused(self) -> None:
        self.as_profile('maintainer')
        self.files = []
        self.assertEqual(git._merge_pr(12), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])

    # ── the interactive walk (gh-merge merge → _merge_walk) ──
    def test_merge_walks_and_merges_on_m(self) -> None:
        self.as_profile('maintainer')
        self.answers = ['m']
        self.assertEqual(git.gh_merge('merge'), 0)
        self.assertEqual(self.cmdlines, ['gh pr merge 12 --rebase --admin'])

    def test_skip_leaves_the_pr_untouched(self) -> None:
        self.as_profile('maintainer')
        self.answers = ['s']
        self.assertEqual(git.gh_merge('merge'), 0)
        self.assertEqual(self.cmdlines, [])

    def test_quit_stops_the_walk_before_later_prs(self) -> None:
        self.as_profile('maintainer')
        self.open_prs = [{'number': 12, 'title': 'a', 'headRefName': 'user/x'},
                         {'number': 13, 'title': 'b', 'headRefName': 'user/y'}]
        self.answers = ['q']
        self.assertEqual(git.gh_merge('merge'), 0)
        self.assertEqual(self.cmdlines, [])

    def test_no_open_prs_is_a_clean_noop(self) -> None:
        self.as_profile('maintainer')
        self.open_prs = []
        self.assertEqual(git.gh_merge('merge'), 0)
        self.assertEqual(self.cmdlines, [])

    def test_an_unreadable_pr_list_errors(self) -> None:
        # None is 'gh could not tell us', not 'the queue is empty' — never a silent 0.
        self.as_profile('maintainer')
        self.open_prs = None
        self.assertEqual(git.gh_merge('merge'), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])

    # ── the docs gate (gh-merge-docs), disjoint from the content one ──
    def test_a_docs_pr_merges_through_the_docs_gate(self) -> None:
        """The docs set is one body of work: a regeneration touching all of it merges whole."""
        self.as_profile('maintainer')
        self.files = ['docs/user-guide.md', 'topics/articles.json', 'README.md',
                      'solver/modules.csv', 'solver/config.json', 'solver/ai/claude/CLAUDE.md']
        self.answers = ['m']
        self.assertEqual(git.gh_merge_docs(), 0)
        self.assertEqual(self.cmdlines, ['gh pr merge 12 --rebase --admin'])

    def test_the_two_gates_refuse_each_other(self) -> None:
        """Whichever verb you reach for names the review you are doing."""
        self.as_profile('maintainer')
        self.files = ['docs/user-guide.md']
        self.assertEqual(git._merge_pr(12), ExitCodes.EXIT_ERROR)            # docs via gh-merge
        self.files = ['solutions/public/p0042/p0042_s0.py']
        self.answers = ['m']
        self.assertEqual(git.gh_merge_docs(), 0)                            # the walk survives…
        self.assertEqual(self.cmdlines, [])                                  # …but nothing merged

    def test_the_docs_gate_admits_only_the_named_files_under_solver(self) -> None:
        """`solver/config.json` is in scope; the `solver/` tree around it is not."""
        self.as_profile('maintainer')
        self.answers = ['m']
        self.files = ['solver/config.py']
        self.assertEqual(git.gh_merge_docs(), 0)
        self.assertEqual(self.cmdlines, [])                                  # refused
        self.files = ['solver/config.json']
        self.answers = ['m']
        self.assertEqual(git.gh_merge_docs(), 0)
        self.assertEqual(self.cmdlines, ['gh pr merge 12 --rebase --admin'])

    def test_the_docs_gate_reaches_the_tag_leg_but_not_the_solution_beside_it(self) -> None:
        """`update-tags` writes each problem's tags.json, so a reconciliation must merge —
        while the solution file next to it stays a solutions review."""
        self.as_profile('maintainer')
        self.files = ['solutions/public/p0042/tags.json',
                      'solutions/private/p0100_0199/p0101/tags.json', 'topics/tags.json']
        self.answers = ['m']
        self.assertEqual(git.gh_merge_docs(), 0)
        self.assertEqual(self.cmdlines, ['gh pr merge 12 --rebase --admin'])
        self.cmdlines.clear()
        self.files = ['solutions/public/p0042/tags.json', 'solutions/public/p0042/p0042_s0.py']
        self.answers = ['m']
        self.assertEqual(git.gh_merge_docs(), 0)
        self.assertEqual(self.cmdlines, [])                                  # refused


class GitFilterCommandTest(_GitCommandCase):
    """The explicit wire-the-filter command (the key-reconstruct aftermath)."""

    def setUp(self) -> None:
        super().setUp()
        self._saved_run_proc = git.run
        self.dirty = ''

        def fake_run(*_a: Any, **_k: Any) -> Any:
            return MagicMock(returncode=0, stdout=self.dirty)
        git.run = fake_run                      # type: ignore[assignment]

    def tearDown(self) -> None:
        git.run = self._saved_run_proc          # type: ignore[assignment]
        super().tearDown()

    def test_status_is_a_passthrough(self) -> None:
        self.assertEqual(git.git_filter(), 0)
        self.assertEqual(len(self.cmdlines), 1)
        self.assertIn('gitfilter status', self.cmdlines[0])

    def test_install_wires_then_rechecks_out(self) -> None:
        self.assertEqual(git.git_filter('install'), 0)
        self.assertEqual(len(self.cmdlines), 2)
        self.assertIn('gitfilter install', self.cmdlines[0])
        self.assertIn('git checkout -- solutions/private', self.cmdlines[1])

    def test_refused_install_stops_before_the_recheckout(self) -> None:
        self.rcs = [1]                              # not key-authorized: install refuses
        self.assertEqual(git.git_filter('install'), 1)
        self.assertEqual(len(self.cmdlines), 1)

    def test_local_private_edits_skip_the_recheckout(self) -> None:
        self.dirty = ' M solutions/private/p0101/x.py'
        self.assertEqual(git.git_filter('install'), 0)
        self.assertEqual(len(self.cmdlines), 1)     # wired, but nothing clobbered


class EncKeyPullFlowTest(_GitCommandCase):
    """The sync tail: wire the filter exactly when unwired AND key-authorized."""

    def setUp(self) -> None:
        super().setUp()
        self._saved_master = git.read_master_key
        self._saved_run_proc = git.run
        self.master = MagicMock(return_value=b'\x00' * 32)
        self.master.cache_clear = MagicMock()
        git.read_master_key = self.master       # type: ignore[assignment]

    def tearDown(self) -> None:
        git.read_master_key = self._saved_master  # type: ignore[assignment]
        git.run = self._saved_run_proc          # type: ignore[assignment]
        super().tearDown()

    def _wire_state(self, wired: bool) -> None:
        def fake_run(*_a: Any, **_k: Any) -> Any:
            return MagicMock(returncode=0 if wired else 1)
        git.run = fake_run                      # type: ignore[assignment]

    def test_already_wired_is_a_silent_noop(self) -> None:
        self._wire_state(wired=True)
        git._enc_key_pull_flow()
        self.assertEqual(self.cmdlines, [])
        self.master.assert_not_called()

    def test_unauthorized_is_a_silent_noop(self) -> None:
        self._wire_state(wired=False)
        self.master.side_effect = KeyError('no entry for this public key')
        git._enc_key_pull_flow()
        self.assertEqual(self.cmdlines, [])

    def test_newly_authorized_wires_and_rechecks_out(self) -> None:
        self._wire_state(wired=False)
        git._enc_key_pull_flow()
        self.master.cache_clear.assert_called_once()    # the pull may have delivered access
        self.assertEqual(len(self.cmdlines), 2)
        self.assertIn('solver.crypto.gitfilter install', self.cmdlines[0])
        self.assertIn('git checkout -- solutions/private', self.cmdlines[1])

    def test_failed_install_skips_the_recheckout(self) -> None:
        self._wire_state(wired=False)
        self.rcs = [1]                              # install refused (key check failed late)
        git._enc_key_pull_flow()
        self.assertEqual(len(self.cmdlines), 1)


class CanAmendTest(unittest.TestCase):
    """`_can_amend`: True only for an unpushed HEAD with dirty paths — decided quietly.

    The three preconditions are read at the `run`/`_remotes_containing_head` boundary,
    each stubbed so no real git runs. What matters is that every reason amend must be
    refused (no HEAD, a pushed HEAD, an undecidable push state, a clean tree) comes back
    False — that is what keeps the loud `git-commit-amend` off an empty-message commit's
    recovery path.
    """

    def setUp(self) -> None:
        self.head_rc: int = 0                       # rev-parse HEAD: 0 = a commit exists
        self.pushed: list[str] | None = []          # _remotes_containing_head: [] = unpushed
        self.status: str = ' M solutions/public/p0218/p0218_s0.py'

        def fake_run(argv: list[str], **_k: Any) -> Any:
            if 'rev-parse' in argv:
                return MagicMock(returncode=self.head_rc)
            if 'status' in argv:
                return MagicMock(returncode=0, stdout=self.status)
            raise AssertionError(f'unexpected run: {argv}')

        self._saved_run = git.run
        self._saved_remotes = git._remotes_containing_head
        self._saved_paths = git._commit_paths
        git.run = fake_run                       # type: ignore[assignment]
        git._remotes_containing_head = lambda: self.pushed  # type: ignore[assignment]
        git._commit_paths = lambda problem: ['solutions/public/p0218']  # type: ignore[assignment]
        self.problem: Any = MagicMock(number=218)

    def tearDown(self) -> None:
        git.run = self._saved_run                # type: ignore[assignment]
        git._remotes_containing_head = self._saved_remotes  # type: ignore[assignment]
        git._commit_paths = self._saved_paths    # type: ignore[assignment]

    def test_unpushed_head_with_dirty_paths_can_amend(self) -> None:
        self.assertTrue(git._can_amend(self.problem))

    def test_no_head_cannot_amend(self) -> None:
        self.head_rc = 1                             # no commit to amend yet
        self.assertFalse(git._can_amend(self.problem))

    def test_a_pushed_head_cannot_amend(self) -> None:
        self.pushed = ['origin/user/t-000000']       # on origin — amending would force-push
        self.assertFalse(git._can_amend(self.problem))

    def test_an_undecidable_push_state_cannot_amend(self) -> None:
        self.pushed = None                           # cannot tell — never assume unpushed
        self.assertFalse(git._can_amend(self.problem))

    def test_clean_paths_cannot_amend(self) -> None:
        self.status = ''                             # nothing under this problem changed
        self.assertFalse(git._can_amend(self.problem))


class GitCommitDispatchTest(_GitCommandCase):
    """git-commit's empty-message dispatch: amend when it can, `--reset` suppresses it,
    an explicit message never amends. `_can_amend` and `git-commit-amend` are stubbed —
    the predicate has its own test; this pins which branch git-commit takes."""

    _FRESH = 'git add -A solutions/public/p0218 && git commit --message "solution for p0218"'

    def setUp(self) -> None:
        super().setUp()
        self.amendable: bool = True
        self.amend_rc: int = 0
        self.amend_calls: int = 0

        def fake_amend(problem: Any) -> int:
            self.amend_calls += 1
            return self.amend_rc

        self._saved_can_amend = git._can_amend
        self._saved_amend = git.git_commit_amend
        self._saved_paths = git._commit_paths
        git._can_amend = lambda problem: self.amendable  # type: ignore[assignment]
        git.git_commit_amend = fake_amend        # type: ignore[assignment]
        git._commit_paths = lambda problem: ['solutions/public/p0218']  # type: ignore[assignment]
        self.as_profile('contributor')
        self.problem: Any = MagicMock(number=218)

    def tearDown(self) -> None:
        git._can_amend = self._saved_can_amend   # type: ignore[assignment]
        git.git_commit_amend = self._saved_amend  # type: ignore[assignment]
        git._commit_paths = self._saved_paths    # type: ignore[assignment]
        super().tearDown()

    def test_empty_message_amends_when_it_can(self) -> None:
        self.assertEqual(git.git_commit(self.problem), 0)
        self.assertEqual(self.amend_calls, 1)
        self.assertEqual(self.cmdlines, [])          # folded into HEAD; no fresh commit ran

    def test_a_failing_amend_is_returned_not_retried_as_fresh(self) -> None:
        self.amend_rc = ExitCodes.EXIT_ERROR         # _can_amend said yes, so trust the amend
        self.assertEqual(git.git_commit(self.problem), ExitCodes.EXIT_ERROR)
        self.assertEqual(self.cmdlines, [])          # never a second, fresh commit

    def test_empty_message_commits_fresh_when_it_cannot_amend(self) -> None:
        self.amendable = False
        self.assertEqual(git.git_commit(self.problem), 0)
        self.assertEqual(self.amend_calls, 0)
        self.assertEqual(self.cmdlines, [self._FRESH])

    def test_reset_suppresses_the_amend_even_when_it_could(self) -> None:
        self.amendable = True                        # amendable — but --reset must win
        self.assertEqual(git.git_commit(self.problem, reset=True), 0)
        self.assertEqual(self.amend_calls, 0)
        self.assertEqual(self.cmdlines, ['git reset --soft origin/master && ' + self._FRESH])

    def test_an_explicit_message_never_amends(self) -> None:
        self.assertEqual(git.git_commit(self.problem, 'hand-written'), 0)
        self.assertEqual(self.amend_calls, 0)
        self.assertEqual(self.cmdlines,
                         ['git add -A solutions/public/p0218 && git commit --message "hand-written"'])


class GitCommitDocsTest(_GitCommandCase):
    """git-commit-docs: the docs set, the `(docs)` tag, and the clean no-op.

    The `git status` probe is stubbed, so what is pinned is the command line the verb
    builds — which paths it stages, and with what message."""

    def setUp(self) -> None:
        super().setUp()
        self.dirty: str = ' M docs/user-guide.md'

        def fake_run(argv: list[str], **_k: Any) -> Any:
            assert 'status' in argv, f'unexpected run: {argv}'
            return MagicMock(returncode=0, stdout=self.dirty)

        self._saved_run_proc = git.run
        git.run = fake_run                       # type: ignore[assignment]
        self.addCleanup(lambda: setattr(git, 'run', self._saved_run_proc))
        self.as_profile('maintainer')

    def test_it_stages_exactly_the_docs_set(self) -> None:
        """The glob leg carries git's explicit :(glob) magic, and is quoted for the shell."""
        self.assertEqual(git.git_commit_docs('regenerate'), 0)
        self.assertEqual(self.cmdlines, [
            'git add -A docs/ topics/ README.md solver/modules.csv solver/config.json '
            'solver/ai/models.py solver/ai/claude/CLAUDE.md solver/web/content/home-summary.md '
            "':(glob)solutions/**/tags.json' && git commit --message \"docs(topic): regenerate\""])

    def test_the_message_is_tagged_once(self) -> None:
        git.git_commit_docs('docs(topic): already tagged')
        self.assertIn('--message "docs(topic): already tagged"', self.cmdlines[0])

    def test_an_empty_message_becomes_the_default(self) -> None:
        git.git_commit_docs()
        self.assertIn('--message "docs(topic): update"', self.cmdlines[0])

    def test_a_clean_docs_set_is_a_noop_not_a_failure(self) -> None:
        """It composes in a `&&` chain after a regeneration that had nothing to do."""
        self.dirty = ''
        self.assertEqual(git.git_commit_docs('nothing to say'), 0)
        self.assertEqual(self.cmdlines, [])

    def test_reset_squashes_to_origin_first(self) -> None:
        self.assertEqual(git.git_commit_docs('checkpoint', reset=True), 0)
        self.assertTrue(self.cmdlines[0].startswith('git reset --soft origin/master && git add -A'))

    def test_reset_runs_even_on_a_clean_set(self) -> None:
        """--reset is about squashing the local commits, not about the working tree."""
        self.dirty = ''
        self.assertEqual(git.git_commit_docs('squash', reset=True), 0)
        self.assertEqual(len(self.cmdlines), 1)


if __name__ == '__main__':
    unittest.main()
