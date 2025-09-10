#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 844: k-Markov Numbers.

Problem Statement:
    Consider positive integer solutions to
        a^2+b^2+c^2 = 3abc
    For example, (1,5,13) is a solution. We define a 3-Markov number to be any part
    of a solution, so 1, 5 and 13 are all 3-Markov numbers. Adding distinct 3-Markov
    numbers ≤ 10^3 would give 2797.

    Now we define a k-Markov number to be a positive integer that is part of a solution to:
        sum_{i=1}^k x_i^2 = k * product_{i=1}^k x_i,
        where x_i are positive integers.

    Let M_k(N) be the sum of k-Markov numbers ≤ N. Hence M_3(10^3)=2797, also
    M_8(10^8) = 131493335.

    Define S(K,N) = sum_{k=3}^K M_k(N). You are given S(4, 10^2)=229 and
    S(10, 10^8)=2383369980.

    Find S(10^{18}, 10^{18}). Give your answer modulo 1_405_695_061.

Solution Approach:
    Use number theory and algebraic manipulation to find integer solutions for the
    equations defined. Employ combinatorics to sum distinct k-Markov numbers.
    Efficient enumeration or closed-form formulas for M_k(N) and S(K,N) will be
    necessary due to large constraints. Modular arithmetic is required for the
    final result. Time complexity should handle up to 10^{18} inputs efficiently,
    suggesting deep mathematical insight or formula derivation.

Answer: ...
URL: https://projecteuler.net/problem=844
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 844
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'K': 4, 'N': 100}},
    {'category': 'main', 'input': {'K': 10, 'N': 100000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_k_markov_numbers_p0844_s0(*, K: int, N: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))