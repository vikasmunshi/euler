#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 316: Numbers in Decimal Expansions.

Problem Statement:
    Let p = p_1 p_2 p_3 ... be an infinite sequence of random digits,
    selected from {0,1,2,3,4,5,6,7,8,9} with equal probability.
    It can be seen that p corresponds to the real number 0.p_1 p_2 p_3 ...
    It can also be seen that choosing a random real number from [0,1) is
    equivalent to choosing an infinite sequence of random digits
    selected from {0,1,2,3,4,5,6,7,8,9} with equal probability.

    For any positive integer n with d decimal digits, let k be the smallest
    index such that p_k, p_{k + 1}, ..., p_{k + d - 1} are the decimal
    digits of n, in the same order.
    Also, let g(n) be the expected value of k; it can be proven that g(n)
    is always finite and, interestingly, always an integer number.

    For example, if n = 535, then
    for p = 31415926 535 897..., we get k = 9
    for p = 35528714365004956000049084876408468 535 4..., we get k = 36
    etc and we find that g(535) = 1008.

    Given that sum_{n = 2}^{999} g(floor(10^6 / n)) = 27280188, find
    sum_{n = 2}^{999999} g(floor(10^16 / n)).

Solution Approach:
    Model each integer's decimal representation as a finite string pattern.
    Compute g(n) as the expected waiting time to observe the pattern in
    a random digit stream: treat it as the hitting time of a DFA built
    from the pattern (use KMP prefix-function to build transitions).
    Solve linear equations for expected hitting time from automaton states
    or use dynamic programming on the Markov chain of prefix matches.
    Group n by identical floor(10^power / n) values to avoid recomputing.
    Complexity: dominated by sum over distinct patterns of O(L^3) or O(L^2)
    work per pattern for length L; organize to be feasible for the input.

Answer: ...
URL: https://projecteuler.net/problem=316
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 316
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n_max': 10, 'ten_power': 6}},
    {'category': 'main', 'input': {'n_max': 999999, 'ten_power': 16}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_numbers_in_decimal_expansions_p0316_s0(*, n_max: int, ten_power: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))