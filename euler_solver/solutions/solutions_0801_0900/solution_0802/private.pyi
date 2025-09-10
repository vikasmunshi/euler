#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 802: Iterated Composition.

Problem Statement:
    Let R^2 be the set of pairs of real numbers (x, y). Let π = 3.14159...

    Consider the function f from R^2 to R^2 defined by
    f(x, y) = (x^2 - x - y^2, 2xy - y + π), and its n-th iterated
    composition f^(n)(x, y) = f(f(... f(x, y)...)). For example
    f^(3)(x, y) = f(f(f(x, y))). A pair (x, y) is said to have period n
    if n is the smallest positive integer such that f^(n)(x, y) = (x, y).

    Let P(n) denote the sum of x-coordinates of all points having period not
    exceeding n. Interestingly, P(n) is always an integer. For example,
    P(1) = 2, P(2) = 2, P(3) = 4.

    Find P(10^7) and give your answer modulo 1020340567.

Solution Approach:
    Analyze the given iterated mapping in R^2 with polynomial and linear terms.
    To find points of period n, solve f^(n)(x,y) = (x,y) and identify minimal
    periods using fixed point and periodic orbit theory. Use algebraic geometry
    or computational algebra techniques to determine periodic points and sum x-coords.
    Efficient modular arithmetic and possible number-theoretic or dynamical system
    optimizations are needed for n=10^7.

Answer: ...
URL: https://projecteuler.net/problem=802
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 802
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 10000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_iterated_composition_p0802_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))