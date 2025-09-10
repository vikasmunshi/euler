#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 111: Primes with Runs.

Problem Statement:
    Considering 4-digit primes containing repeated digits it is clear that they
    cannot all be the same: 1111 is divisible by 11, 2222 is divisible by 22,
    and so on. But there are nine 4-digit primes containing three ones:
    1117, 1151, 1171, 1181, 1511, 1811, 2111, 4111, 8111.

    We shall say that M(n, d) represents the maximum number of repeated digits
    for an n-digit prime where d is the repeated digit, N(n, d) represents the
    number of such primes, and S(n, d) represents the sum of these primes.

    So M(4, 1) = 3 is the maximum number of repeated digits for a 4-digit
    prime where one is the repeated digit, there are N(4, 1) = 9 such primes,
    and the sum of these primes is S(4, 1) = 22275. For d = 0 it is only
    possible to have M(4, 0) = 2, with N(4, 0) = 13 and S(4, 0) = 67061.

    The statement lists M(4,d), N(4,d) and S(4,d) for d = 0..9 and the sum of
    all S(4,d) is 273700.

    Find the sum of all S(10, d) for d = 0,1,...,9.

Solution Approach:
    For each digit d in 0..9, determine M(n,d) by testing candidate repeat
    counts k from n-1 downwards and generating numbers with exactly k digits
    equal to d (choose the other positions and assign digits).

    Enumerate combinations of positions to be non-d (choose n-k positions),
    iterate possible digit assignments (respect leading-zero and last-digit
    constraints), and test primality for each generated number.

    Use combinatoric generation with heavy pruning (skip even/5 endings,
    avoid leading zeros) and a fast deterministic Miller–Rabin for 64-bit
    integers. Complexity is combinatorial (sum C(n,r)*9^r) but pruning makes
    the search practical for n = 10.

Answer:
URL: https://projecteuler.net/problem=111
"""
from __future__ import annotations

from itertools import combinations, product
from typing import Any

from euler_solver.c_libs import use_wrapped_c_function
from euler_solver.c_libs.py_wrappers.primes import fast_is_prime
from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution, show_solution

euler_problem: int = 111
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}},
    {'category': 'main', 'input': {'n': 10}},
    {'category': 'extra', 'input': {'n': 11}}
]


@use_wrapped_c_function('p0111')
def euler111(n: int, print_working: bool) -> int: ...

@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_primes_with_runs_p0111_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
