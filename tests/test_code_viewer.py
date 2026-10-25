#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the code viewer's reads (euler_site.site.code): the summary a file opens with —
the first sentence of what it says about itself — and the numbered, anchored lines."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from euler_site.site import code


class SummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def summary(self, name: str, text: str) -> str | None:
        path = self.dir / name
        path.write_text(text, encoding='utf-8')
        return code.summary(path)

    def test_a_module_says_it_in_its_docstring(self) -> None:
        text = '#!/usr/bin/env python3\n"""Load test cases. Then more.\n\nDetail."""\nx = 1\n'
        self.assertEqual(self.summary('m.py', text), 'Load test cases.')

    def test_a_dotted_name_does_not_end_the_sentence(self) -> None:
        self.assertEqual(self.summary('m.py', '"""Read `solver.config` e.g. here. Next."""\n'),
                         'Read `solver.config` e.g. here.')

    def test_a_script_says_it_in_its_header_comment(self) -> None:
        text = '#!/usr/bin/env bash\n# Re-check every problem.\n# ======\n#\n# More.\nset -e\n'
        self.assertEqual(self.summary('s.sh', text), 'Re-check every problem.')

    def test_a_list_after_a_colon_is_not_part_of_it(self) -> None:
        text = '# Three packages (docs/package-guide.md), each with its own:\n#\n#   one\n'
        self.assertEqual(self.summary('x.toml', text), 'Three packages, each with its own.')

    def test_block_comments_and_templates(self) -> None:
        self.assertEqual(self.summary('a.css', '/* The app shell.\n   Detail. */\nbody {}\n'), 'The app shell.')
        self.assertEqual(self.summary('t.html', '{% extends "b.html" %}\n{# The page. More. #}\n'), 'The page.')

    def test_nothing_to_say_is_none(self) -> None:
        self.assertIsNone(self.summary('tox.ini', '[flake8]\nmax-line-length = 120\n'))

    def test_a_summary_is_html_with_its_code_spans(self) -> None:
        self.assertEqual(code.ticks('Run `a<b>` now'), 'Run <code>a&lt;b&gt;</code> now')
        self.assertEqual(code.plain('Run `a` now'), 'Run a now')


class HighlightTests(unittest.TestCase):
    def test_one_line_out_per_line_in_blank_ones_included(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'x.py'
            path.write_text('\n\ns = """a\nb"""\n\n', encoding='utf-8')
            listing = code.highlight(path)
        self.assertTrue(listing.coloured)
        self.assertEqual(len(listing.lines), 5)
        self.assertEqual(listing.language, 'Python')


if __name__ == '__main__':
    unittest.main()
