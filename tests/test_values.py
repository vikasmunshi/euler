#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for `values.conf` and the reader that overlays it onto the declared defaults.

The file is **data, not code**: it is hand-edited, it survives a release that retires a
setting, and nothing in it may be able to stop the shell from starting. The retired-key
case is the one that actually bit — dropping `server_port` from the old managed set made
every older config file raise `KeyError` at import, before anything could print an error
saying so. Those cases are pinned here in their new form.

The other half is the shipped file itself. Every setting has a default in `config.py` (the
safety net) *and* a line in `values.conf` (the catalogue, and the place to change it), so
the two can drift. `ShippedValuesTests` holds them to each other: build the configuration
with the file and without it, and the only setting allowed to differ is the one a command
maintains.
"""
from __future__ import annotations

import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

from solver.config import build_config, settable_fields
from solver.config.settings import Scripts, values_file_for
from solver.config.paths import repo_root
from solver.config.values import ValuesError, read_sections, set_value

#: Settings a *command* keeps up to date, so the shipped file is expected to have moved on
#: from the declared default. `ecb_usd_rate` is refreshed from the ECB feed by
#: `update-usd-rate`; everything else in the file is chosen by a person and must match.
_MAINTAINED: frozenset[str] = frozenset({'ecb_usd_rate'})

_ROOT: Path = repo_root()
#: A path that does not exist — `build_config` then yields the pure declared defaults.
_NO_FILE: Path = Path('/nonexistent/values.conf')

#: Enough of an anchor set to let the shipped file's `${...}` references resolve; what the
#: anchors actually expand to is `build_config`'s business, not this reader's.
_ANCHORS: dict[str, str] = {'root_dir': str(_ROOT), 'package_dir': str(_ROOT / 'solver'),
                            'secrets_dir': str(_ROOT.parent / '.euler'), 'home_dir': str(Path.home())}


class ShippedValuesTests(unittest.TestCase):
    """The shipped file and the declared defaults say the same thing."""

    def setUp(self) -> None:
        self.from_file = build_config(root=_ROOT)
        self.from_defaults = build_config(root=_ROOT, values_file=_NO_FILE)

    def test_every_setting_agrees_with_its_declared_default(self) -> None:
        for name in settable_fields():
            if name in _MAINTAINED:
                continue
            with self.subTest(setting=name):
                self.assertEqual(getattr(self.from_file, name), getattr(self.from_defaults, name),
                                 f'values.conf and the default declared in config.py disagree '
                                 f'about `{name}`')

    def test_the_scripts_section_agrees_too(self) -> None:
        self.assertEqual(self.from_file.scripts, self.from_defaults.scripts)

    def test_the_file_names_every_setting(self) -> None:
        """The catalogue is complete: a setting missing from the file cannot be found."""
        sections = read_sections(values_file_for(_ROOT), _ANCHORS)
        named = {key for section, items in sections.items() if section != 'scripts' for key in items}
        self.assertEqual(named, set(settable_fields()),
                         'values.conf and the declared settings differ (left: file only, '
                         'right: class only)')

    def test_the_file_names_every_script(self) -> None:
        sections = read_sections(values_file_for(_ROOT), _ANCHORS)
        self.assertEqual(set(sections.get('scripts', {})), set(Scripts._fields))

    def test_no_field_is_left_underived(self) -> None:
        """Every declared path resolves — the `_DERIVED` sentinel never reaches a caller."""
        for spec in fields(self.from_defaults):
            value = getattr(self.from_defaults, spec.name)
            if isinstance(value, Path):
                with self.subTest(setting=spec.name):
                    self.assertNotIn('\x00', str(value), f'{spec.name} was never derived')


class OverlayTests(unittest.TestCase):
    """What a values file may and may not do to a running shell."""

    def _write(self, text: str) -> Path:
        path = Path(tempfile.mkdtemp(prefix='euler-values-test-')) / 'values.conf'
        path.write_text(text, encoding='utf-8')
        return path

    def test_a_value_overrides_the_declared_default(self) -> None:
        config = build_config(root=_ROOT, values_file=self._write('[limits]\ntimeout_single = 42.5\n'))
        self.assertEqual(config.timeout_single, 42.5)

    def test_a_retired_setting_is_ignored_rather_than_fatal(self) -> None:
        """The `server_port` lesson: an older file must not stop the shell from starting."""
        config = build_config(root=_ROOT, values_file=self._write('[limits]\nserver_port = 8080\n'))
        self.assertFalse(hasattr(config, 'server_port'))

    def test_an_uncoercible_value_leaves_the_default_standing(self) -> None:
        config = build_config(root=_ROOT, values_file=self._write('[limits]\ntimeout_single = soon\n'))
        self.assertEqual(config.timeout_single, build_config(root=_ROOT, values_file=_NO_FILE).timeout_single)

    def test_a_malformed_file_is_not_fatal(self) -> None:
        config = build_config(root=_ROOT, values_file=self._write('this is not an ini file at all\n'))
        self.assertEqual(config.timeout_single, 90.0)

    def test_a_missing_file_is_not_fatal(self) -> None:
        self.assertEqual(build_config(root=_ROOT, values_file=_NO_FILE).timeout_single, 90.0)

    def test_anchors_interpolate(self) -> None:
        config = build_config(root=_ROOT, values_file=self._write('[paths]\ntopics_dir = ${root_dir}/elsewhere\n'))
        self.assertEqual(config.topics_dir, _ROOT / 'elsewhere')

    def test_a_key_set_in_two_sections_is_refused(self) -> None:
        """Two lines claiming one setting have no defensible winner."""
        path = self._write('[limits]\ntimeout_single = 1.0\n\n[names]\ntimeout_single = 2.0\n')
        with self.assertRaises(ValuesError):
            build_config(root=_ROOT, values_file=path)

    def test_an_inline_comment_is_not_part_of_the_value(self) -> None:
        config = build_config(root=_ROOT, values_file=self._write('[limits]\ntimeout_single = 7.0  # why\n'))
        self.assertEqual(config.timeout_single, 7.0)


class SetValueTests(unittest.TestCase):
    """`update-usd-rate` writes one line; everything around it survives."""

    def setUp(self) -> None:
        self.path = Path(tempfile.mkdtemp(prefix='euler-setvalue-test-')) / 'values.conf'
        self.path.write_text('# a heading comment\n\n[rates]\n'
                             '# why this number is what it is\n'
                             'ecb_usd_rate = 1.0000  # maintained\n\n'
                             '[limits]\ntimeout_single = 90.0\n', encoding='utf-8')

    def test_the_value_is_replaced(self) -> None:
        set_value(self.path, 'ecb_usd_rate', 1.2345)
        self.assertIn('ecb_usd_rate = 1.2345', self.path.read_text())

    def test_the_comments_and_the_rest_survive(self) -> None:
        set_value(self.path, 'ecb_usd_rate', 1.2345)
        text = self.path.read_text()
        self.assertIn('# a heading comment', text)
        self.assertIn('# why this number is what it is', text)
        self.assertIn('# maintained', text)
        self.assertIn('timeout_single = 90.0', text)

    def test_it_reads_back_as_what_was_written(self) -> None:
        set_value(self.path, 'ecb_usd_rate', 1.2345)
        self.assertEqual(build_config(root=_ROOT, values_file=self.path).ecb_usd_rate, 1.2345)

    def test_an_unknown_key_is_refused_rather_than_appended(self) -> None:
        with self.assertRaises(ValuesError):
            set_value(self.path, 'not_a_setting', 1)


if __name__ == '__main__':
    unittest.main()
