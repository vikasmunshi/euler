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

URL: https://projecteuler.net/problem=191
"""
from typing import Any

euler_problem: int = 191
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'days': 4}, 'answer': None},
    {'category': 'main', 'input': {'days': 30}, 'answer': None},
    {'category': 'extra', 'input': {'days': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    'TkhlbQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
