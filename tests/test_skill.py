#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `claude-blog` command's use of the article index (`topics/articles.json`):
target completion (unwritten first, curated pages included) and the `final` gate that
keeps a finished article from being rewritten without `--force`.

The index is stubbed in memory — no repository tree is read, and the skill itself is
never launched: `_run_skill` is replaced by a recorder.
"""
from __future__ import annotations

import unittest
from typing import Any, cast
from unittest.mock import patch

from prompt_toolkit.completion import Completion

from solver.ai import skill
from solver.config import ExitCodes

_INDEX: list[dict[str, Any]] = [
    {'path': 'domain/alpha', 'title': 'Alpha', 'status': 'draft', 'tags': ['alpha'],
     'refs': ['p0001', 'p0002', 'p0003']},
    {'path': 'domain/beta', 'title': 'Beta', 'status': 'draft', 'tags': ['beta'],
     'refs': ['p0004']},
    {'path': 'technique/gamma', 'title': 'Gamma', 'status': 'draft', 'tags': ['gamma'],
     'refs': ['p0005_s0', 'p0005_s1', 'p0006_s0']},
    {'path': 'number-theory/primes', 'title': 'Primes', 'status': 'final', 'tags': ['delta'],
     'refs': ['p0007', 'p0008']},
]


def _completions(incomplete: str) -> list[Completion]:
    """The command's completions for *incomplete* — always Completion objects, never bare strings."""
    return [c for c in skill._topic_completions(cast(Any, None), incomplete) if isinstance(c, Completion)]


class TopicCompletionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.enterContext(patch.object(skill, '_topic_index', lambda: _INDEX))

    def _paths(self, incomplete: str = '') -> list[str]:
        return [c.text for c in _completions(incomplete)]

    def test_completions_are_alphabetical(self) -> None:
        """Sorted by path, not by how much needs writing: a maintainer types the name of the topic
        they have in mind, and an order that shifts as pages get written cannot be learned."""
        self.assertEqual(self._paths(), ['domain/alpha', 'domain/beta', 'number-theory/primes',
                                         'technique/gamma'])

    def test_curated_topics_are_offered_not_just_tag_pages(self) -> None:
        """A page that is no tag's own (`number-theory/primes`) is a completion like any other."""
        self.assertEqual(self._paths('number-theory'), ['number-theory/primes'])
        self.assertEqual(self._paths('prime'), ['number-theory/primes'])

    def test_meta_shows_folder_distinct_problems_and_status(self) -> None:
        """Every page has a status now, so every entry shows one. The count is *distinct
        problems*, so a technique's per-index refs (p0005_s0, p0005_s1) count once."""
        meta = {c.text: str(c.display_meta) for c in _completions('')}
        self.assertIn('draft', meta['technique/gamma'])
        self.assertIn('final', meta['number-theory/primes'])
        self.assertIn('technique · 2 · draft', meta['technique/gamma'])
        self.assertIn('domain · 3 · draft', meta['domain/alpha'])


class FinalGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.launched: list[str] = []

        def _record(_ctx: Any, invocation: str, _title: str) -> int:
            self.launched.append(invocation)
            return ExitCodes.EXIT_OK

        self.enterContext(patch.object(skill, '_topic_index', lambda: _INDEX))
        self.enterContext(patch.object(skill, '_run_skill', _record))

    def _blog(self, topic: str, prompt: str = '', *, force: bool = False) -> int:
        return skill.claude_blog(cast(Any, None), topic, prompt, force=force)

    def test_final_topic_is_left_alone(self) -> None:
        self.assertEqual(self._blog('number-theory/primes'), ExitCodes.EXIT_OK)
        self.assertEqual(self.launched, [])

    def test_final_topic_named_by_bare_slug_is_also_gated(self) -> None:
        self.assertEqual(self._blog('primes'), ExitCodes.EXIT_OK)
        self.assertEqual(self.launched, [])

    def test_force_rewrites_a_final_topic(self) -> None:
        self._blog('number-theory/primes', force=True)
        self.assertEqual(self.launched, ['/claude-euler-blogger number-theory/primes'])

    def test_draft_and_unknown_topics_run(self) -> None:
        self._blog('technique/gamma')
        self._blog('technique/not-in-the-index', 'keep it short')
        self.assertEqual(self.launched, ['/claude-euler-blogger technique/gamma',
                                         '/claude-euler-blogger technique/not-in-the-index keep it short'])


class BlogPromptTests(unittest.TestCase):
    """A bare `claude-blog <path>` (as the web Write/Rewrite Actions emit) prompts for an angle
    when the shell is interactive — Enter skips it; a command block never prompts."""

    def setUp(self) -> None:
        self.launched: list[str] = []
        self.enterContext(patch.object(skill, '_topic_index', lambda: _INDEX))
        self.enterContext(patch.object(skill, '_run_skill',
                                       lambda _c, inv, _t: self.launched.append(inv) or ExitCodes.EXIT_OK))

    def _blog(self, topic: str, prompt: str = '', *, tty: bool, typed: str = '') -> None:
        with patch.object(skill.sys.stdin, 'isatty', lambda: tty), \
             patch.object(skill.console, 'input', lambda *a, **k: typed):
            skill.claude_blog(cast(Any, None), topic, prompt)

    def test_interactive_and_empty_prompts_and_appends(self) -> None:
        self._blog('technique/gamma', tty=True, typed='emphasise the bound')
        self.assertEqual(self.launched, ['/claude-euler-blogger technique/gamma emphasise the bound'])

    def test_interactive_empty_and_enter_leaves_it_bare(self) -> None:
        self._blog('technique/gamma', tty=True, typed='')
        self.assertEqual(self.launched, ['/claude-euler-blogger technique/gamma'])

    def test_non_interactive_never_prompts(self) -> None:
        # console.input would raise if called; a command block must not block on a read.
        with patch.object(skill.sys.stdin, 'isatty', lambda: False), \
             patch.object(skill.console, 'input',
                          lambda *a, **k: self.fail('must not prompt without a tty')):
            skill.claude_blog(cast(Any, None), 'technique/gamma')
        self.assertEqual(self.launched, ['/claude-euler-blogger technique/gamma'])

    def test_a_given_prompt_is_not_overridden(self) -> None:
        with patch.object(skill.sys.stdin, 'isatty', lambda: True), \
             patch.object(skill.console, 'input',
                          lambda *a, **k: self.fail('must not prompt when one was given')):
            skill.claude_blog(cast(Any, None), 'technique/gamma', 'keep it short')
        self.assertEqual(self.launched, ['/claude-euler-blogger technique/gamma keep it short'])


if __name__ == '__main__':
    unittest.main()
