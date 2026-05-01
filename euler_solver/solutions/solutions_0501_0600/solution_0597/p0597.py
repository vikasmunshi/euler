#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 597: Torpids.

Problem Statement:
    The Torpids are rowing races held annually in Oxford, following some curious rules:

    - A division consists of n boats (typically 13), placed in order based on past
      performance.
    - All boats within a division start at 40 metre intervals along the river, in order
      with the highest-placed boat starting furthest upstream.
    - The boats all start rowing simultaneously, upstream, trying to catch the boat in
      front while avoiding being caught by boats behind.
    - Each boat continues rowing until either it reaches the finish line or it catches
      up with ("bumps") a boat in front.
    - The finish line is a distance L metres (the course length, in reality about 1800
      metres) upstream from the starting position of the lowest-placed boat. Because
      of the staggered starting positions, higher-placed boats row a slightly shorter
      course than lower-placed boats.
    - When a "bump" occurs, the "bumping" boat takes no further part in the race. The
      "bumped" boat must continue, however, and may even be "bumped" again by boats
      that started two or more places behind it.
    - After the race, boats are assigned new places within the division, based on the
      bumps that occurred. Specifically, for any boat A that started in a lower place
      than B, then A will be placed higher than B in the new order if and only if one
      of the following occurred:
        1. A bumped B directly
        2. A bumped another boat that went on to bump B
        3. A bumped another boat, that bumped yet another boat, that bumped B
        4. etc

    NOTE: For the purposes of this problem you may disregard the boats' lengths, and
    assume that a bump occurs precisely when the two boats draw level.

    Suppose that, in a particular race, each boat B_j rows at a steady speed v_j = -
    log X_j metres per second, where the X_j are chosen randomly (with uniform
    distribution) between 0 and 1, independently from one another. These speeds are
    relative to the riverbank: you may disregard the flow of the river.

    Let p(n,L) be the probability that the new order is an even permutation of the
    starting order, when there are n boats in the division and L is the course length.

    For example, with n=3 and L=160, labelling the boats as A,B,C in starting order with
    C highest, the different possible outcomes of the race are as follows:

      Bumps occurring       New order       Permutation    Probability
      none                  A, B, C         even           4/15
      B bumps C             A, C, B         odd            8/45
      A bumps B             B, A, C         odd            1/3
      B bumps C, then A bumps C   C, A, B   even           4/27
      A bumps B, then B bumps C   C, B, A   odd            2/27

    Therefore, p(3,160) = 4/15 + 4/27 = 56/135.

    You are also given that p(4,400)=0.5107843137, rounded to 10 digits after the decimal
    point.

    Find p(13,1800) rounded to 10 digits after the decimal point.

URL: https://projecteuler.net/problem=597
"""
from typing import Any

euler_problem: int = 597
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 13, 'L': 1800}, 'answer': None},
    {'category': 'dev', 'input': {'n': 3, 'L': 160}, 'answer': None},
    {'category': 'dev', 'input': {'n': 4, 'L': 400}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
