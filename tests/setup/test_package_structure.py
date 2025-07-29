#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the cached_requests module."""
import unittest

from euler.setup.base_dir import base_dir


class TestPackageStructure(unittest.TestCase):
    def test_package_structure(self):
        """Test that the package root directory contains the expected directories."""
        package_structure = ['__init__.py',
                             'cli/__init__.py',
                             'evaluator/__init__.py',
                             'maths/__init__.py',
                             'resources',
                             'resources/data',
                             'setup/__init__.py',
                             'solutions/__init__.py',
                             'solutions/set_0000/__init__.py',
                             'solutions/set_0001/__init__.py',
                             'solutions/set_0002/__init__.py',
                             'solutions/set_0003/__init__.py',
                             'solutions/set_0004/__init__.py',
                             'solutions/set_0005/__init__.py',
                             'solutions/set_0006/__init__.py',
                             'solutions/set_0007/__init__.py',
                             'solutions/set_0008/__init__.py',
                             'solutions/set_0009/__init__.py', ]
        missing = [f for f in package_structure if (base_dir / f).exists() is False]
        self.assertEqual(missing, [], msg=f'Missing: {missing}')


if __name__ == '__main__':
    unittest.main()
