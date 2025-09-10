#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 836: A Bold Proposition.

Problem Statement:
    Let A be an affine plane over a radically integral local field F with residual
    characteristic p.

    We consider an open oriented line section U of A with normalized Haar measure m.

    Define f(m, p) as the maximal possible discriminant of the jacobian associated to
    the orthogonal kernel embedding of U into A.

    Find f(20230401, 57). Give as your answer the concatenation of the first letters
    of each bolded word.

Solution Approach:
    This problem involves advanced algebraic geometry concepts such as affine planes,
    local fields, Haar measure, jacobians, and orthogonal kernels. Key mathematical
    ideas include algebraic geometry, local field theory, and measure normalization.
    The solution likely requires symbolic or theoretical reasoning about these
    structures. Complexity depends on deep mathematical insights rather than
    computational complexity.

Answer: ...
URL: https://projecteuler.net/problem=836
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 836
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'m': 20230401, 'p': 57}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_a_bold_proposition_p0836_s0(*, m: int, p: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))