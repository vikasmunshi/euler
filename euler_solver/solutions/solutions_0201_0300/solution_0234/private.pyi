#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 234: Semidivisible Numbers.

Problem Statement:
    For an integer n >= 4, define the lower prime square root lps(n) as the largest
    prime <= sqrt(n), and the upper prime square root ups(n) as the smallest prime
    >= sqrt(n).

    Examples: lps(4) = 2 = ups(4). lps(1000) = 31, ups(1000) = 37.
    Call an integer n >= 4 semidivisible if one of lps(n) and ups(n) divides n,
    but not both.

    The sum of the semidivisible numbers not exceeding 15 is 30 (the numbers are
    8, 10 and 12). 15 is not semidivisible because it is a multiple of both
    lps(15) = 3 and ups(15) = 5. As a further example the sum of the 92
    semidivisible numbers up to 1000 is 34825.

    What is the sum of all semidivisible numbers not exceeding 999966663333?

Solution Approach:
    Iterate consecutive primes p < q where q is the next prime after p. For n with
    sqrt(n) in (p, q) we have lps(n)=p and ups(n)=q, so n lies in (p^2, q^2).
    In that interval semidivisible n are multiples of p but not q, plus multiples
    of q but not p. Since p and q are primes, lcm(p,q)=p*q.

    For each prime pair intersect the interval with [4, max_limit] and compute
    counts and sums of relevant multiples via arithmetic progression formulas:
    use floor(max / p) etc and sum(k) = m*(m+1)/2. Precompute primes up to
    ceil(sqrt(max_limit)) with a sieve.

    Complexity: sieve up to sqrt(max_limit) in O(M log log M) time and O(M) space,
    then O(pi(M)) intervals processed in constant time each; practical for the
    given limit (~1e6).

Answer: ...
URL: https://projecteuler.net/problem=234
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 234
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 15}},
    {'category': 'main', 'input': {'max_limit': 999966663333}},
    {'category': 'extra', 'input': {'max_limit': 1000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_semidivisible_numbers_p0234_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))