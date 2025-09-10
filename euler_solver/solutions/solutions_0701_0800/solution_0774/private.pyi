#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 774: Conjunctive Sequences.

Problem Statement:
    Let '&' denote the bitwise AND operation.
    For example, 10 & 12 = 1010_2 & 1100_2 = 1000_2 = 8.

    We shall call a finite sequence of non-negative integers (a_1, a_2, ..., a_n)
    conjunctive if a_i & a_{i+1} ≠ 0 for all i = 1 ... n-1.

    Define c(n,b) to be the number of conjunctive sequences of length n in which
    all terms are ≤ b.

    You are given that c(3,4) = 18, c(10,6) = 2496120, and c(100,200) ≡ 268159379
    (mod 998244353).

    Find c(123,123456789). Give your answer modulo 998244353.

Solution Approach:
    Use dynamic programming with bitwise adjacency graph representing allowed
    transitions between numbers. Represent states to track sequences maintaining
    the conjunctive condition. Employ fast matrix exponentiation for large n.
    Modular arithmetic is applied with modulo 998244353. Time complexity depends
    on optimization and representation of states due to large input size.

Answer: ...
URL: https://projecteuler.net/problem=774
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 774
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 123, 'b': 123456789}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_conjunctive_sequences_p0774_s0(*, n: int, b: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))