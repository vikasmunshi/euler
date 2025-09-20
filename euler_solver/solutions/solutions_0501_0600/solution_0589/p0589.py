#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 589: Poohsticks Marathon.

Problem Statement:
    Christopher Robin and Pooh Bear love the game of Poohsticks so much that they
    invented a new version which allows them to play for longer before one of
    them wins and they have to go home for tea. The game starts as normal with both
    dropping a stick simultaneously on the upstream side of a bridge. But rather
    than the game ending when one of the sticks emerges on the downstream side,
    instead they fish their sticks out of the water, and drop them back in again
    on the upstream side. The game only ends when one of the sticks emerges from
    under the bridge ahead of the other one having also 'lapped' the other stick
    - that is, having made one additional journey under the bridge compared to
    the other stick.

    On a particular day when playing this game, the time taken for a stick to travel
    under the bridge varies between a minimum of 30 seconds, and a maximum of 60
    seconds. The time taken to fish a stick out of the water and drop it back in
    again on the other side is 5 seconds. The current under the bridge has the
    unusual property that the sticks' journey time is always an integral number of
    seconds, and it is equally likely to emerge at any of the possible times between
    30 and 60 seconds (inclusive). It turns out that under these circumstances,
    the expected time for playing a single game is 1036.15 seconds (rounded to 2
    decimal places). This time is measured from the point of dropping the sticks
    for the first time, to the point where the winning stick emerges from under
    the bridge having lapped the other.

    The stream flows at different rates each day, but maintains the property that
    the journey time in seconds is equally distributed amongst the integers from
    a minimum, n, to a maximum, m, inclusive. Let the expected time of play in
    seconds be E(m,n). Hence E(60,30)=1036.15...

    Let S(k) = sum from m=2 to k of sum from n=1 to m-1 of E(m,n).

    For example S(5) = 7722.82 rounded to 2 decimal places.

    Find S(100) and give your answer rounded to 2 decimal places.

URL: https://projecteuler.net/problem=589
"""
from typing import Any

euler_problem: int = 589
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 5}, 'answer': None},
    {'category': 'main', 'input': {'k': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    'JDOovp1v4gjABeNv'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
