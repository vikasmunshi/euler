#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the managed-settings overlay (solver.config.Config.load_managed_config).

``solver/config.json`` is **data, not code**: it may be hand-edited, may survive a
release that retires a setting, and must never be able to break startup or reach a
setting that is not managed. These pin that contract — the retired-key case is the
one that bit: dropping ``server_port`` from ``managed`` made every older config.json
raise ``KeyError`` at import, before the shell could even print an error.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from solver.config import config


class LoadManagedConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = {param: config._data[param] for param in config.managed}
        self._tmp = Path(tempfile.mkdtemp(prefix='euler-cfg-test-')) / 'config.json'
        self._saved_file = config.managed_config_file
        type(config).managed_config_file = self._tmp
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        type(config).managed_config_file = self._saved_file
        config._data.update(self._saved)

    def _write(self, data: dict[str, object]) -> None:
        self._tmp.write_text(json.dumps(data))

    def test_managed_values_are_overlaid(self) -> None:
        self._write({'timeout_single': 42.0})
        config.load_managed_config()
        self.assertEqual(config.timeout_single, 42.0)

    def test_a_retired_setting_is_ignored_not_fatal(self) -> None:
        """A key dropped from `managed` may still sit in an older file — skip it."""
        self._write({'server_port': 8080, 'timeout_single': 42.0})
        config.load_managed_config()                     # must not raise
        self.assertEqual(config.timeout_single, 42.0)    # …and the rest still applies
        self.assertNotIn('server_port', config._data)

    def test_an_unmanaged_key_cannot_reach_the_settings(self) -> None:
        """The file may only touch `managed`: it must not redirect root_dir & co."""
        before = config.root_dir
        self._write({'root_dir': '/tmp/nowhere', 'base_url': 'http://evil.example'})
        config.load_managed_config()
        self.assertEqual(config.root_dir, before)
        self.assertNotEqual(config.base_url, 'http://evil.example')

    def test_a_bad_value_is_skipped_not_fatal(self) -> None:
        self._write({'timeout_single': 'not-a-number'})
        config.load_managed_config()                     # must not raise
        self.assertIsInstance(config.timeout_single, float)

    def test_a_missing_or_malformed_file_is_not_fatal(self) -> None:
        config.load_managed_config()                     # file absent
        self._tmp.write_text('{ not json')
        config.load_managed_config()
        self.assertIsInstance(config.timeout_single, float)


if __name__ == '__main__':
    unittest.main()
