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
from solver.shell import dialogue
from solver.shell.command import Context, registry
from tests import silence

silence()


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
        granularity, plus the solved/problems pair the web index shows as the page's subtitle,
        so a consumer can rank, filter or label without re-deriving them.

        The solved set is pinned here: it is real progress in a real clone, and a test that
        read it would pass or fail on which problems this checkout has solved."""
        self._article('domain/alpha.md', '<!-- tags: [alpha] -->\n<!-- status: final -->\n# Alpha, at length\n')
        self._article('curated/mix.md', '<!-- tags: [alpha, beta] -->\n# Mixed\n')
        with patch.object(tags, '_problem_meta', return_value=({}, {2})):
            index = tags._build_index(_central())
        rows = {row['path']: row for row in index['articles']}
        self.assertEqual([row['path'] for row in index['articles']], sorted(rows))   # sorted by path
        self.assertEqual(set(rows), {'domain/alpha', 'curated/mix'})                 # pages only
        self.assertEqual(rows['domain/alpha']['status'], 'final')
        self.assertEqual(rows['domain/alpha']['title'], 'Alpha, at length')          # the page's own H1
        self.assertEqual(rows['domain/alpha']['refs'], ['p0002', 'p0003'])
        self.assertEqual(rows['curated/mix']['status'], 'draft')                     # no comment → draft
        self.assertEqual(rows['curated/mix']['refs'], ['p0002', 'p0003'])            # union of both tags
        # the counts: two distinct problems behind the page, one of them solved
        self.assertEqual((rows['curated/mix']['solved'], rows['curated/mix']['problems']), (1, 2))

    def test_counts_collapse_solution_refs_to_problems(self) -> None:
        """A technique leg names solution indices (`p0002_s0`, `p0002_s1`); the subtitle counts
        problems, so the two are one."""
        self.assertEqual(tags._article_counts(['p0002_s0', 'p0002_s1', 'p0003'], {3}), (1, 2))
        self.assertEqual(tags._article_counts([], {3}), (0, 0))                      # an untagged page

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
        self.assertIn('## Problems', text)                                           # the visible list
        self.assertIn('[0002](/solutions/0002/)', text)                              # its one problem, linked
        self.assertEqual(tags.article_status(text), 'draft')

    def test_problems_block_is_a_visible_sorted_list_with_markers(self) -> None:
        """The generated section renders: distinct problems (pNNNN_sN collapsed), sorted, each
        linked with a solved/unsolved marker baked in."""
        by_slug = {t['slug']: t for t in _central()['tags']}
        # alpha's refs in the fixture are p0002, p0003; add a technique-style per-index ref to
        # prove the solution index collapses to one problem row.
        by_slug['alpha'] = {**by_slug['alpha'], 'refs': ['p0002', 'p0003', 'p0003_s0']}
        block = tags._problems_block(['alpha'], by_slug, {2: 'Two', 3: 'Three'}, {2})
        self.assertTrue(block.startswith('<!-- problems (generated by update-tags) -->'))
        self.assertTrue(block.rstrip().endswith('<!-- /problems -->'))
        self.assertIn('- ● [0002](/solutions/0002/) — Two', block)      # filled = solved
        self.assertIn('- ○ [0003](/solutions/0003/) — Three', block)    # hollow = unsolved
        self.assertEqual(block.count('/solutions/0003/'), 1)        # per-index refs collapse to one row

    def test_check_flags_a_stale_index(self) -> None:
        central = _central()
        self._article('domain/alpha.md', '<!-- tags: [alpha] -->\n# Alpha\n')
        self.assertIsNone(tags._load_index())                        # nothing written yet
        tags._write_index(tags._build_index(central))
        self.assertEqual(tags._load_index(), tags._build_index(central))
        self._article('domain/alpha.md', '<!-- tags: [alpha] -->\n<!-- status: final -->\n# Alpha\n')
        self.assertNotEqual(tags._load_index(), tags._build_index(central))


class _TopicCase(unittest.TestCase):
    """A scratch `topics/` tree and a two-tag vocabulary, for everything `create-topic` does."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.topics = root / 'topics'
        self.topics.mkdir()
        vocab = root / 'tags.json'
        vocab.write_text('{"version": 1, "facets": {}, "tags": ['
                         '{"slug": "prime-number", "facet": "domain", "name": "Prime number",'
                         ' "reference": null, "additional-references": [], "summary": "", "refs": []},'
                         '{"slug": "trial-division", "facet": "technique", "name": "Trial division",'
                         ' "reference": null, "additional-references": [], "summary": "", "refs": []}]}')
        saved = (config.topics_dir, config.central_tags_file)
        config.topics_dir = self.topics
        config.central_tags_file = vocab
        self.addCleanup(lambda: setattr(config, 'central_tags_file', saved[1]))
        self.addCleanup(lambda: setattr(config, 'topics_dir', saved[0]))
        # the final reconcile is exercised elsewhere; here it would read the real problem tree
        self.enterContext(patch.object(tags, 'update_tags', lambda **k: 0))

    def _page(self, rel: str) -> Path:
        return self.topics / f'{rel}.md'


