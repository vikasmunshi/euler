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

URL: https://projecteuler.net/problem=911
"""
from typing import Any

euler_problem: int = 911
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
