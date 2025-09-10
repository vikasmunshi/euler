#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 361: Subsequence of Thue-Morse Sequence.

Problem Statement:
    The Thue-Morse sequence {T_n} is a binary sequence satisfying:
    T_0 = 0
    T_{2n} = T_n
    T_{2n + 1} = 1 - T_n

    The first several terms of {T_n} begin:
    01101001100101101001011001101001...

    Define {A_n} as the sorted sequence of integers whose binary
    representation appears as a contiguous subsequence in {T_n}.
    For example, 18 is 10010 in binary and 10010 appears in {T_n}
    (T_8 to T_12), so 18 is in {A_n}. 14 is 1110 which never appears
    in {T_n}, so 14 is not in {A_n}.

    The first terms of {A_n} are:
    A_0 = 0, A_1 = 1, A_2 = 2, A_3 = 3, A_4 = 4, A_5 = 5, A_6 = 6,
    A_7 = 9, A_8 = 10, A_9 = 11, A_10 = 12, A_11 = 13, A_12 = 18, ...

    It is known that A_100 = 3251 and A_1000 = 80852364498.

    Find the last 9 digits of sum_{k = 1}^{18} A_{10^k}.

Solution Approach:
    Model subsequence-occurrence in Thue-Morse using automata/finite-state
    transitions derived from the doubling rules. Count which binary strings
    occur as substrings via dynamic programming over the automaton states.
    Use combinatorics and recurrence relations to jump to very large indices
    (A_{10^k}) with matrix exponentiation or fast doubling of transition
    counts. Expected complexity: poly(log N) matrix exponentiation over
    a small state space; memory O(1) aside from matrices.

Answer: ...
URL: https://projecteuler.net/problem=361
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 361
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k_max': 2}},
    {'category': 'main', 'input': {'k_max': 18}},
    {'category': 'extra', 'input': {'k_max': 20}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_subsequence_of_thue_morse_sequence_p0361_s0(*, k_max: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))