#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 922: Young's Game A.

Problem Statement:
    A Young diagram is a finite collection of (equally-sized) squares in a grid-like
    arrangement of rows and columns, such that
        the left-most squares of all rows are aligned vertically;
        the top squares of all columns are aligned horizontally;
        the rows are non-increasing in size as we move top to bottom;
        the columns are non-increasing in size as we move left to right.

    Two players Right and Down play a game on several Young diagrams, all disconnected
    from each other. Initially, a token is placed in the top-left square of each diagram.
    Then they take alternating turns, starting with Right. On Right's turn, Right selects
    a token on one diagram and moves it any number of squares to the right. On Down's
    turn, Down selects a token on one diagram and moves it any number of squares downwards.
    A player unable to make a legal move on their turn loses the game.

    For a,b,k ≥ 1 we define an (a,b,k)-staircase to be the Young diagram where the
    bottom-right frontier consists of k steps of vertical height a and horizontal length b.
    Additionally, define the weight of an (a,b,k)-staircase to be a + b + k.

    Let R(m, w) be the number of ways of choosing m staircases, each having weight not
    exceeding w, upon which Right (moving first in the game) will win the game assuming
    optimal play. Different orderings of the same set of staircases are to be counted
    separately.

    For example, R(2, 4) = 7 is illustrated, and R(3, 9) = 314104.

    Find R(8, 64) giving your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=922
"""
from typing import Any

euler_problem: int = 922
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 2, 'w': 4}, 'answer': None},
    {'category': 'main', 'input': {'m': 8, 'w': 64}, 'answer': None},
    {'category': 'extra', 'input': {'m': 3, 'w': 9}, 'answer': None},
]
encrypted: str = (
    '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'
    'blkfmav64pfcYrVmLGhjlDqPyBemfNJBKphOAg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
