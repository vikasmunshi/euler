#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 335: Gathering the Beans.

Problem Statement:
    Whenever Peter feels bored, he places some bowls, containing one bean each,
    in a circle. After this, he takes all the beans out of a certain bowl and
    drops them one by one in the bowls going clockwise. He repeats this,
    starting from the bowl he dropped the last bean in, until the initial
    situation appears again.

    For example with 5 bowls he acts as follows. So with 5 bowls it takes
    Peter 15 moves to return to the initial situation.

    Let M(x) represent the number of moves required to return to the initial
    situation, starting with x bowls. Thus, M(5) = 15. It can also be verified
    that M(100) = 10920.

    Find sum_{k=0}^{10^18} M(2^k + 1). Give your answer modulo 7^9.

URL: https://projecteuler.net/problem=335
"""
from typing import Any

euler_problem: int = 335
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_k': 4}, 'answer': None},
    {'category': 'main', 'input': {'max_k': 1000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_k': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
