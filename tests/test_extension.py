#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Unit tests for the extension mechanism (solver.shell.extension): overlays that emit events
after a command and replace a command's body, and the refusals that keep the two sides in step."""
from __future__ import annotations

import contextlib
import tempfile
import unittest
from pathlib import Path
from typing import Iterator

from solver.auth import Subject
from solver.config import config
from solver.shell.command import Context, registry
from solver.core import notices
from solver.shell import extension as extension_mod
from solver.shell.extension import (Extension, ExtensionError, Overlay, active, apply_overlays, load_extension,
                                    read_overlays)
from solver.shell.register import register
from tests import silence

silence()

_calls: list[str] = []


@contextlib.contextmanager
def as_profile(profile: str) -> Iterator[None]:
    saved = config.subject
    config.subject = Subject(user='t', slug='t-000000', channel='terminal', auth_method='test', profile=profile)
    try:
        yield
    finally:
        config.subject = saved


def zz_ext_echo(word: str, times: int = 1) -> int:
    """Test command: record *word*."""
    _calls.append(f'orig:{word}x{times}')
    return 0 if word != 'fail' else 3


def zz_ext_admin() -> int:
    """Test command above the reader floor."""
    return 0


def _replacement(word: str, times: int = 1) -> int:
    """Not the docstring the help shows."""
    _calls.append(f'repl:{word}x{times}')
    return 0


def _misfit(word: str) -> int:
    return 0


def _run(name: str, *argv: str) -> int:
    cmd = registry.resolve(name)
    assert cmd is not None
    return cmd.invoke(Context(argv=list(argv)))


class ExtensionTests(unittest.TestCase):
    def setUp(self) -> None:
        _calls.clear()
        self.events: list[str] = []
        with as_profile('reader'):
            register(requires='reader', aliases=('zz-ext-e',))(zz_ext_echo)
            register(requires='admin')(zz_ext_admin)

    def tearDown(self) -> None:
        for name in ('zz-ext-echo', 'zz-ext-admin'):
            registry.unregister(name)
        registry.withheld.discard('zz-ext-admin')

    def ext(self, *overlays: Overlay) -> Extension:
        return Extension(overlays=overlays, notify=self.events.append)

    def test_emit_fires_after_the_command_whatever_its_exit_code(self) -> None:
        apply_overlays(self.ext(Overlay('zz-ext-echo', emit=('git', 'progress'))))
        self.assertEqual(_run('zz-ext-echo', 'hi'), 0)
        self.assertEqual(_run('zz-ext-echo', 'fail'), 3)            # rc passes through
        self.assertEqual(self.events, ['git', 'progress'] * 2)
        self.assertEqual(_calls, ['orig:hix1', 'orig:failx1'])

    def test_replace_runs_the_new_body_behind_the_original_contract(self) -> None:
        cmd = registry.resolve('zz-ext-echo')
        assert cmd is not None
        help_before, usage_before = cmd.help, cmd.usage
        apply_overlays(self.ext(Overlay('zz-ext-echo', replace=f'{__name__}:_replacement')))
        self.assertEqual(_run('zz-ext-echo', 'hi', 'times=2'), 0)   # same parsing and coercion
        self.assertEqual(_calls, ['repl:hix2'])
        self.assertEqual((cmd.help, cmd.usage), (help_before, usage_before))

    def test_a_replacement_with_another_signature_is_refused(self) -> None:
        with self.assertRaisesRegex(ExtensionError, 'does not match the signature'):
            apply_overlays(self.ext(Overlay('zz-ext-echo', replace=f'{__name__}:_misfit')))

    def test_an_unresolvable_replacement_is_refused(self) -> None:
        with self.assertRaises(ExtensionError):
            apply_overlays(self.ext(Overlay('zz-ext-echo', replace=f'{__name__}:_nowhere')))

    def test_a_misfit_anywhere_applies_nothing(self) -> None:
        """Checked before applied: the shell refuses to start, so a half-applied table never runs."""
        with self.assertRaises(ExtensionError):
            apply_overlays(self.ext(Overlay('zz-ext-echo', emit=('git',)), Overlay('zz-ext-nothing', emit=('git',))))
        self.assertEqual(_run('zz-ext-echo', 'hi'), 0)
        self.assertEqual(self.events, [])

    def test_an_overlay_on_no_command_is_refused(self) -> None:
        with self.assertRaisesRegex(ExtensionError, 'names no command'):
            apply_overlays(self.ext(Overlay('zz-ext-nothing', emit=('git',))))

    def test_an_overlay_must_use_the_command_name_not_an_alias(self) -> None:
        with self.assertRaisesRegex(ExtensionError, 'an alias of'):
            apply_overlays(self.ext(Overlay('zz-ext-e', emit=('git',))))

    def test_an_overlay_on_a_withheld_command_is_skipped(self) -> None:
        self.assertIn('zz-ext-admin', registry.withheld)            # reader is below its floor
        apply_overlays(self.ext(Overlay('zz-ext-admin', emit=('git',))))

    def test_emitting_without_notify_is_refused(self) -> None:
        with self.assertRaisesRegex(ExtensionError, 'no notify'):
            apply_overlays(Extension(overlays=(Overlay('zz-ext-echo', emit=('git',)),)))

    def test_loading_installs_the_notices_carrier(self) -> None:
        class Carrier:
            def to_staff(self, subject: str, body: str) -> bool:
                return True

            def dismiss(self, subject: str) -> bool:
                return True

            def key_hint(self) -> str:
                return 'by pigeon'

        try:
            load_extension(Extension(notices=Carrier()))
            self.assertTrue(notices.to_staff('s', 'b'))
            self.assertEqual(notices.key_hint(), 'by pigeon')
            self.assertIsNotNone(active())
        finally:
            notices.install(None)
            extension_mod._active = None
        self.assertFalse(notices.to_staff('s', 'b'), 'with no carrier nothing is delivered')
        self.assertIn('host-unlock', notices.key_hint())

    def test_an_unimportable_module_is_refused(self) -> None:
        with self.assertRaisesRegex(ExtensionError, 'module'):
            load_extension(Extension(modules=('solver.no_such_module',)))


class ReadOverlaysTests(unittest.TestCase):
    def read(self, text: str) -> tuple[Overlay, ...]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'overlays.toml'
            path.write_text(text, encoding='utf-8')
            return read_overlays(path)

    def test_reads_emit_and_replace(self) -> None:
        overlays = self.read('[git-pull]\nemit = ["git"]\n\n[show]\nreplace = "pkg.viewer:show"\n')
        self.assertEqual(overlays, (Overlay('git-pull', emit=('git',)), Overlay('show', replace='pkg.viewer:show')))

    def test_rejects_malformed_entries(self) -> None:
        for text in ('[x]\nwhen = "always"\n',          # unknown key
                     '[x]\n',                            # empty
                     '[x]\nemit = "git"\n',              # not a list
                     '[x]\nreplace = "no_colon"\n',      # not module:attr
                     '[x\n'):                            # not TOML
            with self.subTest(text=text), self.assertRaises(ExtensionError):
                self.read(text)


if __name__ == '__main__':
    unittest.main()
