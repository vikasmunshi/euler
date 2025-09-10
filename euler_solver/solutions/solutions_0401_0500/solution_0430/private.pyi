#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 430: Range Flips.

Problem Statement:
    N disks are placed in a row, indexed 1 to N from left to right.
    Each disk has a black side and white side. Initially all disks show their white side.

    At each turn, two, not necessarily distinct, integers A and B between 1 and N (inclusive)
    are chosen uniformly at random.
    All disks with an index from A to B (inclusive) are flipped.

    The following example shows the case N = 8. At the first turn A = 5 and B = 2, and at the
    second turn A = 4 and B = 6.

    Let E(N, M) be the expected number of disks that show their white side after M turns.
    We can verify that E(3, 1) = 10/9, E(3, 2) = 5/3, E(10, 4) ≈ 5.157 and E(100, 10) ≈ 51.893.

    Find E(10^10, 4000).
    Give your answer rounded to 2 decimal places behind the decimal point.

Solution Approach:
    Use probability and linearity of expectation.
    The state of each disk after flips can be modeled using parity of flips affecting it.
    Compute the probability a disk is white by summing over all possible flips.
    Use formulas for geometric series and closed forms for efficient expectation calculation.
    The problem involves combinatorics and probability with large inputs; O(N) direct simulation is
    infeasible.
    Aim for an O(M) or O(1) formula exploiting uniform random choices and symmetry.

Answer: ...
URL: https://projecteuler.net/problem=430
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 430
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3, 'm': 2}},
    {'category': 'main', 'input': {'n': 10000000000, 'm': 4000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_range_flips_p0430_s0(*, n: int, m: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))