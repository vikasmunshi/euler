#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 903: Total Permutation Powers.

Problem Statement:
    A permutation π of {1, ..., n} can be represented in one-line notation as
    π(1), ..., π(n). If all n! permutations are written in lexicographic order
    then rank(π) is the position of π in this 1-based list.

    For example, rank(2, 1, 3) = 3 because the six permutations of {1, 2, 3}
    in lexicographic order are:
    1, 2, 3
    1, 3, 2
    2, 1, 3
    2, 3, 1
    3, 1, 2
    3, 2, 1

    Let Q(n) be the sum sum_{π} sum_{i=1}^{n!} rank(π^i), where π ranges over all
    permutations of {1, ..., n}, and π^i is the permutation arising from applying
    π i times.

    For example, Q(2) = 5, Q(3) = 88, Q(6) = 133103808 and Q(10) ≡ 468421536
    (mod 10^9 + 7).

    Find Q(10^6). Give your answer modulo (10^9 + 7).

Solution Approach:
    The problem involves group theory (permutations and their powers), combinatorics,
    and modular arithmetic.
    Key ideas include decomposing permutations into cycle structures and understanding
    the effect of repeated permutation applications on cycle ranks.
    Efficient computation requires using number theory concepts (such as orders of elements),
    counting cycle structures, and leveraging fast modular arithmetic.
    Expected complexity needs careful optimization to handle n=10^6.

Answer: ...
URL: https://projecteuler.net/problem=903
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 903
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}},
    {'category': 'dev', 'input': {'n': 3}},
    {'category': 'main', 'input': {'n': 1000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_total_permutation_powers_p0903_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))