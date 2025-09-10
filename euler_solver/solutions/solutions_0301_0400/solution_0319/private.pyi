#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 319: Bounded Sequences.

Problem Statement:
    Let x_1, x_2, ..., x_n be a sequence of length n such that:
    x_1 = 2
    for all 1 < i <= n: x_{i-1} < x_i
    for all i and j with 1 <= i, j <= n: (x_i)^j < (x_j + 1)^i

    There are only five such sequences of length 2, namely:
    {2,4}, {2,5}, {2,6}, {2,7} and {2,8}.
    There are 293 such sequences of length 5; three examples are:
    {2,5,11,25,55}, {2,6,14,36,88}, {2,8,22,64,181}.

    Let t(n) denote the number of such sequences of length n.
    You are given that t(10) = 86195 and t(20) = 5227991891.

    Find t(10^10) and give your answer modulo 10^9.

Solution Approach:
    Use the inequality j*log(x_i) < i*log(x_j+1) to transform constraints.
    The monotonicity and inequalities yield a finite set of feasible values per
    index; model allowed transitions between values as a DAG and count paths.
    Count sequences by dynamic programming over indices, aggregating transitions.
    For n = 10^10 lift the DP by constructing a transition matrix of states
    and applying fast matrix exponentiation modulo 10^9. Expect O(k^3 log n)
    with k the number of states, reducible with sparsity and cumulative sums.

Answer: ...
URL: https://projecteuler.net/problem=319
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 319
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}},
    {'category': 'main', 'input': {'n': 10000000000}},
    {'category': 'extra', 'input': {'n': 20}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_bounded_sequences_p0319_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))