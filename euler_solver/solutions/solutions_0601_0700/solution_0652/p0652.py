#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 652: Distinct Values of a Proto-logarithmic Function.

Problem Statement:
    Consider the values of log_2(8), log_4(64) and log_3(27). All three are equal to 3.

    Generally, the function f(m,n)=log_m(n) over integers m,n >= 2 has the property that
    f(m_1,n_1) = f(m_2,n_2) if
        1. m_1 = a^e, n_1 = a^f, m_2 = b^e, n_2 = b^f for some integers a,b,e,f or
        2. m_1 = a^e, n_1 = b^e, m_2 = a^f, n_2 = b^f for some integers a,b,e,f.

    We call a function g(m,n) over integers m,n >= 2 proto-logarithmic if
        - g(m_1,n_1) = g(m_2,n_2) if any integers a,b,e,f fulfilling 1. or 2. can be found,
        - and g(m_1,n_1) != g(m_2,n_2) if no integers a,b,e,f fulfilling 1. or 2. can be found.

    Let D(N) be the number of distinct values that any proto-logarithmic function g(m,n)
    attains over 2 <= m,n <= N.

    For example, D(5)=13, D(10)=69, D(100)=9607 and D(10000)=99959605.

    Find D(10^18), and give the last 9 digits as answer.

    Note: According to the four exponentials conjecture the function log_m(n) is
    proto-logarithmic. While this conjecture is yet unproven in general, log_m(n) can
    be used to calculate D(N) for small values of N.

URL: https://projecteuler.net/problem=652
"""
from typing import Any

euler_problem: int = 652
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'HArHBsLUpvQqgLyh'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
