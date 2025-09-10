#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 717: Summation of a Modular Formula.

Problem Statement:
    For an odd prime p, define f(p) = floor(2^(2^p) / p) modulo 2^p.
    For example, when p=3, floor(2^8 / 3) = 85 ≡ 5 mod 8, so f(3) = 5.

    Further define g(p) = f(p) modulo p. You are given g(31) = 17.

    Now define G(N) to be the summation of g(p) for all odd primes less than N.
    You are given G(100) = 474 and G(10^4) = 2819236.

    Find G(10^7).

Solution Approach:
    Use modular arithmetic and properties of exponents to efficiently compute the
    expressions involving huge powers modulo p and 2^p.
    Employ prime sieving up to N (10^7) for generating primes.
    Combine fast modular exponentiation and floor division properties to extract f(p).
    Optimize summation and memory usage for large N.
    Expected complexity depends on prime generation and modular computations, careful
    optimization needed for feasibility within time and memory limits.

Answer: ...
URL: https://projecteuler.net/problem=717
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 717
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 10000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_summation_of_a_modular_formula_p0717_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))