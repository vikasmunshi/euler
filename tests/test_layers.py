#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the layering guard (scripts/linters/layers.py): euler_webshell → euler_site →
solver, never upward, and the allowlist of known exceptions only ratchets down."""
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
        self.write('packages/solver/solver/core/a.py', 'from euler_webshell.msg import X\n')
        self.write('packages/solver/solver/core/b.py', 'def f():\n    import euler_site.auth.client\n')
        self.write('packages/solver/solver/core/c.py', 'from euler_webshell import roster\n')
        self.write('packages/solver/solver/core/d.py', 'from solver.core import problems\n')       # fine
        self.assertEqual(layers.violations(self.root), {
            ('packages/solver/solver/core/a.py', 'euler_webshell.msg'),
            ('packages/solver/solver/core/b.py', 'euler_site.auth.client'),
            ('packages/solver/solver/core/c.py', 'euler_webshell'),
        })

    def test_the_site_may_import_the_solver_but_not_the_web_shell(self) -> None:
        self.write('packages/site/euler_site/app.py', 'from solver.core import problems\nfrom euler_site import csp\n')
        self.write('packages/site/euler_site/bad.py', 'from euler_webshell.msg import notify\n')
        self.write('packages/webshell/euler_webshell/ok.py', 'from euler_site import csp\nimport solver.main\n')
        self.assertEqual(layers.violations(self.root), {('packages/site/euler_site/bad.py', 'euler_webshell.msg')})

    def test_the_manifest_may_load_only_the_solvers_command_modules(self) -> None:
        self.write('packages/solver/solver/modules.csv', 'module,registers_commands\n'
                                                         'euler_webshell.users,True\neuler_site.app,\n'
                                                         'solver.core.git,True\n')
        self.assertEqual(layers.violations(self.root),
                         {('packages/solver/solver/modules.csv', 'euler_webshell.users')})

    def test_allowlist_admits_known_and_fails_new_and_stale(self) -> None:
        self.write('packages/solver/solver/core/a.py', 'from euler_webshell.msg import X\n')
        self.allow.write_text('# known\npackages/solver/solver/core/a.py euler_webshell.msg\n', encoding='utf-8')
        self.assertEqual(self.check()[0], 0)
        self.write('packages/solver/solver/core/b.py', 'import euler_webshell.msg\n')
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn('packages/solver/solver/core/b.py: imports euler_webshell.msg', out)
        self.write('packages/solver/solver/core/a.py', '\n')
        self.write('packages/solver/solver/core/b.py', '\n')
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
