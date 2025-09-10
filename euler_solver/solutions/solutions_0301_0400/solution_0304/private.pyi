#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 304: Primonacci.

Problem Statement:
    For any positive integer n the function next_prime(n) returns the smallest
    prime p such that p > n.

    The sequence a(n) is defined by:
    a(1) = next_prime(10^14) and a(n) = next_prime(a(n-1)) for n > 1.

    The Fibonacci sequence f(n) is defined by:
    f(0) = 0, f(1) = 1 and f(n) = f(n-1) + f(n-2) for n > 1.

    The sequence b(n) is defined as f(a(n)).

    Find sum_{n=1..100000} b(n). Give your answer mod 1234567891011.

Solution Approach:
    Number theory and modular arithmetic: compute Fibonacci numbers modulo M =
    1234567891011 using fast doubling. Reduce indices modulo the Pisano period
    of M; compute that period by factoring M and combining periods via lcm.
    Generate successive primes a(n) starting from next_prime(10^14) using a
    fast primality test (Miller-Rabin) and stepping by odd integers; expect
    ~log(10^14) gap sizes so 100000 steps are feasible. Overall complexity
    dominated by primality tests and modular Fibonacci (fast doubling) calls.

Answer: ...
URL: https://projecteuler.net/problem=304
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 304
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}},
    {'category': 'main', 'input': {'n': 100000}},
    {'category': 'extra', 'input': {'n': 1000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_primonacci_p0304_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))