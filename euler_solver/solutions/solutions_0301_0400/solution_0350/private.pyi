#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 350: Constraining the Least Greatest and the Greatest Least.

Problem Statement:
    A list of size n is a sequence of n natural numbers. Examples are (2,4,6),
    (2,6,4), (10,6,15,6) and (11).

    The greatest common divisor, or gcd, of a list is the largest natural
    number that divides all entries of the list. Examples: gcd(2,6,4) = 2,
    gcd(10,6,15,6) = 1 and gcd(11) = 11.

    The least common multiple, or lcm, of a list is the smallest natural
    number divisible by each entry of the list. Examples: lcm(2,6,4) = 12,
    lcm(10,6,15,6) = 30 and lcm(11) = 11.

    Let f(G, L, N) be the number of lists of size N with gcd >= G and lcm
    <= L. For example:
    f(10, 100, 1) = 91.
    f(10, 100, 2) = 327.
    f(10, 100, 3) = 1135.
    f(10, 100, 1000) mod 101^4 = 3286053.

    Find f(10^6, 10^12, 10^18) mod 101^4.

Solution Approach:
    Reduce by factoring out the gcd: for each g >= G, write a_i = g * b_i so
    gcd(b) = 1 and lcm(b) <= L / g. Let F(M,N) be the number of lists of
    length N with gcd = 1 and lcm <= M. Then f(G,L,N) = sum_{g=G..L} F(floor(L/g),N).

    Count lists whose lcm divides m by observing each element must divide m:
    there are tau(m)^N such lists, where tau is the divisor function.
    Use Möbius inversion on the gcd condition to obtain
    F(M,N) = sum_{d=1..M} mu(d) * S(floor(M/d)) with S(x)=sum_{k=1..x} tau(k)^N.

    Compute S(x) and the outer sum efficiently by grouping equal floor values,
    using multiplicativity, divisor summatory techniques and memoization.
    Expected approach complexity: roughly sublinear in M (typical x^{2/3}
    or similar) with careful sieving and convolution; compute results mod 101^4.

Answer: ...
URL: https://projecteuler.net/problem=350
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 350
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'G': 10, 'L': 100, 'N': 1}},
    {'category': 'main', 'input': {'G': 1000000, 'L': 1000000000000, 'N': 1000000000000000000}},
    {'category': 'extra', 'input': {'G': 1000, 'L': 1000000, 'N': 1000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_constraining_the_least_greatest_and_the_greatest_least_p0350_s0(*, G: int, L: int, N: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))