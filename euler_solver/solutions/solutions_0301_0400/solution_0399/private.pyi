#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 399: Squarefree Fibonacci Numbers.

Problem Statement:
    The first 15 Fibonacci numbers are:
    1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610.
    It can be seen that 8 and 144 are not squarefree: 8 is divisible by 4
    and 144 is divisible by 4 and by 9.
    So the first 13 squarefree Fibonacci numbers are:
    1, 1, 2, 3, 5, 13, 21, 34, 55, 89, 233, 377 and 610.

    The 200th squarefree Fibonacci number is:
    971183874599339129547649988289594072811608739584170445.
    The last sixteen digits of this number are: 1608739584170445 and in
    scientific notation this number can be written as 9.7e53.

    Find the 100000000th squarefree Fibonacci number.
    Give as your answer its last sixteen digits followed by a comma followed
    by the number in scientific notation (rounded to one digit after the decimal).
    For the 200th squarefree number the answer would have been:
    1608739584170445,9.7e53

    Note:
    For this problem, assume that for every prime p, the first Fibonacci number
    divisible by p is not divisible by p^2 (this is part of Wall's conjecture).
    This has been verified for primes ≤ 3·10^15, but has not been proven in general.
    If it happens that the conjecture is false, then the accepted answer to this problem
    isn't guaranteed to be the 100000000th squarefree Fibonacci number, rather it
    represents only a lower bound for that number.

Solution Approach:
    Use number theory and properties of Fibonacci numbers related to divisibility
    and squarefree conditions.
    Implement an efficient search or formula-based approach to identify squarefree
    Fibonacci numbers indexed by their order.
    Handle large integer arithmetic and output formatting carefully.
    Computational complexity depends heavily on the approach; advanced optimizations
    and conjecture assumptions help limit the search space.

Answer: ...
URL: https://projecteuler.net/problem=399
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 399
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 13}},
    {'category': 'main', 'input': {'n': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_squarefree_fibonacci_numbers_p0399_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))