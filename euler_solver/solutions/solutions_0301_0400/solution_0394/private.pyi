#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 394: Eating Pie.

Problem Statement:
    Jeff eats a pie in an unusual way.
    The pie is circular. He starts with slicing an initial cut in the pie along
    a radius.
    While there is at least a given fraction F of pie left, he performs the
    following procedure:
    - He makes two slices from the pie centre to any point of what is remaining
      of the pie border, any point on the remaining pie border equally likely.
      This will divide the remaining pie into three pieces.
    - Going counterclockwise from the initial cut, he takes the first two pie
      pieces and eats them.
    When less than a fraction F of pie remains, he does not repeat this
    procedure. Instead, he eats all of the remaining pie.

    For x >= 1, let E(x) be the expected number of times Jeff repeats the
    procedure above with F = 1/x. It can be verified that E(1) = 1,
    E(2) ≈ 1.2676536759, and E(7.5) ≈ 2.1215732071.

    Find E(40) rounded to 10 decimal places behind the decimal point.

Solution Approach:
    Model each operation as partitioning the remaining circumference into three
    random segments; the remaining fraction after a step equals the largest of
    the three Dirichlet(1,1,1) segments. Reduce to products of iid largest-
    segment random variables and compute tail probabilities for the product.
    Work in log-space and compute n-fold convolutions of the log-density using
    FFT or numerical integration to obtain P(product >= 1/x). Sum these tails
    to get E(x). Expect numerical methods with careful error control; target
    time ~ O(N log N) for N-point FFT based convolution.

Answer: ...
URL: https://projecteuler.net/problem=394
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 394
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'x': 1}},
    {'category': 'main', 'input': {'x': 40}},
    {'category': 'extra', 'input': {'x': 7.5}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_eating_pie_p0394_s0(*, x: float) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))