#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 186: Connectedness of a Network.

Problem Statement:
    Here are the records from a busy telephone system with one million users.
    The telephone number of the caller and the called number in record n are
    Caller(n) = S_{2n-1} and Called(n) = S_{2n} where S_1, S_2, S_3, ... come
    from the "Lagged Fibonacci Generator":

    For 1 ≤ k ≤ 55:
        S_k = [100003 - 200003*k + 300007*k^3] mod 1000000.
    For k ≥ 56:
        S_k = [S_{k-24} + S_{k-55}] mod 1000000.

    If Caller(n) = Called(n) the call is a misdial and the call fails;
    otherwise the call is successful.

    From the start of the records, any pair X and Y are friends if X calls Y
    or Y calls X. Friendship extends by transitive closure (friend of a friend).

    The Prime Minister's phone number is 524287. After how many successful
    calls, not counting misdials, will 99% of the users (including the PM) be
    a friend, or a friend of a friend etc., of the Prime Minister?

Solution Approach:
    Simulate the lagged Fibonacci generator to produce caller/called pairs.
    Maintain connected components with a disjoint-set (union-find) structure,
    using union by size and path compression to track component sizes.
    Increment a counter only for successful calls (caller != called) and
    union the two users. After each union check the PM component size and stop
    when it reaches target_fraction * max_users.

    Key ideas: random-like sequence generation, union-find, online processing.
    Time complexity: O(C * α(N)) where C is calls processed; space O(N).
    Generate S_k on the fly to avoid storing large sequences.

Answer: ...
URL: https://projecteuler.net/problem=186
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 186
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_users': 10, 'pm_number': 7, 'target_fraction': 0.99}},
    {'category': 'main', 'input': {'max_users': 1000000, 'pm_number': 524287, 'target_fraction': 0.99}},
    {'category': 'extra', 'input': {'max_users': 200000, 'pm_number': 524287, 'target_fraction': 0.99}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_connectedness_of_a_network_p0186_s0(*, max_users: int, pm_number: int, target_fraction: float) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))