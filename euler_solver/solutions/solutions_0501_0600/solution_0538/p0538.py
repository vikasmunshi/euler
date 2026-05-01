#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 538: Maximum Quadrilaterals.

Problem Statement:
    Consider a positive integer sequence S = (s_1, s_2, ..., s_n).

    Let f(S) be the perimeter of the maximum-area quadrilateral whose side lengths
    are 4 elements (s_i, s_j, s_k, s_l) of S (all i, j, k, l distinct). If there are
    many quadrilaterals with the same maximum area, then choose the one with the
    largest perimeter.

    For example, if S = (8, 9, 14, 9, 27), then we can take the elements (9, 14, 9, 27)
    and form an isosceles trapezium with parallel side lengths 14 and 27 and both
    leg lengths 9. The area of this quadrilateral is 127.611470879... It can be shown
    that this is the largest area for any quadrilateral that can be formed using side
    lengths from S. Therefore, f(S) = 9 + 14 + 9 + 27 = 59.

    Let u_n = 2^{B(3n)} + 3^{B(2n)} + B(n + 1), where B(k) is the number of 1 bits
    of k in base 2. For example, B(6) = 2, B(10) = 2 and B(15) = 4, and u_5 = 2^4 + 3^2 + 2 = 27.

    Also, let U_n be the sequence (u_1, u_2, ..., u_n). For example, U_10 = (8, 9, 14, 9, 27, 16, 36, 9, 27, 28).

    It can be shown that f(U_5) = 59, f(U_{10}) = 118, f(U_{150}) = 3223.
    It can also be shown that sum f(U_n) = 234761 for 4 ≤ n ≤ 150.

    Find sum f(U_n) for 4 ≤ n ≤ 3,000,000.

URL: https://projecteuler.net/problem=538
"""
from typing import Any

euler_problem: int = 538
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 3000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'hwAa8IPG6OWOkdkS5JQbsARSOyLsDDoA'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
