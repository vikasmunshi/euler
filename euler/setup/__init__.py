#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from euler.setup.encryption import decrypt_solution_module, encrypt_solution_module
from euler.setup.evaluate import evaluate, evaluate_and_get_evaluation_result, set_show_solution, show_solution
from euler.setup.module import get_module, get_test_cases_from_module
from euler.setup.paths import MAX_SHARABLE, base_dir
from euler.setup.register import framework_version, register_solution, set_record_all_test_cases
from euler.setup.requests import get_text_file
from euler.setup.result import EvaluationResult
from euler.setup.summary import create_summary

__all__ = [
    'EvaluationResult',
    'MAX_SHARABLE',
    'base_dir',
    'create_summary',
    'decrypt_solution_module',
    'encrypt_solution_module',
    'evaluate',
    'evaluate_and_get_evaluation_result',
    'framework_version',
    'get_module',
    'get_test_cases_from_module',
    'get_text_file',
    'register_solution',
    'set_record_all_test_cases',
    'set_show_solution',
    'show_solution',
]

__package__ = 'euler'
