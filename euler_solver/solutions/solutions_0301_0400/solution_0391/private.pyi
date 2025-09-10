#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 391: Hopping Game.

Problem Statement:
    Let s_k be the number of 1's when writing the numbers from 0 to k in
    binary.

    For example, writing 0 to 5 in binary, we have 0, 1, 10, 11, 100, 101.
    There are seven 1's, so s_5 = 7.

    The sequence S = {s_k : k >= 0} starts {0, 1, 2, 4, 5, 7, 9, 12, ...}.

    A game is played by two players. Before the game starts, a number n is
    chosen. A counter c starts at 0. At each turn, the player chooses a number
    from 1 to n (inclusive) and increases c by that number. The resulting
    value of c must be a member of S. If there are no more valid moves, then
    the player loses.

    For example, with n = 5 and starting with c = 0:
    Player 1 chooses 4, so c becomes 0 + 4 = 4.
    Player 2 chooses 5, so c becomes 4 + 5 = 9.
    Player 1 chooses 3, so c becomes 9 + 3 = 12.
    etc.

    Note that c must always belong to S, and each player can increase c by
    at most n.

    Let M(n) be the highest number that the first player could choose at the
    start to force a win, and M(n) = 0 if there is no such move. For example,
    M(2) = 2, M(7) = 1, and M(20) = 4.

    It can be verified that sum M(n)^3 = 8150 for 1 <= n <= 20.

    Find sum M(n)^3 for 1 <= n <= 1000.

Solution Approach:
    Generate S by computing s_k = total number of 1-bits in binary for all
    k up to a bound sufficient for given max_limit. Use fast bit-counting or
    prefix popcount accumulation to produce S in increasing order.
    Model the game as an impartial normal-play game: positions are values c in
    S, moves add d in [1, n] such that c+d is in S. Compute win/lose status
    for positions (DP/backward computation) up to the reachable maximum.
    For each n, inspect initial moves d in [1,n] with d in S to find the
    largest d that moves to a losing position. Time: dominated by generating
    S and evaluating positions up to needed bound; aim for near-linear work in
    the number of S elements considered per n.

Answer: ...
URL: https://projecteuler.net/problem=391
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 391
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20}},
    {'category': 'main', 'input': {'max_limit': 1000}},
    {'category': 'extra', 'input': {'max_limit': 5000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_hopping_game_p0391_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))