#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The facet guard that stands between a generated tags.json and the tag graph.

`enforce_facets` is what makes a bulk re-tag safe: the generator repeatedly files existing slugs
under the wrong facet, and prose in the prompt did not stop it (marking every vocabulary entry
with its facet took violations up, not down). These pin the two directions apart - a problem-level
slug is relocated because nothing has to be invented, a technique is dropped because placing one
needs a solution index that cannot be guessed - and the vocabulary is mocked so no repository
state is read.
"""
from __future__ import annotations

import unittest
from json import dumps, loads
from typing import Any
from unittest.mock import patch

from solver.ai import docs

#: A miniature vocabulary spanning all three facets.
_FACETS = {
    'prime-number': 'domain',
    'abundant-number': 'domain',
    'optimal-substructure': 'domain',
    'sieve-of-sundaram': 'technique',
    'memoization': 'technique',
    'size-work-to-the-input': 'takeaway',
}


def _tags(domain: list[str] | None = None, takeaways: list[str] | None = None,
          techniques: dict[str, list[str]] | None = None,
          new_tags: list[Any] | None = None) -> str:
    return dumps({'domain': domain or [], 'takeaways': takeaways or [],
                  'techniques': techniques or {}, 'new-tags': new_tags or []})


class EnforceFacetsTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch('solver.core.tags.facet_map', return_value=dict(_FACETS))
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_guard(self, raw: str) -> tuple[dict[str, Any], list[str]]:
        cleaned, conflicts = docs.enforce_facets(raw)
        return loads(cleaned), conflicts

    def test_correctly_filed_tags_pass_through_untouched(self) -> None:
        """The common case must be a no-op - the guard only moves what disagrees."""
        raw = _tags(domain=['prime-number'], takeaways=['size-work-to-the-input'],
                    techniques={'s0': ['sieve-of-sundaram']})
        out, conflicts = self.run_guard(raw)
        self.assertEqual(conflicts, [])
        self.assertEqual(out['domain'], ['prime-number'])
        self.assertEqual(out['techniques'], {'s0': ['sieve-of-sundaram']})

    def test_domain_slug_filed_under_techniques_is_relocated(self) -> None:
        """`domain` is problem-level, so the slug moves rather than being lost."""
        raw = _tags(domain=['prime-number'], techniques={'s0': ['optimal-substructure', 'memoization']})
        out, conflicts = self.run_guard(raw)
        self.assertIn('optimal-substructure', out['domain'])
        self.assertEqual(out['techniques'], {'s0': ['memoization']})
        self.assertEqual(conflicts, ['optimal-substructure is domain, moved out of technique'])

    def test_takeaway_filed_under_techniques_is_relocated(self) -> None:
        raw = _tags(techniques={'s0': ['size-work-to-the-input']})
        out, conflicts = self.run_guard(raw)
        self.assertEqual(out['takeaways'], ['size-work-to-the-input'])
        self.assertEqual(out['techniques'], {'s0': []})
        self.assertEqual(len(conflicts), 1)

    def test_technique_filed_under_domain_is_dropped_not_relocated(self) -> None:
        """A technique attaches to one solution index. Guessing an index - or copying to every
        index - is the expand-to-all-indices defect the re-tag exists to remove, so it drops."""
        raw = _tags(domain=['prime-number', 'sieve-of-sundaram'], techniques={'s0': []})
        out, conflicts = self.run_guard(raw)
        self.assertEqual(out['domain'], ['prime-number'])
        self.assertEqual(out['techniques'], {'s0': []})
        self.assertEqual(conflicts, ['sieve-of-sundaram is technique, dropped from domain'])

    def test_relocation_does_not_duplicate_an_existing_entry(self) -> None:
        """A slug the model filed in both places must not land twice in the survivor."""
        raw = _tags(domain=['optimal-substructure'],
                    techniques={'s0': ['optimal-substructure']})
        out, _ = self.run_guard(raw)
        self.assertEqual(out['domain'], ['optimal-substructure'])

    def test_unknown_slug_backed_by_a_proposal_is_kept(self) -> None:
        """Propose-and-use is the designed path: update-tags promotes, the use resolves."""
        raw = _tags(domain=['not-in-vocabulary'], new_tags=[{'slug': 'not-in-vocabulary'}])
        out, conflicts = self.run_guard(raw)
        self.assertEqual(out['domain'], ['not-in-vocabulary'])
        self.assertEqual(conflicts, [])
        self.assertEqual(len(out['new-tags']), 1)

    def test_unknown_slug_without_a_proposal_is_dropped(self) -> None:
        """Used but never defined, it would land as a dangling reference --check rejects.

        A real one: `string_matching_placeholder` reached p0679 this way - not even valid slug
        syntax, and invented rather than proposed.
        """
        raw = _tags(domain=['prime-number', 'string_matching_placeholder'])
        out, conflicts = self.run_guard(raw)
        self.assertEqual(out['domain'], ['prime-number'])
        self.assertEqual(conflicts,
                         ['string_matching_placeholder is undefined and unproposed, '
                          'dropped from domain'])

    def test_proposal_reusing_a_taken_slug_is_dropped(self) -> None:
        """Slugs are globally unique, so a proposal colliding in any facet can never be promoted."""
        raw = _tags(new_tags=[{'slug': 'memoization', 'facet': 'domain'},
                              {'slug': 'genuinely-new', 'facet': 'domain'}])
        out, conflicts = self.run_guard(raw)
        self.assertEqual([t['slug'] for t in out['new-tags']], ['genuinely-new'])
        self.assertEqual(conflicts, ['memoization already exists as technique, proposal dropped'])

    def test_output_is_written_the_way_update_tags_writes_it(self) -> None:
        """Byte-compatible with `tags._write_problem_tags`, or every reconcile shows fake churn."""
        cleaned, _ = docs.enforce_facets(_tags(domain=['prime-number']))
        self.assertTrue(cleaned.endswith('\n'))
        self.assertEqual(cleaned, dumps(loads(cleaned), indent=2) + '\n')


class ExplicitSelectorTests(unittest.TestCase):
    """The targeted-re-run selector, which neither `untagged` nor `start` can express."""

    def test_parses_a_comma_separated_list(self) -> None:
        from solver.ai import batch
        with patch.object(batch.Problem, 'from_number', side_effect=lambda n: n):
            self.assertEqual(batch._explicit('26,39,146'), [26, 39, 146])

    def test_tolerates_spaces_and_a_p_prefix(self) -> None:
        from solver.ai import batch
        with patch.object(batch.Problem, 'from_number', side_effect=lambda n: n):
            self.assertEqual(batch._explicit('p26, 39 , P146'), [26, 39, 146])

    def test_empty_selects_nothing(self) -> None:
        from solver.ai import batch
        self.assertEqual(batch._explicit(''), [])


if __name__ == '__main__':
    unittest.main()
