#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 497: Drunken Tower of Hanoi.

Problem Statement:
    Bob is very familiar with the famous mathematical puzzle/game, "Tower of Hanoi,"
    which consists of three upright rods and disks of different sizes that can slide
    onto any of the rods. The game begins with a stack of n disks placed on the
    leftmost rod in descending order by size. The objective of the game is to move
    all of the disks from the leftmost rod to the rightmost rod, given the following
    restrictions:

        1. Only one disk can be moved at a time.
        2. A valid move consists of taking the top disk from one stack and placing it
           onto another stack (or an empty rod).
        3. No disk can be placed on top of a smaller disk.

    Moving on to a variant of this game, consider a long room k units (square tiles)
    wide, labeled from 1 to k in ascending order. Three rods are placed at squares a,
    b, and c, and a stack of n disks is placed on the rod at square a.

    Bob begins the game standing at square b. His objective is to play the Tower of
    Hanoi game by moving all of the disks to the rod at square c. However, Bob can
    only pick up or set down a disk if he is on the same square as the rod/stack in
    question.

    Unfortunately, Bob is also drunk. On a given move, Bob will either stumble one
    square to the left or one square to the right with equal probability, unless Bob
    is at either end of the room, in which case he can only move in one direction.
    Despite Bob's inebriated state, he is still capable of following the rules of the
    game itself, as well as choosing when to pick up or put down a disk.

    The following animation depicts a side-view of a sample game for n = 3, k = 7,
    a = 2, b = 4, and c = 6.

    Let E(n, k, a, b, c) be the expected number of squares that Bob travels during a
    single optimally-played game. A game is played optimally if the number of
    disk-pickups is minimized.

    Interestingly enough, the result is always an integer. For example,
    E(2,5,1,3,5) = 60 and E(3,20,4,9,17) = 2358.

    Find the last nine digits of sum_{1 ≤ n ≤ 10000} E(n, 10^n, 3^n, 6^n, 9^n).

URL: https://projecteuler.net/problem=497
"""
from typing import Any

euler_problem: int = 497
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
