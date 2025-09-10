#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 191: Prize Strings.

Problem Statement:
    A particular school offers cash rewards to children with good attendance and
    punctuality. If they are absent for three consecutive days or late on more
    than one occasion then they forfeit their prize.

    During an n-day period a trinary string is formed for each child consisting
    of L's (late), O's (on time), and A's (absent).

    Although there are eighty-one trinary strings for a 4-day period that can be
    formed, exactly forty-three strings would lead to a prize:
    OOOO OOOA OOOL OOAO OOAA OOAL OOLO OOLA OAOO OAOA
    OAOL OAAO OAAL OALO OALA OLOO OLOA OLAO OLAA AOOO
    AOOA AOOL AOAO AOAA AOAL AOLO AOLA AAOO AAOA AAOL
    AALO AALA ALOO ALOA ALAO ALAA LOOO LOOA LOAO LOAA
    LAOO LAOA LAAO

    How many "prize" strings exist over a 30-day period?

Solution Approach:
    Dynamic programming and combinatorics. Count strings with no L (only A and O
    with no run of three A's) using a linear recurrence a_n = a_{n-1} + a_{n-2}
    + a_{n-3}. Precompute f[k] for 0..n. Count strings with exactly one L by
    summing f[i-1]*f[n-i] over positions i. Total = f[n] + sum_{i} f[i-1]*f[n-i].
    Time complexity O(n), space O(n) (or O(1) with rolling arrays).

Answer: ...
URL: https://projecteuler.net/problem=191
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 191
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'days': 4}},
    {'category': 'main', 'input': {'days': 30}},
    {'category': 'extra', 'input': {'days': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prize_strings_p0191_s0(*, days: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))