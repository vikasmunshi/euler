#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 726: Falling Bottles.

Problem Statement:
    Consider a stack of bottles of wine. There are n layers in the stack with the top
    layer containing only one bottle and the bottom layer containing n bottles. For n=4
    the stack looks like the picture shown in the problem.

    The collapsing process happens every time a bottle is taken. A space is created in
    the stack and that space is filled according to the following recursive steps:
        - No bottle touching from above: nothing happens. For example, taking F.
        - One bottle touching from above: that will drop down to fill the space creating
          another space. For example, taking D.
        - Two bottles touching from above: one will drop down to fill the space creating
          another space. For example, taking C.

    This process happens recursively; for example, taking bottle A in the diagram. Its
    place can be filled with either B or C. If it is filled with C then the space that C
    creates can be filled with D or E. So there are 3 different collapsing processes that
    can happen if A is taken, although the final shape is the same.

    Define f(n) to be the number of ways that we can take all the bottles from a stack with
    n layers. Two ways are considered different if at any step we took a different bottle
    or the collapsing process went differently.

    Given f(1) = 1, f(2) = 6 and f(3) = 1008.

    Also define S(n) = sum_{k=1}^n f(k).

    Find S(10^4) modulo 1000000033.

URL: https://projecteuler.net/problem=726
"""
from typing import Any

euler_problem: int = 726
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    '8ZtCNw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
