#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the ``.gitattributes`` rule the crypt filter is wired by.

The rule is **tracked** — it ships in the repo, so a fresh clone already carries it and
``gitfilter install`` should only ever *recognise* it. The regression these tests pin is
what happens when it does not: ``-diff`` was added to the tracked rule without updating
``crypto.config['attr_line']``, the installer's exact-line match failed, and it appended a
second — weaker, `-diff`-less — copy of the same rule to a tracked file. Every
collaborator clone then reported a modified ``.gitattributes`` after ``git-sync``.

Two guards, for the two halves of that failure:

- the constant must equal the tracked rule, so the fallback write produces the current
  rule and nothing drifts silently again;
- the matcher must recognise the rule by its **meaning** (path + ``filter=<name>``), so a
  future flag change is a non-event rather than a duplicated line.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from solver.crypto.config import config as crypto_config
from solver.crypto.gitfilter import _rule_present, filter_settings

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TRACKED_ATTRS = _REPO_ROOT / '.gitattributes'


class AttrLineMatchesTheTrackedRuleTests(unittest.TestCase):
    """The constant and the tracked file are one fact; they must not drift apart."""

    def test_attr_line_is_a_line_of_the_tracked_gitattributes(self) -> None:
        lines = _TRACKED_ATTRS.read_text(encoding='utf-8').splitlines()
        self.assertIn(crypto_config['attr_line'], lines,
                      'crypto.config attr_line has drifted from the tracked .gitattributes '
                      'rule — the installer will append a duplicate to a tracked file')

    def test_attr_path_prefixes_attr_line(self) -> None:
        self.assertTrue(crypto_config['attr_line'].startswith(crypto_config['attr_path'] + ' '))

    def test_the_tracked_rule_is_recognised(self) -> None:
        self.assertTrue(_rule_present(_TRACKED_ATTRS))


class RulePresentTests(unittest.TestCase):
    """The matcher reads the rule's meaning, not its exact text."""

    def setUp(self) -> None:
        self.scratch = Path(tempfile.mkdtemp(prefix='euler-attrs-'))
        self.addCleanup(__import__('shutil').rmtree, self.scratch, True)

    def _wrote(self, text: str) -> Path:
        path = self.scratch / '.gitattributes'
        path.write_text(text, encoding='utf-8')
        return path

    def test_the_rule_without_diff_still_counts(self) -> None:
        """A tree predating `-diff` is already wired; re-appending would be the bug."""
        self.assertTrue(_rule_present(self._wrote('solutions/private/** filter=solver-crypt -text\n')))

    def test_flags_may_be_reordered_or_added(self) -> None:
        self.assertTrue(_rule_present(
            self._wrote('solutions/private/**\t-text\tfilter=solver-crypt\t-diff\n')))

    def test_the_duplicated_file_is_recognised_not_appended_to_again(self) -> None:
        """The exact state a collaborator clone was left in — it must now be a no-op."""
        self.assertTrue(_rule_present(self._wrote(
            '# Transparent encryption for private solutions (solver.crypto.gitfilter).\n'
            'solutions/private/** filter=solver-crypt -text -diff\n'
            '# Transparent encryption for private solutions (solver.crypto.gitfilter).\n'
            'solutions/private/** filter=solver-crypt -text\n')))

    def test_a_commented_rule_does_not_count(self) -> None:
        self.assertFalse(_rule_present(
            self._wrote('# solutions/private/** filter=solver-crypt -text -diff\n')))

    def test_another_filter_on_the_same_path_does_not_count(self) -> None:
        self.assertFalse(_rule_present(
            self._wrote('solutions/private/** filter=something-else -text\n')))

    def test_this_filter_on_another_path_does_not_count(self) -> None:
        self.assertFalse(_rule_present(
            self._wrote('solutions/public/** filter=solver-crypt -text\n')))

    def test_empty_and_absent_read_as_not_wired(self) -> None:
        self.assertFalse(_rule_present(self._wrote('')))
        self.assertFalse(_rule_present(self.scratch / 'does-not-exist'))


if __name__ == '__main__':
    unittest.main()


class FilterCommandTests(unittest.TestCase):
    """The command git records for the filter must not be shadowed by the worktree.

    git runs a filter with the cwd at the **top of the worktree**, and a solver checkout has
    a `solver/` package sitting right there — so `python -m solver.crypto.gitfilter` imports
    the *clone's* source instead of the venv's installed copy. That is not theoretical: three
    readers whose clones were behind ran an old filter against a current key file and could
    not decrypt, while their shell (a console script, sane sys.path) reported the key as
    available. `-P` (PYTHONSAFEPATH) is what keeps the two agreeing.
    """

    def test_every_recorded_command_is_import_safe(self) -> None:
        for setting, command in filter_settings('solver-crypt').items():
            if setting.endswith('.required'):
                continue
            self.assertIn(' -P -m solver.crypto.gitfilter', command, setting)
