#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for `update-models`' staleness rule — the one thing about it that has bitten twice.

The generated block carries a date. Rendered as *today* and compared whole, it made the
block differ from itself on any day it had not already been regenerated: `--check` failed
daily and a release carried a commit that moved a date and nothing else. That is the same
trap `update-usd-rate` was split out of this command to escape, arriving by another door,
which is why it is worth a test rather than a comment.

The rule: a comparison ignores the date, so the block is stale only when a **model or a
price** has moved — and the date then records when that last happened. Nothing here touches
the network; the collected-models shape is the generator's own input type.
"""
from __future__ import annotations

import unittest

from solver.ai import update_models

#: What `_collect()` returns: `(model_id, display name, input price, output price)`.
_MODELS: list[tuple[str, str, float, float]] = [
    ('claude-opus-5', 'Claude Opus 5', 15.0, 75.0),
    ('claude-haiku-4-5', 'Claude Haiku 4.5', 1.0, 5.0),
]


def _block(models: list[tuple[str, str, float, float]], date: str) -> str:
    """The rendered block with its date stamp forced, standing in for a file from that day."""
    return update_models._DATED_RE.sub(f'(last changed {date};',
                                       update_models._render(models, {}))


class DateStampTests(unittest.TestCase):
    def test_the_date_is_stamped_into_the_header(self) -> None:
        self.assertIn(f'last changed {update_models._today()};',
                      update_models._render(_MODELS, {}))

    def test_two_renderings_of_one_catalogue_differ_only_by_their_date(self) -> None:
        """The whole failure mode, stated directly: same models, different day."""
        yesterday = _block(_MODELS, '5th August 2026')
        today = _block(_MODELS, '6th August 2026')
        self.assertNotEqual(yesterday, today, 'the stamp really does differ')
        self.assertEqual(update_models._undated(yesterday), update_models._undated(today),
                         'and nothing else does, so the catalogue is not stale')

    def test_a_moved_price_is_still_stale(self) -> None:
        """The date rule must not swallow the change the command exists to catch."""
        dearer = [('claude-opus-5', 'Claude Opus 5', 20.0, 75.0), _MODELS[1]]
        self.assertNotEqual(update_models._undated(_block(_MODELS, '6th August 2026')),
                            update_models._undated(_block(dearer, '6th August 2026')))

    def test_a_new_model_is_still_stale(self) -> None:
        extra = [*_MODELS, ('claude-fable-5', 'Claude Fable 5', 30.0, 150.0)]
        self.assertNotEqual(update_models._undated(_block(_MODELS, '6th August 2026')),
                            update_models._undated(_block(extra, '6th August 2026')))

    def test_the_shipped_block_carries_a_date_the_rule_can_find(self) -> None:
        """A reworded header would silently restore the daily rewrite."""
        text = update_models.MODELS_FILE.read_text()
        self.assertRegex(text, update_models._DATED_RE)
        self.assertNotEqual(update_models._undated(text), text)


class RenderTests(unittest.TestCase):
    def test_a_curated_comment_survives_a_regeneration(self) -> None:
        rendered = update_models._render(_MODELS, {'claude-opus-5': 'the one we use for code'})
        self.assertIn("CLAUDE_OPUS_5 = 'claude-opus-5'  # the one we use for code", rendered)

    def test_a_new_model_is_commented_with_its_display_name(self) -> None:
        rendered = update_models._render(_MODELS, {})
        self.assertIn("CLAUDE_HAIKU_4_5 = 'claude-haiku-4-5'  # Claude Haiku 4.5", rendered)

    def test_prices_are_written_to_two_places(self) -> None:
        rendered = update_models._render(_MODELS, {})
        self.assertIn('Model.CLAUDE_OPUS_5: Price(input=15.00, output=75.00),', rendered)


if __name__ == '__main__':
    unittest.main()
