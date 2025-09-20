#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 105: Special Subset Sums: Testing.

Problem Statement:
    Let S(A) represent the sum of elements in set A of size n. We shall call it a special
    sum set if for any two non-empty disjoint subsets, B and C, the following properties
    are true:

        1. S(B) != S(C); that is, sums of subsets cannot be equal.
        2. If B contains more elements than C then S(B) > S(C).

    For example, {81, 88, 75, 42, 87, 84, 86, 65} is not a special sum set because
    65 + 87 + 88 = 75 + 81 + 84, whereas {157, 150, 164, 119, 79, 159, 161, 139, 158}
    satisfies both rules for all possible subset pair combinations and S(A) = 1286.

    Using sets.txt (right click and "Save Link/Target As..."), a 4K text file with one-
    hundred sets containing seven to twelve elements (the two examples given above are
    the first two sets in the file), identify all the special sum sets, A_1, A_2, ..., A_k,
    and find the value of S(A_1) + S(A_2) + ... + S(A_k).

URL: https://projecteuler.net/problem=105
"""
from typing import Any

euler_problem: int = 105
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0105_sets.txt'},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
