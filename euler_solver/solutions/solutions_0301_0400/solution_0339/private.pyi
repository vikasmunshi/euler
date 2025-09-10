#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 339: Peredur Fab Efrawg.

Problem Statement:
    "And he came towards a valley, through which ran a river; and the borders
    of the valley were wooded, and on each side of the river were level
    meadows. And on one side of the river he saw a flock of white sheep, and
    on the other a flock of black sheep. And whenever one of the white sheep
    bleated, one of the black sheep would cross over and become white; and when
    one of the black sheep bleated, one of the white sheep would cross over and
    become black."
    (Source: en.wikisource.org)

    Initially each flock consists of n sheep. Each sheep (regardless of colour)
    is equally likely to be the next sheep to bleat. After a sheep has bleated
    and a sheep from the other flock has crossed over, Peredur may remove a
    number of white sheep in order to maximize the expected final number of
    black sheep. Let E(n) be the expected final number of black sheep if
    Peredur uses an optimal strategy.

    You are given that E(5) = 6.871346 rounded to 6 places behind the decimal
    point.
    Find E(10,000) and give your answer rounded to 6 places behind the
    decimal point.

Solution Approach:
    Model the process as a Markov decision problem on states (w, b) for white and
    black counts. Let V(w,b) be the optimal expected final number of black
    sheep. Transitions depend on which sheep bleats next; probabilities are
    proportional to current counts. After a transition, an optimal removal of
    white sheep may be applied (an optimal stopping/removal decision).
    Use dynamic programming / memoization to compute V for all reachable
    states. Exploit symmetry and monotonicity to prune states. Expected time
    O(n^2) time and O(n^2) memory in a straightforward DP; optimize if needed.

Answer: ...
URL: https://projecteuler.net/problem=339
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 339
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}},
    {'category': 'main', 'input': {'n': 10000}},
    {'category': 'extra', 'input': {'n': 20000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_peredur_fab_efrawg_p0339_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))