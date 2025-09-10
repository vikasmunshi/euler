#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 298: Selective Amnesia.

Problem Statement:
    Larry and Robin play a memory game involving a sequence of random numbers
    between 1 and 10 inclusive that are called out one at a time. Each player
    can remember up to 5 previous numbers. When the called number is in a
    player's memory, that player is awarded a point. If it's not, the player
    adds the called number to his memory, removing another number if his memory
    is full.

    Both players start with empty memories. Both players always add new missed
    numbers to their memory but use a different strategy in deciding which
    number to remove:
        Larry's strategy is to remove the number that hasn't been called in
        the longest time (remove the least recently used among remembered
        numbers).
        Robin's strategy is to remove the number that's been in the memory
        the longest time (remove the earliest inserted, i.e., FIFO).

    An example game is given in the statement illustrating the two memories
    and their scores over turns.

    Denoting Larry's score by L and Robin's score by R, what is the expected
    value of |L - R| after 50 turns? Give the answer rounded to eight decimal
    places using the format x.xxxxxxxx.

Solution Approach:
    Model the process as a discrete-time Markov chain over the combined state
    of both players' memories and their scores or differences; exploit symmetry
    and the small alphabet (10 numbers) and fixed memory size (5) to reduce
    state space. Use dynamic programming to propagate probabilities turn by
    turn, accumulating the distribution of |L-R|. Numerical aggregation yields
    the expected value. Complexity depends on the number of reachable states;
    optimizations include state canonicalization, marginalization, and
    exploiting identical-number symmetry.

Answer: ...
URL: https://projecteuler.net/problem=298
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 298
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'turns': 10}},
    {'category': 'main', 'input': {'turns': 50}},
    {'category': 'extra', 'input': {'turns': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_selective_amnesia_p0298_s0(*, turns: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))