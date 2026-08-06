#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the configuration package's two load-bearing invariants.

**`solver.config.config` is the singleton, not the submodule.** The static settings live
in a module of the same name inside the package, so importing it binds `config` on the
package to that *module*; `__init__` rebinds the name to the instance immediately
afterwards. Every one of the ~50 `from solver.config import config` call sites depends on
that rebinding having happened, and the failure mode is silent — attribute reads on a
module raise `AttributeError` far from the cause.

**Importing configuration does nothing.** No chdir, no `PATH` rewrite, no identity
resolution, no `rich`. This is what lets the git filter, the web service tiers and the
tests read a path constant without having their process relocated or a one-shot shell
ticket consumed on their behalf. It used to do all four, at import.

The purity checks run in a subprocess: this test process has long since imported
everything, so the question can only be asked of a fresh interpreter.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from solver.config import Config, config
from solver.config.paths import package_root, repo_root

#: Run from the repo root so the child resolves the same tree this process did.
_ROOT = repo_root()


def _probe(source: str) -> str:
    """Run *source* in a fresh interpreter at the repo root and return its stdout."""
    result = subprocess.run([sys.executable, '-c', source], capture_output=True, text=True, cwd=_ROOT)
    if result.returncode != 0:
        raise AssertionError(f'probe failed:\n{result.stderr}')
    return result.stdout.strip()


class SingletonBindingTests(unittest.TestCase):
    def test_config_is_the_instance_not_the_module(self) -> None:
        self.assertIsInstance(config, Config)

    def test_the_binding_survives_importing_the_submodule_by_path(self) -> None:
        """The hazard in full: import the *submodule* first, then ask for the name.

        A submodule cannot load without its parent package running to completion first,
        so `__init__`'s rebinding always wins — but only as long as the rebinding is the
        last thing `__init__` does with that name.
        """
        out = _probe('import solver.config.config\n'
                     'from solver.config import Config, config\n'
                     'print(type(config).__name__, isinstance(config, Config))')
        self.assertEqual(out, 'Config True')


class ImportPurityTests(unittest.TestCase):
    def test_importing_config_does_not_move_the_process(self) -> None:
        """`enter_repo` is the shell's explicit move; import is not."""
        out = _probe('import os, tempfile\n'
                     'os.chdir(tempfile.gettempdir())\n'
                     'before = os.getcwd()\n'
                     'import solver.config\n'
                     'print(before == os.getcwd())')
        self.assertEqual(out, 'True', 'importing solver.config changed the working directory')

    def test_importing_config_does_not_rewrite_path(self) -> None:
        out = _probe('import os\n'
                     'before = os.environ.get("PATH")\n'
                     'import solver.config\n'
                     'print(before == os.environ.get("PATH"))')
        self.assertEqual(out, 'True', 'importing solver.config rewrote PATH')

    def test_importing_config_resolves_no_identity(self) -> None:
        """`subject` is a `cached_property`: unresolved until something asks for it.

        `solver.auth` staying out of `sys.modules` is the stronger half — resolving a
        subject on the git-filter path consumes the web shell's one-shot ticket.
        """
        out = _probe('import sys\n'
                     'from solver.config import config\n'
                     'print("subject" in vars(config), "solver.auth" in sys.modules)')
        self.assertEqual(out, 'False False')

    def test_importing_config_does_not_import_rich(self) -> None:
        out = _probe('import sys\n'
                     'import solver.config\n'
                     'print("rich" in sys.modules, "prompt_toolkit" in sys.modules)')
        self.assertEqual(out, 'False False')

    def test_the_crypto_path_stays_silent_on_stdout(self) -> None:
        """The git filter's stdout carries file content; a stray print corrupts a solution."""
        out = _probe('import solver.crypto.gitfilter')
        self.assertEqual(out, '')


class AccessorAgreementTests(unittest.TestCase):
    """Item and attribute access answer the same question, stored or resolved."""

    def test_stored_settings_agree(self) -> None:
        self.assertEqual(config['timeout_single'], config.timeout_single)

    def test_resolved_settings_agree(self) -> None:
        self.assertIs(config['subject'], config.subject)

    def test_an_unknown_name_raises_the_right_error_for_each_channel(self) -> None:
        with self.assertRaises(KeyError):
            config['no_such_setting']
        with self.assertRaises(AttributeError):
            config.no_such_setting


class AnchorTests(unittest.TestCase):
    def test_package_root_is_the_solver_package(self) -> None:
        self.assertEqual(package_root.name, 'solver')
        self.assertTrue((package_root / 'modules.csv').is_file())

    def test_repo_root_holds_the_checkout(self) -> None:
        root: Path = repo_root()
        self.assertTrue((root / 'solver').is_dir())
        self.assertTrue((root / 'solutions').is_dir())


if __name__ == '__main__':
    unittest.main()
