#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the Phase 5c save gate (solver/web/site/validate.py, DD-10):
the per-suffix checks every 5d write passes — .py (auto-fix + flake8),
.c (compile against the runner header), .json (reject-and-restore semantics),
and the .html sanitize-and-store-clean via nh3."""
from __future__ import annotations

import unittest
from pathlib import Path

from solver.web.site.validate import validate

_REPO = Path(__file__).resolve().parents[1]

_PY_CLEAN = 'def solve() -> str:\n    return str(42)\n'
_PY_UNDEFINED = 'def solve() -> str:\n    return str(missing_name)\n'
_PY_UNUSED_IMPORT = 'import os\n\n\ndef solve() -> str:\n    return str(42)\n'

_C_CLEAN = '''#include "runner.h"

const char *solve(int argc, char *argv[]) {
    (void)argc; (void)argv;
    static char answer[32];
    snprintf(answer, sizeof answer, "%d", 42);
    return answer;
}
'''
_C_BROKEN = 'const char *solve(int argc, char *argv[]) { return undeclared; }\n'


class PythonGateTests(unittest.TestCase):
    def test_clean_source_passes(self) -> None:
        result = validate('p9999_s0.py', _PY_CLEAN.encode(), _REPO)
        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.content.decode(), _PY_CLEAN)

    def test_undefined_name_rejected_with_diagnostic(self) -> None:
        result = validate('p9999_s0.py', _PY_UNDEFINED.encode(), _REPO)
        self.assertFalse(result.ok)
        self.assertIn('F821', result.message)
        self.assertTrue(any(d.severity == 'error' and d.line == 2 for d in result.diagnostics))

    def test_autofix_removes_unused_import_when_dev_tools_present(self) -> None:
        # In this venv the dev extras are installed, so autoflake strips the
        # unused import and the save lands with canonicalised content.
        result = validate('p9999_s0.py', _PY_UNUSED_IMPORT.encode(), _REPO)
        self.assertTrue(result.ok, result.message)
        self.assertNotIn('import os', result.content.decode())

    def test_undecodable_source_rejected(self) -> None:
        result = validate('p9999_s0.py', b'\xff\xfe\x00bad', _REPO)
        self.assertFalse(result.ok)


class CGateTests(unittest.TestCase):
    def test_clean_source_compiles(self) -> None:
        result = validate('p9999_s0.c', _C_CLEAN.encode(), _REPO)
        self.assertTrue(result.ok, result.message)
        self.assertEqual(result.content, _C_CLEAN.encode())   # stored verbatim

    def test_broken_source_rejected_with_diagnostic(self) -> None:
        result = validate('p9999_s0.c', _C_BROKEN.encode(), _REPO)
        self.assertFalse(result.ok)
        self.assertTrue(any(d.severity == 'error' for d in result.diagnostics))
        self.assertNotIn('euler-cgate-', result.message)      # scratch paths hidden


class JsonGateTests(unittest.TestCase):
    def test_valid_json_is_reindented(self) -> None:
        result = validate('test_cases.json', b'[{"category":"main","answer":1}]', _REPO)
        self.assertTrue(result.ok)
        self.assertEqual(result.content.decode(),
                         '[\n  {\n    "category": "main",\n    "answer": 1\n  }\n]')

    def test_malformed_json_rejected(self) -> None:
        result = validate('test_cases.json', b'[not json', _REPO)
        self.assertFalse(result.ok)
        self.assertIn('not valid JSON', result.message)


class HtmlGateTests(unittest.TestCase):
    def test_script_is_stripped_and_structure_kept(self) -> None:
        dirty = ('<article><h3>T</h3><p>x<script>alert(1)</script></p>'
                 '<img src=x onerror=alert(1)></article>')
        result = validate('notes.html', dirty.encode(), _REPO)
        self.assertTrue(result.ok)
        clean = result.content.decode()
        self.assertNotIn('<script', clean)
        self.assertNotIn('<img', clean)
        self.assertIn('<h3>T</h3>', clean)

    def test_mathjax_tex_survives_as_text(self) -> None:
        result = validate('notes.html', b'<p>$t_n = \\frac12n(n+1)$ and $$x^2$$</p>', _REPO)
        self.assertTrue(result.ok)
        self.assertIn('$t_n = \\frac12n(n+1)$', result.content.decode())

    def test_link_attributes_kept_and_rel_rewritten(self) -> None:
        dirty = ('<p><a href="https://x.example" class="reference-source" '
                 'target="_blank" rel="nofollow" onclick="alert(1)">l</a></p>')
        result = validate('notes.html', dirty.encode(), _REPO)
        clean = result.content.decode()
        self.assertIn('href="https://x.example"', clean)
        self.assertIn('class="reference-source"', clean)
        self.assertIn('rel="noopener noreferrer"', clean)     # nh3-managed
        self.assertNotIn('onclick', clean)

    def test_table_normalised_with_tbody(self) -> None:
        result = validate('notes.html', b'<table><tr><td>1</td></tr></table>', _REPO)
        self.assertIn('<tbody>', result.content.decode())     # store-clean normalisation


class DispatchTests(unittest.TestCase):
    def test_unknown_suffix_rejected(self) -> None:
        result = validate('solve.sh', b'echo 42', _REPO)
        self.assertFalse(result.ok)
        self.assertIn('not an editable', result.message)


if __name__ == '__main__':
    unittest.main()
