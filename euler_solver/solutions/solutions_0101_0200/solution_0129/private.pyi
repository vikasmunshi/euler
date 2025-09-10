#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 129: Repunit Divisibility.

Problem Statement:
    A number consisting entirely of ones is called a repunit. We shall define
    R(k) to be a repunit of length k; for example, R(6) = 111111.
    Given that n is a positive integer and gcd(n, 10) = 1, it can be shown
    that there always exists a value k for which R(k) is divisible by n, and
    let A(n) be the least such value of k; for example, A(7) = 6 and A(41) = 5.
    The least value of n for which A(n) first exceeds ten is 17.
    Find the least value of n for which A(n) first exceeds one-million.

Solution Approach:
    Search n in increasing order, skipping n divisible by 2 or 5 (gcd(n,10)=1).
    For each candidate n compute the minimal k with R(k) ≡ 0 (mod n) by
    iterating remainders r = (r*10 + 1) % n until r == 0, counting steps.
    Use modular arithmetic and multiplicative order properties to optimize:
    factor n and test order divisors of 10 where applicable to prune work.
    Expected time depends on the threshold; naive search is O(sum A(n)) and
    may be slow without number-theory based shortcuts.

Answer: ...
URL: https://projecteuler.net/problem=129
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 129
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000000}},
    {'category': 'extra', 'input': {'max_limit': 2000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_repunit_divisibility_p0129_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))