#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 707: Lights Out.

Problem Statement:
    Consider a w x h grid. A cell is either ON or OFF. When a cell is selected,
    that cell and all cells connected to that cell by an edge are toggled on-off,
    off-on. See the diagram for the 3 cases of selecting a corner cell, an edge
    cell or central cell in a grid that has all cells on (white).

    The goal is to get every cell to be off simultaneously. This is not possible
    for all starting states. A state is solvable if, by a process of selecting
    cells, the goal can be achieved.

    Let F(w,h) be the number of solvable states for a w x h grid. You are given
    F(1,2)=2, F(3,3)=512, F(4,4)=4096 and F(7,11) ≡ 270016253 mod 1,000,000,007.

    Let f_1 = f_2 = 1 and f_n = f_{n-1} + f_{n-2} for n ≥ 3 be the Fibonacci
    sequence and define
        S(w,n) = sum_{k=1}^n F(w, f_k).

    You are given S(3,3) = 32, S(4,5) = 1052960 and S(5,7) ≡ 346547294 mod 1,000,000,007.

    Find S(199,199). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=707
"""
from typing import Any

euler_problem: int = 707
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'w': 199, 'n': 199}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
