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

URL: https://projecteuler.net/problem=186
"""
from typing import Any

euler_problem: int = 186
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_users': 10, 'pm_number': 7, 'target_fraction': 0.99}, 'answer': None},
    {'category': 'main', 'input': {'max_users': 1000000, 'pm_number': 524287, 'target_fraction': 0.99}, 'answer': None},
    {'category': 'extra', 'input': {'max_users': 200000, 'pm_number': 524287, 'target_fraction': 0.99}, 'answer': None},
]
encrypted: str = (
    '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'
    'vqO0G7CFTpDaRAbubH3+xtMav34qc7qgr+UHMg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
