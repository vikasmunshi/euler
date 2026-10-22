#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the layering guard (scripts/linters/layers.py): the solver shell must not
import the web tier, and the allowlist of known couplings only ratchets down."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import textwrap
import unittest
from pathlib import Path
from types import ModuleType

_SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'linters' / 'layers.py'


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location('layers', _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


layers = _load()


class LayersTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.allow = self.root / 'layers.allow'
        self.allow.write_text('', encoding='utf-8')

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text), encoding='utf-8')

    def check(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = layers.check(self.root, self.allow)
        return rc, out.getvalue()

    def test_finds_top_level_lazy_and_submodule_imports(self) -> None:
        self.write('solver/core/a.py', 'from solver.web.msg import X\n')
        self.write('solver/core/b.py', 'def f():\n    import solver.web.auth.client\n')
        self.write('solver/core/c.py', 'from solver.auth import roster\n')
        self.write('solver/core/d.py', 'from solver.core import problems\n')       # fine
        self.assertEqual(layers.violations(self.root), {
            ('solver/core/a.py', 'solver.web.msg'),
            ('solver/core/b.py', 'solver.web.auth.client'),
            ('solver/core/c.py', 'solver.auth.roster'),
        })

    def test_web_side_modules_may_import_anything(self) -> None:
        self.write('solver/web/site/app.py', 'from solver.web.msg import X\n')
        self.write('solver/auth/roster.py', 'from solver.web import csp\n')
        self.assertEqual(layers.violations(self.root), set())

    def test_the_manifest_may_not_load_web_command_modules(self) -> None:
        self.write('solver/modules.csv', 'module,registers_commands\n'
                                         'solver.web.msg.commands,True\nsolver.web.msg.app,\nsolver.core.git,True\n')
        self.assertEqual(layers.violations(self.root), {('solver/modules.csv', 'solver.web.msg.commands')})

    def test_allowlist_admits_known_and_fails_new_and_stale(self) -> None:
        self.write('solver/core/a.py', 'from solver.web.msg import X\n')
        self.allow.write_text('# known\nsolver/core/a.py solver.web.msg\n', encoding='utf-8')
        self.assertEqual(self.check()[0], 0)
        self.write('solver/core/b.py', 'import solver.web.msg\n')
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn('solver/core/b.py: imports web-side solver.web.msg', out)
        self.write('solver/core/a.py', '\n')
        self.write('solver/core/b.py', '\n')
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn('stale entry', out)

    def test_the_repository_is_clean_against_its_allowlist(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = layers.check(_SCRIPT.parents[2])
        self.assertEqual(rc, 0, out.getvalue())


if __name__ == '__main__':
    unittest.main()
