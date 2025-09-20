#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 480: The Last Question.

Problem Statement:
    Consider all the words which can be formed by selecting letters, in any order,
    from the phrase:

        thereisasyetinsufficientdataforameaningfulanswer

    Suppose those with 15 letters or less are listed in alphabetical order and numbered
    sequentially starting at 1.
    The list would include:
    1 : a
    2 : aa
    3 : aaa
    4 : aaaa
    5 : aaaaa
    6 : aaaaaa
    7 : aaaaaac
    8 : aaaaaacd
    9 : aaaaaacde
    10 : aaaaaacdee
    11 : aaaaaacdeee
    12 : aaaaaacdeeee
    13 : aaaaaacdeeeee
    14 : aaaaaacdeeeeee
    15 : aaaaaacdeeeeeef
    16 : aaaaaacdeeeeeeg
    17 : aaaaaacdeeeeeeh
    ...
    28 : aaaaaacdeeeeeey
    29 : aaaaaacdeeeeef
    30 : aaaaaacdeeeeefe
    ...
    115246685191495242: euleoywuttttsss
    115246685191495243: euler
    115246685191495244: eulera
    ...
    525069350231428029: ywuuttttssssrrr

    Define P(w) as the position of the word w.
    Define W(p) as the word in position p.
    We can see that P(w) and W(p) are inverses:
    P(W(p)) = p and W(P(w)) = w.

    Examples:
        W(10) = aaaaaacdee
        P(aaaaaacdee) = 10
        W(115246685191495243) = euler
        P(euler) = 115246685191495243

    Find W(P(legionary) + P(calorimeters) - P(annihilate) + P(orchestrated) - P(fluttering)).

    Give your answer using lowercase characters (no punctuation or space).

URL: https://projecteuler.net/problem=480
"""
from typing import Any

euler_problem: int = 480
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
