#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 426: Box-Ball System.

Problem Statement:
    Consider an infinite row of boxes. Some of the boxes contain a ball. For
    example, an initial configuration of 2 consecutive occupied boxes followed
    by 2 empty boxes, 2 occupied boxes, 1 empty box, and 2 occupied boxes can
    be denoted by the sequence (2, 2, 2, 1, 2), in which the number of consecutive
    occupied and empty boxes appear alternately.

    A turn consists of moving each ball exactly once according to the following
    rule: Transfer the leftmost ball which has not been moved to the nearest
    empty box to its right.

    After one turn the sequence (2, 2, 2, 1, 2) becomes (2, 2, 1, 2, 3) as can
    be seen below; note that we begin the new sequence starting at the first
    occupied box.

    A system like this is called a Box-Ball System or BBS for short.

    It can be shown that after a sufficient number of turns, the system evolves
    to a state where the consecutive numbers of occupied boxes is invariant.
    In the example below, the consecutive numbers of occupied boxes evolves to
    [1, 2, 3]; we shall call this the final state.

    We define the sequence {t_i}:
        s_0 = 290797
        s_(k+1) = s_k^2 mod 50515093
        t_k = (s_k mod 64) + 1

    Starting from the initial configuration (t_0, t_1, …, t_10), the final state
    becomes [1, 3, 10, 24, 51, 75].
    Starting from the initial configuration (t_0, t_1, …, t_10 000 000), find the
    final state.
    Give as your answer the sum of the squares of the elements of the final state.
    For example, if the final state is [1, 2, 3] then 14 (= 1^2 + 2^2 + 3^2) is your answer.

URL: https://projecteuler.net/problem=426
"""
from typing import Any

euler_problem: int = 426
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 11}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000001}, 'answer': None},
]
encrypted: str = (
    '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'
    'y47dILXPyyCk5sVsFHO7j2Kx+bkcwmV/'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
