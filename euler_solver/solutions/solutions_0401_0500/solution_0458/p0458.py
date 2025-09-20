#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 458: Permutations of Project.

Problem Statement:
    Consider the alphabet A made out of the letters of the word "project":
    A = {c, e, j, o, p, r, t}.

    Let T(n) be the number of strings of length n consisting of letters from A
    that do not have a substring that is one of the 5040 permutations of "project".

    T(7) = 7^7 - 7! = 818503.

    Find T(10^12). Give the last 9 digits of your answer.

URL: https://projecteuler.net/problem=458
"""
from typing import Any

euler_problem: int = 458
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 7}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Buni/X8ZMrgtjQEP5uaLkoq9chg='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
