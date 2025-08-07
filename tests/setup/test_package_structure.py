#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the cached_requests module."""
import re
import unittest

from yaml import safe_load as load_yaml

from euler.setup import MAX_SHARABLE, base_dir


class TestPackageStructure(unittest.TestCase):
    def test_package_structure(self):
        """Test that the package root directory contains the expected directories."""
        package_structure = ['__init__.py',
                             'maths/__init__.py',
                             'resources',
                             'resources/data',
                             'setup/__init__.py',
                             'solutions/__init__.py',
                             'solutions/solutions_0001_0100/__init__.py',
                             'solutions/solutions_0101_0200/__init__.py',
                             'solutions/solutions_0201_0300/__init__.py',
                             'solutions/solutions_0301_0400/__init__.py',
                             'solutions/solutions_0401_0500/__init__.py',
                             'solutions/solutions_0501_0600/__init__.py',
                             'solutions/solutions_0601_0700/__init__.py',
                             'solutions/solutions_0701_0800/__init__.py',
                             'solutions/solutions_0801_0900/__init__.py',
                             'solutions/solutions_0901_1000/__init__.py', ]
        missing = [f for f in package_structure if not (base_dir / f).exists()]
        self.assertEqual(missing, [], msg=f'Missing: {missing}')

    def test_solution_files(self):
        """Test that the solution files have the correct module name and directory structure"""
        solutions_dir = base_dir / 'solutions'
        euler_problem_assignment_regex = re.compile(r'euler_problem\s*=\s*([0-9]+)')
        incorrect: list[str] = []
        for implementation_dir in solutions_dir.rglob('solution_[0-9][0-9][0-9][0-9]'):
            euler_problem: int = int(implementation_dir.name.split('_')[-1])
            yaml_file = implementation_dir / 'solution.yaml'
            if yaml_file.exists():
                with open(yaml_file, 'r') as f:
                    data = load_yaml(f)
                euler_problem_in_yaml: int | None = data.get('euler_problem')
                if euler_problem_in_yaml != euler_problem:
                    incorrect.append(f'{implementation_dir.name=} {euler_problem=} {euler_problem_in_yaml=}')
            if euler_problem > MAX_SHARABLE:
                py_file = implementation_dir / 'solution.py'
                if py_file.exists():
                    incorrect.append(f'{implementation_dir.name=} {py_file.name=}')
                json_file = implementation_dir / 'solution.json'
                if json_file.exists():
                    incorrect.append(f'{implementation_dir.name=} {json_file.name=}')
            py_file = implementation_dir / ('solution.py' if euler_problem <= MAX_SHARABLE else 'private.py')
            if py_file.exists():
                with open(py_file, 'r') as f:
                    source_code = f.read()
                for euler_problem_assignment in euler_problem_assignment_regex.findall(source_code):
                    if int(euler_problem_assignment) != euler_problem:
                        incorrect.append(f'{implementation_dir.name=} {py_file.name=} {euler_problem_assignment=}')
            elif euler_problem <= MAX_SHARABLE:
                incorrect.append(f'{implementation_dir.name=} {py_file.name=}')
            json_file = implementation_dir / ('solution.json' if euler_problem <= MAX_SHARABLE else 'private.json')
            if euler_problem <= MAX_SHARABLE and not json_file.exists():
                incorrect.append(f'{implementation_dir.name=} {json_file.name=}')

        self.assertEqual(incorrect, [], msg=f'Incorrect:\n{"\n".join(incorrect)}')

    def test_test_cases(self):
        solutions_dir = base_dir / 'solutions'
        incorrect: list[str] = []
        for implementation_dir in solutions_dir.rglob('solution_[0-9][0-9][0-9][0-9]'):
            euler_problem: int = int(implementation_dir.name.split('_')[-1])
            yaml_file = implementation_dir / 'solution.yaml'
            if yaml_file.exists():
                with open(yaml_file, 'r') as f:
                    data = load_yaml(f)
                test_case_categories = [test_case.get('test_case_category') for test_case in data.get('test_cases', [])]
                test_case_category_counts = {cat: test_case_categories.count(cat) for cat in set(test_case_categories)}
                if test_case_category_counts.get('main') != 1:
                    incorrect.append(f'{euler_problem=} {test_case_category_counts=}')
        self.assertEqual(incorrect, [], msg=f'Incorrect:\n{"\n".join(sorted(incorrect))}')


if __name__ == '__main__':
    unittest.main()
