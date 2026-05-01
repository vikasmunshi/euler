#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 698: 123 Numbers.

Problem Statement:
    We define 123-numbers as follows:

        1 is the smallest 123-number.
        When written in base 10 the only digits that can be present are "1", "2"
        and "3" and if present the number of times they each occur is also a
        123-number.

    So 2 is a 123-number, since it consists of one digit "2" and 1 is a 123-number.
    Therefore, 33 is a 123-number as well since it consists of two digits "3" and
    2 is a 123-number.
    On the other hand, 1111 is not a 123-number, since it contains 4 digits "1"
    and 4 is not a 123-number.

    In ascending order, the first 123-numbers are:
    1, 2, 3, 11, 12, 13, 21, 22, 23, 31, 32, 33, 111, 112, 113, 121, 122, 123,
    131, ...

    Let F(n) be the n-th 123-number. For example F(4)=11, F(10)=31, F(40)=1112,
    F(1000)=1223321 and F(6000)=2333333333323.

    Find F(111111111111222333). Give your answer modulo 123123123.

URL: https://projecteuler.net/problem=698
"""
from typing import Any

euler_problem: int = 698
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 111111111111222333}, 'answer': None},
]
encrypted: str = (
    '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'
    'P9TKQbuNuX2JoFVOi+S2kYMi6RUdo2mp0vUKNA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
