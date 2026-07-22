#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Reconcile logic for the tag graph (solver.core.tags) — deletions in particular.

These exercise the pure reconcile helpers on in-memory central/per-problem dicts with the
git-HEAD read mocked, so they need no filesystem or repository state. Domain-facet tags are
used throughout so `_apply_membership` never needs on-disk solution indices.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from solver.config import config
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


class ArticleIndexTests(unittest.TestCase):
    """The article status comment, and the index update-tags builds from it.

    Runs against a scratch `topics/` tree — config is pointed at it for the duration, so
    the real one is never read or written."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.topics = Path(tmp.name)
        saved = (config.topics_dir, config.topics_index_file)
        config.topics_dir = self.topics
        config.topics_index_file = self.topics / 'articles.json'
        self.addCleanup(lambda: setattr(config, 'topics_index_file', saved[1]))
        self.addCleanup(lambda: setattr(config, 'topics_dir', saved[0]))

    def _article(self, rel: str, text: str) -> None:
        path = self.topics / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_status_is_draft_unless_the_page_says_final(self) -> None:
        self.assertEqual(tags.article_status('# Alpha\n'), 'draft')
        self.assertEqual(tags.article_status('<!-- status: FINAL -->\n# Alpha\n'), 'final')
        # a page on disk is never 'missing', whatever its comment claims
        self.assertEqual(tags.article_status('<!-- status: missing -->\n# Alpha\n'), 'draft')

    def test_stamp_lands_under_the_tags_comment_and_is_idempotent(self) -> None:
        stamped = tags._stamp_status('<!-- tags: [alpha] -->\n# Alpha\n')
        self.assertEqual(stamped.splitlines()[:2], ['<!-- tags: [alpha] -->', '<!-- status: draft -->'])
        self.assertEqual(tags._stamp_status(stamped), stamped)
        self.assertEqual(tags._stamp_status('# Alpha\n').splitlines()[0], '<!-- status: draft -->')

    def test_index_is_built_from_the_pages_and_carries_their_refs(self) -> None:
        """A row exists because a page does — update-tags creates one per tag, so there is no
        vocabulary-only row and no `missing`. Each row carries the page's own refs, at the legs'
        granularity, so a consumer can rank or filter without re-deriving them."""
        self._article('domain/alpha.md', '<!-- tags: [alpha] -->\n<!-- status: final -->\n# Alpha, at length\n')
        self._article('curated/mix.md', '<!-- tags: [alpha, beta] -->\n# Mixed\n')
        index = tags._build_index(_central())
        rows = {row['path']: row for row in index['articles']}
        self.assertEqual([row['path'] for row in index['articles']], sorted(rows))   # sorted by path
        self.assertEqual(set(rows), {'domain/alpha', 'curated/mix'})                 # pages only
        self.assertEqual(rows['domain/alpha']['status'], 'final')
        self.assertEqual(rows['domain/alpha']['title'], 'Alpha, at length')          # the page's own H1
        self.assertEqual(rows['domain/alpha']['refs'], ['p0002', 'p0003'])
        self.assertEqual(rows['curated/mix']['status'], 'draft')                     # no comment → draft
        self.assertEqual(rows['curated/mix']['refs'], ['p0002', 'p0003'])            # union of both tags
        self.assertNotIn('problems', rows['curated/mix'])                            # replaced by refs

    def test_a_tag_without_a_page_gets_one_from_the_template(self) -> None:
        """This is what removes `missing`: every tag has a file, so status only answers whether
        the page has been *written*."""
        central = _central()
        tags._regen_articles(central, write=True)
        page = self.topics / 'domain' / 'beta.md'
        self.assertTrue(page.exists())
        text = page.read_text()
        self.assertIn('<!-- tags: [beta] -->', text)
        self.assertIn('<!-- status: draft -->', text)
        self.assertIn('# Beta', text)
        self.assertIn('p0002', text)                                                 # its generated refs
        self.assertEqual(tags.article_status(text), 'draft')

    def test_check_flags_a_stale_index(self) -> None:
        central = _central()
        self._article('domain/alpha.md', '<!-- tags: [alpha] -->\n# Alpha\n')
        self.assertIsNone(tags._load_index())                        # nothing written yet
        tags._write_index(tags._build_index(central))
        self.assertEqual(tags._load_index(), tags._build_index(central))
        self._article('domain/alpha.md', '<!-- tags: [alpha] -->\n<!-- status: final -->\n# Alpha\n')
        self.assertNotEqual(tags._load_index(), tags._build_index(central))


if __name__ == '__main__':
    unittest.main()
