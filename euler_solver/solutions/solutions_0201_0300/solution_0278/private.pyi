#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 278: Linear Combinations of Semiprimes.

Problem Statement:
    Given the values of integers 1 < a1 < a2 < ... < a_n, consider the linear
    combination q1 a1 + q2 a2 + ... + qn a_n = b, using only integer values q_k
    >= 0.
    Note that for a given set of a_k, it may be that not all values of b are
    possible. For instance, if a1 = 5 and a2 = 7, there are no q1 >= 0 and q2 >= 0
    such that b could be 1, 2, 3, 4, 6, 8, 9, 11, 13, 16, 18 or 23. In fact, 23 is
    the largest impossible value of b for a1 = 5 and a2 = 7. We therefore call
    f(5, 7) = 23. Similarly, it can be shown that f(6, 10, 15) = 29 and
    f(14, 22, 77) = 195.
    Find sum f(p*q, p*r, q*r), where p, q and r are prime numbers and
    p < q < r < 5000.

Solution Approach:
    This is a Frobenius (coin problem) instance for three coin values a1 = p*q,
    a2 = p*r, a3 = q*r. Use number theory and shortest-path on residues modulo
    the smallest coin m = min(a1,a2,a3). For each residue class mod m compute the
    minimal representable value using Dijkstra on a graph of m nodes with edges
    adding coin weights; the Frobenius number is max(min_value[res] - m).
    Sum the Frobenius values over all prime triples p<q<r<max_limit. Expected
    complexity: roughly O(m log m) per triple (m = smallest coin), memory O(m).

Answer: ...
URL: https://projecteuler.net/problem=278
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 278
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 30}},
    {'category': 'main', 'input': {'max_limit': 5000}},
    {'category': 'extra', 'input': {'max_limit': 1000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_linear_combinations_of_semiprimes_p0278_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))