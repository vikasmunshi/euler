#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 812: Dynamical Polynomials.

Problem Statement:
    A dynamical polynomial is a monic polynomial f(x) with integer coefficients such
    that f(x) divides f(x^2-2).

    For example, f(x) = x^2 - x - 2 is a dynamical polynomial because
    f(x^2-2) = x^4 - 5x^2 + 4 = (x^2 + x - 2) f(x).

    Let S(n) be the number of dynamical polynomials of degree n.
    For example, S(2) = 6, as there are six dynamical polynomials of degree 2:
    x^2 - 4x + 4, x^2 - x - 2, x^2 - 4, x^2 - 1, x^2 + x - 1, x^2 + 2x + 1.

    Also, S(5) = 58 and S(20) = 122087.

    Find S(10 000). Give your answer modulo 998244353.

Solution Approach:
    Use algebraic and number theoretic properties of polynomials with functional
    equations. Key ideas include studying polynomial divisibility conditions with
    polynomial composition, characteristic equations from functional iteration,
    and modular arithmetic for the large output. Employ combinatorics and
    possibly linear algebra on polynomial coefficient spaces. Complexity depends
    on efficient symbolic manipulations and modular arithmetic.

Answer: ...
URL: https://projecteuler.net/problem=812
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 812
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}},
    {'category': 'main', 'input': {'n': 10000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_dynamical_polynomials_p0812_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
