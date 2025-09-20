#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 336: Maximix Arrangements.

Problem Statement:
    A train is used to transport four carriages in the order ABCD. However,
    sometimes when the train arrives to collect the carriages they are not in
    the correct order.
    To rearrange the carriages they are all shunted on to a large rotating
    turntable. After the carriages are uncoupled at a specific point the train
    moves off the turntable pulling the carriages still attached with it. The
    remaining carriages are rotated 180 degrees. All of the carriages are then
    rejoined and this process is repeated as often as necessary to minimise
    the number of uses of the turntable.
    Some arrangements, such as ADCB, can be solved by separating between A and
    D, and after DCB is rotated the correct order is achieved.
    Simple Simon always solves the problem by first placing carriage A in its
    correct place, then carriage B, then C, and so on.
    Using four carriages, the worst arrangements for Simon, called maximix
    arrangements, are DACB and DBAC; each requires five rotations (although an
    optimal approach can solve them in three).
    There are 24 maximix arrangements for six carriages; the tenth lexicographic
    maximix arrangement is DFAECB.
    Find the 2011th lexicographic maximix arrangement for eleven carriages.

URL: https://projecteuler.net/problem=336
"""
from typing import Any

euler_problem: int = 336
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'num_carriages': 6, 'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'num_carriages': 11, 'n': 2011}, 'answer': None},
    {'category': 'extra', 'input': {'num_carriages': 8, 'n': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
