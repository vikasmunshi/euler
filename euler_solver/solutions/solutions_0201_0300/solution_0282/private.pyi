#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 282: The Ackermann Function.

Problem Statement:
    For non-negative integers m, n, the Ackermann function A(m,n) is
    defined as follows:

    A(m,n) =
        n+1                              if m = 0
        A(m-1,1)                         if m > 0 and n = 0
        A(m-1, A(m,n-1))                 if m > 0 and n > 0

    For example A(1,0) = 2, A(2,2) = 7 and A(3,4) = 125.

    Find sum_{n=0}^6 A(n,n) and give your answer mod 14^8.

Solution Approach:
    Use known closed forms: A(0,n)=n+1, A(1,n)=n+2, A(2,n)=2n+3, A(3,n)=2^(n+3)-3,
    and for m>=4 A grows as iterated exponentiation (tetration) minus 3.
    Compute A(n,n) mod M with M = 14^8 by splitting M = 2^8 * 7^8 and using CRT.
    For the 7^8 part use Euler's phi to reduce large exponents (mod phi) and add
    phi when needed to preserve exponent magnitude. Handle 2-power modulus using
    exact 2-adic behavior of powers of 2. The computation is constant-sized
    (n up to 6) with modular exponentiation and CRT, so time is negligible.

Answer: ...
URL: https://projecteuler.net/problem=282
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 282
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 2, 'modulo': 1475789056}},
    {'category': 'main', 'input': {'max_n': 6, 'modulo': 1475789056}},
    {'category': 'extra', 'input': {'max_n': 7, 'modulo': 1475789056}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_the_ackermann_function_p0282_s0(*, max_n: int, modulo: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))