#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The header's chips: the commands they emit, and the shape they emit them in.

Every command the web UI types into the terminal must be a real command.

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

#: A `data-term-cmd="git-sync"`, or the **static prefix** of an interpolated one
#: (`data-term-cmd="user-authorize {{ item.id }}"` → `user-authorize`) — the same treatment
#: the Action regex below gives its f-strings. Taking only the literal head is what lets the
#: check reach the row verbs, whose argument is a runtime id; a fully interpolated value
#: (`data-term-cmd="{{ command }}"`, the git macro) yields an empty prefix and drops out.
_TERM_CMD_RE = re.compile(r'data-term-cmd="([^"{}]*)')
#: The git menu's macro: `{{ verb('Sync with master', 'git-sync', 'reader') }}`.
_VERB_RE = re.compile(r"verb\(\s*'[^']*'\s*,\s*'([^']+)'")
#: An `Action(kind='term', command=f'claude-blog {name}')` — take the static prefix, which is
#: the command and any literal flags before the first `{…}` interpolation.
_ACTION_CMD_RE = re.compile(r"kind='term',\s*command=f?['\"]([^'\"{}]+)")
#: A row verb built in Python: `'verb': f'msg act {thread_id}'` (solver/web/user/msg_api.py).
#: The chip builds its rows' command in code, not in the template, so the two regexes above
#: stopped seeing it — silently dropping the row verbs out of this check. Anchored on a `verb`
#: binding (`verb =`, `verb, label =`, or the `'verb':` dict key) rather than on f-strings
#: generally: a loose rule would collect prose like f'requires {capability}' and turn the
#: guard into noise.
_VERB_ASSIGN_RE = re.compile(r"'?verb'?(?:,\s*\w+)?\s*[:=]\s*f'([^'{}]+)")


def _emitted_commands() -> set[str]:
    commands: set[str] = set()
    for path in _SITE.rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        commands.update(_TERM_CMD_RE.findall(text))
        commands.update(_VERB_RE.findall(text))
    for path in _SITE.rglob('*.py'):
        text = path.read_text(encoding='utf-8')
        commands.update(_ACTION_CMD_RE.findall(text))
        commands.update(_VERB_ASSIGN_RE.findall(text))
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
        # `user-authorize` used to be pinned here, back when a key-request row typed it. Every
        # message row now types `msg act <id>` and the command dispatches (verb_for), so the
        # UI no longer emits it — `msg` covers that path.
        for expected in ('git-sync', 'gh-merge', 'claude-blog', 'msg', 'user'):
            self.assertIn(expected, emitted)


class HeaderChipShapeTests(unittest.TestCase):
    """The three header chips, read straight from their templates.

    Not through an HTTP tier: the git and message chips render inert on the content service
    (no clone state, no spool) and the per-user fixture stubs `gitstate.read` to None, so a
    request-level test would assert against the empty shapes. What is under test here is the
    *markup* — the order of the git verbs, the message chip's triggers, the terminal chip's
    two acts — which is the thing these templates own.
    """

    @staticmethod
    def _template(name: str) -> str:
        return (_SITE / 'site' / 'templates' / name).read_text(encoding='utf-8')

    def test_the_git_menu_ends_with_the_undo_behind_a_separator(self) -> None:
        """Every other verb moves work forward — review, sync, commit, push, land — and this
        one takes a commit back. Mid-list it sat one slip below Commit; last, behind a
        separator, it reads as the undo it is."""
        menu = self._template('_git.html')
        reset = menu.index("'git-reset'")
        for earlier in ("'git-status --details'", "'git-sync'",
                        "'git-commit solution docs topics'", "'git-push'", "'gh-merge merge'"):
            self.assertLess(menu.index(earlier), reset, earlier)
        # The separator sits between the last forward verb and the undo, with nothing
        # between it and the reset row.
        # Exactly one verb call between the last separator and the reset row: its own.
        last_sep = menu[:reset].rindex('menu-sep')
        self.assertEqual(menu[last_sep:reset].count('{{ verb('), 1,
                         'the separator is the pause immediately before the undo')

    def test_the_message_chip_refreshes_when_it_is_opened(self) -> None:
        """`load` and the pushed nudge can both be missed — the nudge rides the terminal's
        WebSocket, which a hidden or disconnected terminal drops, and `load` has not fired
        since the last full document load. Opening the panel is when a person is asking."""
        # From the element, not the file: the docstring above it quotes the `hx-trigger="load"`
        # that the outerHTML bug re-armed, and a file-wide search finds that first.
        chip = self._template('_msg.html').split('<details id="msg-chip"')[1]
        trigger = re.search(r'hx-trigger="([^"]+)"', chip)
        assert trigger is not None
        self.assertIn('toggle[this.open]', trigger.group(1),
                      'a bare `toggle` fires on close too — htmx calls the filter with the '
                      'element as `this`, so `this.open` is the open half')
        self.assertIn('throttle:1s', trigger.group(1))
        self.assertIn('load', trigger.group(1))                     # the existing triggers survive
        self.assertIn('euler:message from:body', trigger.group(1))

    def test_the_terminal_chip_offers_both_acts(self) -> None:
        """It reported only, and the controls that changed it lived on the terminal's own
        titlebar — exactly where they are unreachable in the state a person most needs them:
        hide the window and the titlebar goes with it."""
        nav = self._template('_nav.html')
        chip = nav.split('id="term-chip"')[1]
        chip = chip[:chip.index('</details>')]
        self.assertIn('<summary', chip)                     # the readout survives as the chip
        self.assertIn('data-term-status', chip)
        self.assertIn('data-term-toggle', chip)             # connect / disconnect, one control
        self.assertIn('data-term-toggle-label', chip)       # …whose label site.js flips
        self.assertIn('data-term-hide', chip)               # hide / show stay two controls,
        self.assertIn('data-term-show', chip)               # …one of which CSS shows
        self.assertIn('term-only-visible', chip)
        self.assertIn('term-only-hidden', chip)

    def test_the_terminal_chip_is_not_dimmed_with_the_shell(self) -> None:
        """`.term-menu` marks a menu whose verbs type into the shell, which site.js dims when
        the socket is down. These two act on the terminal itself, and Connect is precisely
        what someone looking at a disconnected chip came for."""
        nav = self._template('_nav.html')
        self.assertNotIn('term-menu', nav.split('id="term-chip"')[1][:200])

    def test_site_js_paints_every_readout_the_chip_declares(self) -> None:
        """The panel's words are site.js's to write, so a hook the template declares and the
        script never fills would render as the static placeholder for ever."""
        nav = self._template('_nav.html')
        js = (_SITE / 'content' / 'assets' / 'site.js').read_text(encoding='utf-8')
        for hook in ('data-term-toggle-label', 'data-term-state',
                     'data-term-layout', 'data-term-layout-dot'):
            self.assertIn(hook, nav, f'{hook} is not in the chip')
            self.assertIn(f"'[{hook}]'", js, f'{hook} is declared but site.js never paints it')

    def test_the_hide_show_pair_is_resolved_by_css(self) -> None:
        """Two single-purpose controls (site.js's invariant, so neither can lie about a state
        it did not read) presented as one flipping row."""
        css = (_SITE / 'content' / 'assets' / 'site.css').read_text(encoding='utf-8')
        self.assertIn('.term-only-hidden { display: none; }', css)
        self.assertIn('body.ws-hidden .term-only-hidden', css)
        self.assertIn('body.ws-hidden .term-only-visible', css)


if __name__ == '__main__':
    unittest.main()
