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

Solution Approach:
    Model the race as permutations transformed by a sequence of bumps represented by a
    directed graph of bump relations.
    Calculate the probability distribution of outcomes given independent uniform random
    speeds transformed by -log.
    Use combinatorics and probability theory to find p(n,L), the probability of an even
    permutation outcome.
    Numeric precision and efficient enumeration or analytic combinatorics should be
    employed due to complexity.
    Complexity depends heavily on n and conditioning on random order statistics and race
    constraints.

Answer: ...
URL: https://projecteuler.net/problem=597
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 597
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 13, 'L': 1800}},
    {'category': 'dev', 'input': {'n': 3, 'L': 160}},
    {'category': 'dev', 'input': {'n': 4, 'L': 400}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_torpids_p0597_s0(*, n: int, L: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
