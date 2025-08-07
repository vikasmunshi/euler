#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from euler.setup.base_dir import base_dir
from euler.setup.cached_requests import get_text_file
from euler.setup.evaluate import (EvaluationResult, evaluate, evaluate_and_get_evaluation_result, set_show_solution,
                                  show_solution)
from euler.setup.solution_info import SolutionInfo
from euler.setup.solution_registry import get_registered_solutions, register_solution
from euler.setup.test_case import MAX_SHARABLE, TestCase, TestCaseCategory

__all__ = [
    'EvaluationResult',
    'MAX_SHARABLE',
    'SolutionInfo',
    'TestCase',
    'TestCaseCategory',
    'base_dir',
    'evaluate',
    'evaluate_and_get_evaluation_result',
    'get_registered_solutions',
    'get_text_file',
    'register_solution',
    'set_show_solution',
    'show_solution',
]
