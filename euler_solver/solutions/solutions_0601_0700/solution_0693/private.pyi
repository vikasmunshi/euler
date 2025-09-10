#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 693: Finite Sequence Generator.

Problem Statement:
    Two positive integers x and y (x > y) can generate a sequence in the following
    manner:
        a_x = y is the first term,
        a_{z+1} = a_z^2 mod z for z = x, x+1, x+2, ...
        the generation stops when a term becomes 0 or 1.

    The number of terms in this sequence is denoted l(x,y).

    For example, with x = 5 and y = 3, we get a_5 = 3, a_6 = 3^2 mod 5 = 4, a_7 =
    4^2 mod 6 = 4, etc., giving the sequence of 29 terms:
        3,4,4,2,4,7,9,4,4,3,9,6,4,16,4,16,16,4,16,3,9,6,10,19,25,16,16,8,0
    Hence l(5,3) = 29.

    g(x) is defined to be the maximum value of l(x,y) for y < x. For example, g(5) = 29.

    Further, define f(n) to be the maximum value of g(x) for x <= n. For example,
    f(100) = 145 and f(10000) = 8824.

    Find f(3000000).

Solution Approach:
    The problem involves modular arithmetic sequences and finding maximum sequence
    lengths stopping at terms 0 or 1. Key ideas include efficient simulation of the
    sequence generation using modular exponentiation properties, pruning sequences
    early, and caching results. Optimization may involve number theory and careful
    implementation to handle large n up to 3 million. The approach requires
    computational efficiency and possibly precomputation or heuristic pruning.

Answer: ...
URL: https://projecteuler.net/problem=693
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 693
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 3000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_finite_sequence_generator_p0693_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))