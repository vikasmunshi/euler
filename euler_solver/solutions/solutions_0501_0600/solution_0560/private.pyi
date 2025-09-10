#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 560: Coprime Nim.

Problem Statement:
    Coprime Nim is just like ordinary normal play Nim, but the players may only
    remove a number of stones from a pile that is coprime with the current size
    of the pile. Two players remove stones in turn. The player who removes the
    last stone wins.

    Let L(n, k) be the number of losing starting positions for the first player,
    assuming perfect play, when the game is played with k piles, each having
    between 1 and n - 1 stones inclusively.

    For example, L(5, 2) = 6 since the losing initial positions are (1, 1),
    (2, 2), (2, 4), (3, 3), (4, 2) and (4, 4).
    You are also given L(10, 5) = 9964, L(10, 10) = 472400303,
    L(10^3, 10^3) mod 1,000,000,007 = 954021836.

    Find L(10^7, 10^7) mod 1,000,000,007.

Solution Approach:
    Problems of Nim with move restrictions often involve combinatorial game theory
    and number theory, especially gcd and coprimality properties. Efficiently
    enumerating losing positions involves analyzing pile configurations and
    exploiting symmetries or closed-form formulas. Modulo arithmetic is used for
    large results. Expected complexity requires mathematical insights rather than
    brute force.

Answer: ...
URL: https://projecteuler.net/problem=560
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 560
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'k': 2}},
    {'category': 'main', 'input': {'n': 10000000, 'k': 10000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_coprime_nim_p0560_s0(*, n: int, k: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))