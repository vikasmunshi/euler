#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from euler_solver.framework.c_lib import get_use_py_func, import_c_lib, set_use_py_func, use_c_function
from euler_solver.framework.evaluate import Mode, evaluate, evaluate_range, set_show_solution, show_solution
from euler_solver.framework.loader import get_key, load_locked_module, lock_private_files, unlock_private_files
from euler_solver.framework.logger import logger
from euler_solver.framework.paths import MAX_SHARABLE, base_dir
from euler_solver.framework.register import get_registry, register_solution, set_evaluation_options
from euler_solver.framework.requests import get_text_file
from euler_solver.framework.resource_limits import set_resource_limits
from euler_solver.framework.result import ColorCodes, EvaluationResult
from euler_solver.framework.summary import create_summary

__all__ = [
    'ColorCodes',
    'EvaluationResult',
    'MAX_SHARABLE',
    'Mode',
    'base_dir',
    'create_summary',
    'evaluate',
    'evaluate_range',
    'get_key',
    'get_registry',
    'get_text_file',
    'get_use_py_func',
    'import_c_lib',
    'load_locked_module',
    'lock_private_files',
    'logger',
    'register_solution',
    'set_evaluation_options',
    'set_resource_limits',
    'set_show_solution',
    'set_use_py_func',
    'set_use_py_func',
    'show_solution',
    'unlock_private_files',
    'use_c_function',
]
