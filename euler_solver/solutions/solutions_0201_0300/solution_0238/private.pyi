#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 238: Infinite String Tour.

Problem Statement:
    Create a sequence of numbers using the "Blum Blum Shub" pseudo-random
    number generator:
    s_0 = 14025256
    s_{n + 1} = s_n^2 mod 20300713

    Concatenate these numbers s_0 s_1 s_2 ... to create a string w of
    infinite length.
    Then, w = 14025256741014958470038053646...

    For a positive integer k, if no substring of w exists with a sum of
    digits equal to k, p(k) is defined to be zero. If at least one
    substring of w exists with a sum of digits equal to k, we define
    p(k) = z, where z is the starting position of the earliest such
    substring.

    For instance:
    The substrings 1, 14, 1402, ... with respective sums of digits equal
    to 1, 5, 7, ... start at position 1, hence p(1) = p(5) = p(7) = ... = 1.
    The substrings 4, 402, 4025, ... with respective sums equal to 4, 6,
    11, ... start at position 2, hence p(4) = p(6) = p(11) = ... = 2.
    The substrings 02, 0252, ... with respective sums equal to 2, 9, ...
    start at position 3, hence p(2) = p(9) = ... = 3.
    Note that substring 025 starting at position 3 has sum 7, but there was
    an earlier substring (starting at position 1) with sum 7, so p(7) = 1.

    We can verify that, for 0 < k <= 10^3, sum p(k) = 4742.

    Find sum p(k) for 0 < k <= 2*10^15.

Solution Approach:
    Generate the digit stream by concatenating the Blum Blum Shub outputs.
    The RNG sequence modulo 20300713 is ultimately periodic, so the digit
    stream is eventually periodic; extract the finite cycle of digits.
    Use prefix sums of digits so substring sums are differences of prefixes.
    Earliest occurrence for a given k is the minimal start index i with some
    later prefix equal to prefix_{i-1} + k. Frame this as shortest-path on
    a finite automaton of cycle positions and prefix values to find first
    occurrences efficiently.
    Exploit the periodic structure to cover ranges of k analytically and
    aggregate p(k) using arithmetic progression techniques. Aim for time
    roughly polynomial in cycle length and logarithmic/exponential range
    compression in k.

Answer: ...
URL: https://projecteuler.net/problem=238
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 238
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}},
    {'category': 'main', 'input': {'max_limit': 2000000000000000}},
    {'category': 'extra', 'input': {'max_limit': 20000000000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_infinite_string_tour_p0238_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))