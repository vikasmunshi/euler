#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Reconcile logic for the tag graph (solver.core.tags) — deletions in particular.

These exercise the pure reconcile helpers on in-memory central/per-problem dicts with the
git-HEAD read mocked, so they need no filesystem or repository state. Domain-facet tags are
used throughout so `_apply_membership` never needs on-disk solution indices.
"""
from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import patch

from solver.core import tags


def _central() -> dict[str, Any]:
    return {'version': 1, 'facets': {}, 'tags': [
        {'slug': 'alpha', 'facet': 'domain', 'name': 'Alpha', 'reference': None,
         'additional-references': [], 'summary': '', 'refs': ['p0002', 'p0003']},
        {'slug': 'beta', 'facet': 'domain', 'name': 'Beta', 'reference': None,
         'additional-references': [], 'summary': '', 'refs': ['p0002']},
    ]}


def _ptags() -> dict[int, dict[str, Any]]:
    return {
        2: {'domain': ['alpha', 'beta'], 'takeaways': [], 'techniques': {}, 'new-tags': []},
        3: {'domain': ['alpha'], 'takeaways': [], 'techniques': {}, 'new-tags': []},
    }


def _refs(central: dict[str, Any], slug: str) -> list[str] | None:
    return next((t['refs'] for t in central['tags'] if t['slug'] == slug), None)


class TagReconcileTests(unittest.TestCase):
    def _run(self, central: dict[str, Any], ptags: dict[int, dict[str, Any]],
             head: dict[str, Any]) -> None:
        """Run the reconcile steps update-tags applies, with git HEAD mocked."""
        with patch.object(tags, '_head_central', lambda: head):
            tags._maintainer_diff(central, ptags)
        tags._rebuild_refs(central, ptags)

    def test_per_problem_removal_drops_central_ref(self) -> None:
        """A slug removed from a per-problem file disappears from the central leg (scenario A)."""
        central, ptags, head = _central(), _ptags(), _central()
        ptags[2]['domain'].remove('beta')
        self._run(central, ptags, head)
        self.assertEqual(_refs(central, 'beta'), [])
        self.assertEqual(tags._validate(central, ptags), [])

    def test_central_ref_removal_propagates_to_problem(self) -> None:
        """Clearing a tag's central refs removes it from the per-problem file (scenario B, maintainer)."""
        central, ptags, head = _central(), _ptags(), _central()
        next(t for t in central['tags'] if t['slug'] == 'beta')['refs'] = []
        self._run(central, ptags, head)
        self.assertNotIn('beta', ptags[2]['domain'])
        self.assertEqual(_refs(central, 'beta'), [])
        self.assertEqual(tags._validate(central, ptags), [])

    def test_vocabulary_deletion_cascades(self) -> None:
        """Deleting a whole tag from the vocabulary strips it from every per-problem file, leaving
        no orphan (scenario C — the case update-tags previously missed)."""
        central, ptags, head = _central(), _ptags(), _central()
        central['tags'] = [t for t in central['tags'] if t['slug'] != 'beta']
        self._run(central, ptags, head)
        self.assertNotIn('beta', ptags[2]['domain'])
        self.assertEqual(tags._validate(central, ptags), [])

    def test_typo_slug_is_flagged_not_silently_removed(self) -> None:
        """A slug that was never in the vocabulary (never in HEAD) is NOT cascade-deleted — it is
        an authoring error, so it stays put and --check flags it."""
        central, ptags, head = _central(), _ptags(), _central()
        ptags[3]['domain'].append('gamma')      # never a real tag
        self._run(central, ptags, head)
        self.assertIn('gamma', ptags[3]['domain'])
        self.assertTrue(any('gamma' in msg for msg in tags._validate(central, ptags)))


if __name__ == '__main__':
    unittest.main()
