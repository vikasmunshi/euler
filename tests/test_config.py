#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the configuration package's two load-bearing invariants.

**Importing it builds nothing.** No `Config`, no chdir, no `PATH` rewrite, no identity
resolution, no `rich`. The singleton is resolved on first *access*. That is what lets the
git filter, the five web service tiers and the tests read a path constant without having
their process relocated or a one-shot shell ticket consumed on their behalf — and, more
sharply, what lets `euler-auth`, `euler-msg` and `euler-ws` read `env.conf` at all: they
run from `/opt/euler` with no working tree, so a `Config` built underneath them would
raise at import and take the site down with euler-auth. Importing used to do all of it.

**`solver.config.config` is the singleton and never a module.** The static settings live
in `settings.py` precisely so that no submodule can claim that name: a `config` submodule
would bind itself over the package attribute the first time anything imported it by path,
and every `from solver.config import config` after that would quietly receive a module.
The check below tries exactly that import and asserts it changes nothing.

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

    def test_the_binding_survives_importing_every_submodule_by_path(self) -> None:
        """The hazard in full: import every submodule first, then ask for the name.

        None of them is called `config`, which is the whole defence — a submodule of that
        name would be bound over the package attribute by the import machinery itself,
        and no amount of care in `__init__` could take it back afterwards.
        """
        out = _probe('import solver.config.settings, solver.config.paths\n'
                     'import solver.config.values, solver.config.env\n'
                     'from solver.config import Config, config\n'
                     'print(type(config).__name__, isinstance(config, Config))')
        self.assertEqual(out, 'Config True')

    def test_no_module_is_named_config_inside_the_package(self) -> None:
        """Enforce the defence rather than trusting it: the name must stay unclaimed."""
        package = Path(__file__).resolve().parents[1] / 'solver' / 'config'
        self.assertFalse((package / 'config.py').exists(),
                         'a `config` submodule would shadow the singleton on the package')


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

    def test_importing_config_builds_no_config(self) -> None:
        """The singleton arrives on first access, not at import — see the module docstring."""
        out = _probe('import sys, solver.config\n'
                     "print('config' in vars(sys.modules['solver.config']))")
        self.assertEqual(out, 'False')

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
