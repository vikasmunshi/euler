#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 728: Circle of Coins.

Problem Statement:
    Consider n coins arranged in a circle where each coin shows heads or tails.
    A move consists of turning over k consecutive coins: tail-head or head-tail.
    Using a sequence of these moves the objective is to get all the coins showing heads.

    Consider the example, shown below, where n=8 and k=3 and the initial state is
    one coin showing tails (black). The example shows a solution for this state.

    For given values of n and k not all states are solvable. Let F(n,k) be the number
    of states that are solvable. You are given that F(3,2) = 4, F(8,3) = 256 and F(9,3) = 128.

    Further define:
    S(N) = sum from n=1 to N of sum from k=1 to n of F(n,k).

    You are also given that S(3) = 22, S(10) = 10444 and S(10^3) ≡ 853837042 mod 1000000007.

    Find S(10^7). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=728
"""
from typing import Any

euler_problem: int = 728
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'N': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '/PQwH/kirgK3Fnkf'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
