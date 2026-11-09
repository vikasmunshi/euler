#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for :func:`solver.core.listing.listable`: what `ls` and the site's files table show."""
from __future__ import annotations

import unittest
from pathlib import Path

from solver.core.listing import listable

ROOT = Path('/solutions/public/p0042')


class ListableTest(unittest.TestCase):

    def test_known_extensions_shown(self) -> None:
        for name in ('p0042_s0.py', 'p0042_s0.c', 'notes.html', 'resources/words.txt'):
            with self.subTest(name=name):
                self.assertTrue(listable(ROOT / name, ROOT))

    def test_no_extension_hidden(self) -> None:
        self.assertFalse(listable(ROOT / 'p0042_s0', ROOT))

    def test_pycache_hidden_at_any_depth(self) -> None:
        for name in ('__pycache__/p0042_s0.cpython-314.pyc', 'resources/__pycache__/helper.pyc'):
            with self.subTest(name=name):
                self.assertFalse(listable(ROOT / name, ROOT))

    def test_only_directories_below_root_count(self) -> None:
        """A file *named* like the directory is fine, and so is a root that sits under one."""
        self.assertTrue(listable(ROOT / '__pycache__.txt', ROOT))
        root = Path('/__pycache__/p0042')
        self.assertTrue(listable(root / 'notes.html', root))


if __name__ == '__main__':
    unittest.main()
