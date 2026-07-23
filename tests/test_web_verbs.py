#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Every command the web UI types into the terminal must be a real command.

The web shell is the front door: a menu verb, a git-chip action, or a topic Action does not
call a handler — it types a command string into the PTY and lets the shell answer. So a rename
like `gh-pr` → `gh-merge` that misses a template leaves a button that silently does nothing (the
shell rejects the unknown command). This scans every terminal command the site can emit —
`data-term-cmd` literals, the git menu's `verb()` macro, and `Action(kind='term')` handler
commands — and checks each leading token resolves in the command registry.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from solver.shell.command import registry
from solver.utils.loader import load_commands

_ROOT = Path(__file__).resolve().parents[1]
_SITE = _ROOT / 'solver' / 'web'

#: A literal `data-term-cmd="git-sync"` (skip the Jinja-interpolated `{{ … }}` ones).
_TERM_CMD_RE = re.compile(r'data-term-cmd="([^"{}]+)"')
#: The git menu's macro: `{{ verb('Sync with master', 'git-sync', 'reader') }}`.
_VERB_RE = re.compile(r"verb\(\s*'[^']*'\s*,\s*'([^']+)'")
#: An `Action(kind='term', command=f'claude-blog {name}')` — take the static prefix, which is
#: the command and any literal flags before the first `{…}` interpolation.
_ACTION_CMD_RE = re.compile(r"kind='term',\s*command=f?['\"]([^'\"{}]+)")


def _emitted_commands() -> set[str]:
    commands: set[str] = set()
    for path in _SITE.rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        commands.update(_TERM_CMD_RE.findall(text))
        commands.update(_VERB_RE.findall(text))
    for path in _SITE.rglob('*.py'):
        commands.update(_ACTION_CMD_RE.findall(path.read_text(encoding='utf-8')))
    return {c.strip() for c in commands if c.strip()}


class WebTerminalVerbTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_commands()                         # populate the registry from modules.csv

    def test_every_emitted_verb_is_a_real_command(self) -> None:
        emitted = _emitted_commands()
        self.assertTrue(emitted, 'found no terminal verbs to check — the extractor is broken')
        unknown = sorted(cmd for cmd in emitted if registry.resolve(cmd.split()[0]) is None)
        self.assertEqual(unknown, [], f'web UI emits commands the shell does not register: {unknown}')

    def test_the_extractor_sees_the_known_verbs(self) -> None:
        """A guard on the guard: if a refactor stops the regexes matching, the test above would
        pass vacuously. Pin a few commands we know the UI emits."""
        emitted = {c.split()[0] for c in _emitted_commands()}
        for expected in ('git-sync', 'gh-merge', 'claude-blog'):
            self.assertIn(expected, emitted)


if __name__ == '__main__':
    unittest.main()
