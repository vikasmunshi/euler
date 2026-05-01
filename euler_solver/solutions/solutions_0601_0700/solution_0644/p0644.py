#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 644: Squares on the Line.

Problem Statement:
    Sam and Tom are trying a game of (partially) covering a given line segment of
    length L by taking turns in placing unit squares onto the line segment.

    As illustrated below, the squares may be positioned in two different ways,
    either "straight" by placing the midpoints of two opposite sides on the line
    segment, or "diagonal" by placing two opposite corners on the line segment.
    Newly placed squares may touch other squares, but are not allowed to overlap
    any other square laid down before.
    The player who is able to place the last unit square onto the line segment wins.

    With Sam starting each game by placing the first square, they quickly realise
    that Sam can easily win every time by placing the first square in the middle
    of the line segment, making the game boring.

    Therefore they decide to randomise Sam's first move, by first tossing a fair
    coin to determine whether the square will be placed straight or diagonal onto
    the line segment and then choosing the actual position on the line segment
    randomly with all possible positions being equally likely. Sam's gain of the
    game is defined to be 0 if he loses the game and L if he wins. Assuming optimal
    play of both players after Sam's initial move, you can see that Sam's expected
    gain, called e(L), is only dependent on the length of the line segment.

    For example, if L=2, Sam will win with a probability of 1, so e(2) = 2. Choosing
    L=4, the winning probability will be 0.33333333 for the straight case and 0.22654092
    for the diagonal case, leading to e(4) = 1.11974851 (rounded to 8 digits after
    the decimal point each).

    Being interested in the optimal value of L for Sam, let's define f(a,b) to be
    the maximum of e(L) for some L in [a, b].
    You are given f(2,10) = 2.61969775, being reached for L = 7.82842712, and
    f(10,20) = 5.99374121 (rounded to 8 digits each).

    Find f(200,500), rounded to 8 digits after the decimal point.

URL: https://projecteuler.net/problem=644
"""
from typing import Any

euler_problem: int = 644
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'a': 200, 'b': 500}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
