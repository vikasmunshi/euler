#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from euler_solver.setup.evaluate import evaluate, set_show_solution, show_solution
from euler_solver.setup.paths import base_dir
from euler_solver.setup.register import get_registry, register_solution
from euler_solver.setup.requests import get_text_file
from euler_solver.setup.resource_limits import set_resource_limits

__all__ = [
    'base_dir',
    'evaluate',
    'get_registry',
    'get_text_file',
    'register_solution',
    'set_resource_limits',
    'set_show_solution',
    'show_solution',
]

__package__ = 'euler_solver.setup'
