#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 524: First Sort II.

Problem Statement:
    Consider the following algorithm for sorting a list:
        1. Starting from the beginning of the list, check each pair of adjacent elements
           in turn.
        2. If the elements are out of order:
            a. Move the smallest element of the pair at the beginning of the list.
            b. Restart the process from step 1.
        3. If all pairs are in order, stop.

    For example, the list {4 1 3 2} is sorted as follows:
        4 1 3 2 (4 and 1 are out of order so move 1 to the front of the list)
        1 4 3 2 (4 and 3 are out of order so move 3 to the front of the list)
        3 1 4 2 (3 and 1 are out of order so move 1 to the front of the list)
        1 3 4 2 (4 and 2 are out of order so move 2 to the front of the list)
        2 1 3 4 (2 and 1 are out of order so move 1 to the front of the list)
        1 2 3 4 (The list is now sorted)

    Let F(L) be the number of times step 2a is executed to sort list L. For example,
    F({4 1 3 2}) = 5.

    We can list all permutations P of the integers {1, 2, ..., n} in lexicographical order,
    and assign to each permutation an index I_n(P) from 1 to n! corresponding to its position
    in the list.

    Let Q(n, k) = min(I_n(P)) for F(P) = k, the index of the first permutation requiring
    exactly k steps to sort with First Sort. If there is no permutation for which F(P) = k,
    then Q(n, k) is undefined.

    For n = 4 we have:
        P                  I_4(P)    F(P)    Q(4, k)
        {1, 2, 3, 4}       1        0       Q(4, 0) = 1
        {1, 2, 4, 3}       2        4       Q(4, 4) = 2
        {1, 3, 2, 4}       3        2       Q(4, 2) = 3
        {1, 3, 4, 2}       4        2
        {1, 4, 2, 3}       5        6       Q(4, 6) = 5
        {1, 4, 3, 2}       6        4
        {2, 1, 3, 4}       7        1       Q(4, 1) = 7
        {2, 1, 4, 3}       8        5       Q(4, 5) = 8
        {2, 3, 1, 4}       9        1
        {2, 3, 4, 1}       10       1
        {2, 4, 1, 3}       11       5
        {2, 4, 3, 1}       12       3       Q(4, 3) = 12
        {3, 1, 2, 4}       13       3
        {3, 1, 4, 2}       14       3
        {3, 2, 1, 4}       15       2
        {3, 2, 4, 1}       16       2
        {3, 4, 1, 2}       17       3
        {3, 4, 2, 1}       18       2
        {4, 1, 2, 3}       19       7       Q(4, 7) = 19
        {4, 1, 3, 2}       20       5
        {4, 2, 1, 3}       21       6
        {4, 2, 3, 1}       22       4
        {4, 3, 1, 2}       23       4
        {4, 3, 2, 1}       24       3

    Let R(k) = min(Q(n, k)) over all n for which Q(n, k) is defined.

    Find R(12^12).

URL: https://projecteuler.net/problem=524
"""
from typing import Any

euler_problem: int = 524
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'Pl6KrGtOu4+Yet0a6nRbEGh3lN06ZMcL'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
