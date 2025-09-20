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

URL: https://projecteuler.net/problem=298
"""
from typing import Any

euler_problem: int = 298
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'turns': 10}, 'answer': None},
    {'category': 'main', 'input': {'turns': 50}, 'answer': None},
    {'category': 'extra', 'input': {'turns': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    'HCRFjZoslCXnyZ0dNp5ywoXw5ubbNKrEzqMo4Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
