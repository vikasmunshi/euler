#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 751: Concatenation Coincidence.

Problem Statement:
    A non-decreasing sequence of integers a_n can be generated from any positive
    real value θ by the following procedure:
        b_1 = θ
        b_n = floor(b_{n-1}) * (b_{n-1} - floor(b_{n-1}) + 1) for all n ≥ 2
        a_n = floor(b_n)
    where floor(·) is the floor function.

    For example, θ = 2.956938891377988... generates the Fibonacci sequence:
    2, 3, 5, 8, 13, 21, 34, 55, 89, ...

    The concatenation of a sequence of positive integers a_n is a real value τ
    constructed by concatenating the elements of the sequence after the decimal
    point, starting at a_1: a_1.a_2a_3a_4...

    For example, the Fibonacci sequence constructed from θ = 2.956938891377988...
    yields the concatenation τ = 2.3581321345589... Clearly, τ ≠ θ for this value
    of θ.

    Find the only value of θ for which the generated sequence starts at a_1 = 2
    and the concatenation of the generated sequence equals the original value:
    τ = θ. Give your answer rounded to 24 places after the decimal point.

Solution Approach:
    Use numerical methods and fixed-point iteration to find θ such that τ = θ,
    leveraging the sequence definition. The problem combines number theory,
    fixed-point calculations, and concatenation properties.
    Precision handling and careful floating-point arithmetic are required.
    Expected complexity depends on convergence speed of iteration.

Answer: ...
URL: https://projecteuler.net/problem=751
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 751
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_concatenation_coincidence_p0751_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))