class TagSelectionTests(_TopicCase):
    """Picking the tags for a new topic — driven through the adapter, which is where it lives.

    `create-topic`'s `*tags` used to hand-roll `dialogue.select` in the body; it now declares
    `Ask(multi=True, choices='tags')`, so what is worth testing is the whole path: the
    variable supplies the vocabulary, the adapter runs the search-and-select, and the chosen
    slugs arrive as the command's trailing positionals.

    Through the **registry**, and against the real command: both the choice set and the
    command itself are captured at registration, so patching either by module attribute
    would leave the thing under test untouched.
    """

    def setUp(self) -> None:
        super().setUp()
        self.enterContext(patch.object(config, 'subject',
                                       config.subject._replace(profile='maintainer')))

    def _run(self, script: list[str], path: str = 'number-theory/primes') -> None:
        """Drive the command through the two seams every dialogue shares."""
        it = iter(script)
        command = registry.resolve('create-topic')
        assert command is not None
        with (patch.object(tags.console, 'input', lambda *a, **k: next(it)),
              patch.object(dialogue, 'interactive', lambda: True)):
            command.invoke(Context(argv=[path]))

    def _tags_of(self, rel: str = 'number-theory/primes') -> str:
        """The `<!-- tags: [...] -->` line the page was seeded with, or '' if none was made."""
        page = self._page(rel)
        if not page.exists():
            return ''
        line = next(ln for ln in page.read_text().splitlines() if ln.startswith('<!-- tags:'))
        return line.removeprefix('<!-- tags: [').removesuffix('] -->')

    def test_search_then_toggle_by_number_then_done(self) -> None:
        # 'prime' matches prime-number, listed as 1 — the menus are 1-based throughout
        self._run(['prime', '1', 'done'])
        self.assertEqual(self._tags_of(), 'prime-number')

    def test_a_second_toggle_removes(self) -> None:
        # add then remove leaves nothing selected, so 'done' can't finish; add again and finish
        self._run(['prime', '1', '1', 'prime', '1', 'done'])
        self.assertEqual(self._tags_of(), 'prime-number')

    def test_quit_leaves_the_topic_uncreated(self) -> None:
        self._run(['prime', '1', 'q'])
        self.assertFalse(self._page('number-theory/primes').exists())

    def test_a_number_without_a_search_is_ignored(self) -> None:
        # '1' before any search has no results to index; then a real pick finishes
        self._run(['1', 'trial', '1', 'done'])
        self.assertEqual(self._tags_of(), 'trial-division')

    def test_several_tags_arrive_in_selection_order(self) -> None:
        self._run(['prime', '1', 'trial', '1', 'done'])
        self.assertEqual(self._tags_of(), 'prime-number, trial-division')

    def test_a_path_that_could_not_be_created_is_never_asked_about(self) -> None:
        """Searching the vocabulary and *then* being told the path is malformed is backwards."""
        with (patch.object(tags.console, 'input',
                           lambda *a, **k: self.fail('must not ask about a bad path')),
              patch.object(dialogue, 'interactive', lambda: True)):
            command = registry.resolve('create-topic')
            assert command is not None
            command.invoke(Context(argv=['primes']))
        self.assertFalse(self._page('primes').exists())

    def test_an_existing_page_is_never_asked_about_either(self) -> None:
        (self.topics / 'number-theory').mkdir(parents=True, exist_ok=True)
        (self.topics / 'number-theory' / 'primes.md').write_text('<!-- tags: [prime-number] -->\n')
        with (patch.object(tags.console, 'input',
                           lambda *a, **k: self.fail('must not ask about a taken path')),
              patch.object(dialogue, 'interactive', lambda: True)):
            command = registry.resolve('create-topic')
            assert command is not None
            command.invoke(Context(argv=['number-theory/primes']))
        self.assertEqual(self._tags_of(), 'prime-number', 'the existing page is untouched')


class CreateTopicTests(_TopicCase):
    """The maintainer `create-topic` command: validation, and the seeded curated page."""

    def test_creates_a_curated_page_with_all_its_tags(self) -> None:
        rc = tags.create_topic('number-theory/primes', 'prime-number', 'trial-division')
        self.assertEqual(rc, 0)
        text = self._page('number-theory/primes').read_text()
        self.assertIn('<!-- tags: [prime-number, trial-division] -->', text)   # every tag, in order
        self.assertIn('<!-- status: draft -->', text)
        self.assertIn('# Primes', text)                                        # leaf, title-cased
        self.assertIn('<!-- problems (generated by update-tags) -->', text)    # the empty region

    def test_rejects_an_unknown_tag(self) -> None:
        rc = tags.create_topic('number-theory/primes', 'prime-number', 'not-a-tag')
        self.assertNotEqual(rc, 0)
        self.assertFalse(self._page('number-theory/primes').exists())

    def test_rejects_a_bare_path(self) -> None:
        self.assertNotEqual(tags.create_topic('primes', 'prime-number'), 0)

    def test_refuses_to_clobber_an_existing_page(self) -> None:
        self.assertEqual(tags.create_topic('number-theory/primes', 'prime-number'), 0)
        rc = tags.create_topic('number-theory/primes', 'trial-division')
        self.assertNotEqual(rc, 0)
        # the first page's single tag is untouched
        self.assertIn('[prime-number]', self._page('number-theory/primes').read_text())

    def test_non_interactive_without_tags_is_an_error(self) -> None:
        with patch.object(dialogue, 'interactive', lambda: False):
            with self.assertRaises(dialogue.Abort):
                tags.create_topic('number-theory/primes')
        self.assertFalse(self._page('number-theory/primes').exists())


if __name__ == '__main__':
    unittest.main()
