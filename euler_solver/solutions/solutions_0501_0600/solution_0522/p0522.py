#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 522: Hilbert's Blackout.

Problem Statement:
    Despite the popularity of Hilbert's infinite hotel, Hilbert decided to try
    managing extremely large finite hotels, instead.

    To cut costs, Hilbert wished to power the new hotel with his own special
    generator. Each floor would send power to the floor above it, with the top
    floor sending power back down to the bottom floor. That way, Hilbert could
    have the generator placed on any given floor (as he likes having the option)
    and have electricity flow freely throughout the entire hotel.

    Unfortunately, the contractors misinterpreted the schematics when they built
    the hotel. They informed Hilbert that each floor sends power to another floor
    at random, instead. This may compromise Hilbert's freedom to have the
    generator placed anywhere, since blackouts could occur on certain floors.

    For example, consider a sample flow diagram for a three-story hotel:

    If the generator were placed on the first floor, then every floor would receive
    power. But if it were placed on the second or third floors instead, then there
    would be a blackout on the first floor. Note that while a given floor can
    receive power from many other floors at once, it can only send power to one
    other floor.

    To resolve the blackout concerns, Hilbert decided to have a minimal number of
    floors rewired. To rewire a floor is to change the floor it sends power to.
    In the sample diagram above, all possible blackouts can be avoided by rewiring
    the second floor to send power to the first floor instead of the third floor.

    Let F(n) be the sum of the minimum number of floor rewirings needed over all
    possible power-flow arrangements in a hotel of n floors. For example,
    F(3) = 6, F(8) = 16276736, and F(100) mod 135707531 = 84326147.

    Find F(12344321) mod 135707531.

URL: https://projecteuler.net/problem=522
"""
from typing import Any

euler_problem: int = 522
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 12344321}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
