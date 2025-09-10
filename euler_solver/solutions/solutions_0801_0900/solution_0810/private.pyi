#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 810: XOR-Primes.

Problem Statement:
    We use x⊕y for the bitwise XOR of x and y.

    Define the XOR-product of x and y, denoted by x⊗y, similar to a long
    multiplication in base 2, except that the intermediate results are XORed
    instead of the usual integer addition.

    For example, 7⊗3 = 9, or in base 2, 111_2 ⊗ 11_2 = 1001_2:
        111_2
      ⊗  11_2
      -------
        111_2
      ⊕ 111_2
      -------
       1001_2

    An XOR-prime is an integer n greater than 1 that is not an XOR-product of
    two integers greater than 1. The above example shows that 9 is not an
    XOR-prime. Similarly, 5 = 3⊗3 is not an XOR-prime. The first few XOR-primes
    are 2, 3, 7, 11, 13, ... and the 10th XOR-prime is 41.

    Find the 5,000,000th XOR-prime.

Solution Approach:
    Analyze the algebraic structure of XOR-product to characterize XOR-primes.
    Use number theory and bit manipulation properties to identify XOR-primes.
    Efficient sieving or combinatorial methods may be needed for large indexing.
    Expected complexity depends on representation and factorization in XOR-mult.
    Advanced math or fast algorithms necessary for 5 millionth XOR-prime.

Answer: ...
URL: https://projecteuler.net/problem=810
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 810
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 5000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_xor_primes_p0810_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))