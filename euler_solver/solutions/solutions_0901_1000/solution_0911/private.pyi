#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 911: Khinchin Exceptions.

Problem Statement:
    An irrational number x can be uniquely expressed as a continued fraction
    [a0; a1, a2, a3, ...]:
        x = a0 + 1/(a1 + 1/(a2 + 1/(a3 + ...))),
    where a0 is an integer and a1, a2, a3, ... are positive integers.

    Define kj(x) to be the geometric mean of a1, a2, ..., aj.
    That is, kj(x) = (a1 * a2 * ... * aj)^(1/j).
    Also define k∞(x) = lim_{j → ∞} kj(x).

    Khinchin proved that almost all irrational numbers x have the same value
    of k∞(x) ≈ 2.685452..., known as Khinchin's constant.
    However, there are exceptions to this rule.

    For n ≥ 0 define
        ρn = ∑_{i=0}^{∞} (2^n) / (2^{2^i})

    For example ρ2, with continued fraction beginning [3; 3, 1, 3, 4, 3, 1, 3, ...],
    has k∞(ρ2) ≈ 2.059767.

    Find the geometric mean of k∞(ρn) for 0 ≤ n ≤ 50, giving your answer
    rounded to six digits after the decimal point.

Solution Approach:
    Calculate the continued fraction representation of ρn for each n efficiently.
    Compute the geometric mean limit k∞(ρn) from the terms.
    Then compute the geometric mean of these k∞ values for all n in [0,50].
    Numerical methods and number theory about continued fractions are involved.
    Time complexity depends on precision required for continued fraction expansions.

Answer: ...
URL: https://projecteuler.net/problem=911
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 911
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_khinchin_exceptions_p0911_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))