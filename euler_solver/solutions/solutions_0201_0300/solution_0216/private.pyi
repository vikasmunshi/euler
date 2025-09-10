#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 216: The Primality of 2n^2 - 1.

Problem Statement:
    Consider numbers t(n) of the form t(n) = 2n^2 - 1 with n > 1.
    The first such numbers are 7, 17, 31, 49, 71, 97, 127 and 161.
    It turns out that only 49 = 7 * 7 and 161 = 7 * 23 are not prime.
    For n <= 10000 there are 2202 numbers t(n) that are prime.

    How many numbers t(n) are prime for n <= 50000000?

Solution Approach:
    Use number theory and a sieve-like approach. For each odd prime p, solve the
    quadratic congruence 2 n^2 ≡ 1 (mod p) to find residue classes of n where
    t(n) is divisible by p, then mark those n as composite. Count unmarked n.
    Key ideas: quadratic residues, modular arithmetic, sieve over n up to N.
    Expected complexity: roughly O(N log log N) time with O(N) memory for sieve.

Answer: ...
URL: https://projecteuler.net/problem=216
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 216
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 50000000}},
    {'category': 'extra', 'input': {'max_limit': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_the_primality_of_2n2_minus_1_p0216_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))