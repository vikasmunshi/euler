#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 679: Freefarea.

Problem Statement:
    Let S be the set consisting of the four letters {`A`,`E`,`F`,`R`}.
    For n≥0, let S*(n) denote the set of words of length n consisting of
    letters belonging to S.
    We designate the words FREE, FARE, AREA, REEF as keywords.

    Let f(n) be the number of words in S*(n) that contains all four keywords
    exactly once.

    This first happens for n=9, and indeed there is a unique 9 lettered word
    that contain each of the keywords once: FREEFAREA
    So, f(9)=1.

    You are also given that f(15)=72863.

    Find f(30).

URL: https://projecteuler.net/problem=679
"""
from typing import Any

euler_problem: int = 679
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 9}, 'answer': None},
    {'category': 'main', 'input': {'n': 30}, 'answer': None},
]
encrypted: str = (
    '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'
    'yaX0DAMrwwIzk3y4NCIC6g61VBo='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
