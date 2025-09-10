#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 236: Luxury Hampers.

Problem Statement:
    Suppliers 'A' and 'B' provided the following numbers of products for the
    luxury hamper market:
    Beluga Caviar: A=5248, B=640
    Christmas Cake: A=1312, B=1888
    Gammon Joint:   A=2624, B=3776
    Vintage Port:   A=5760, B=3776
    Champagne Truffles: A=3936, B=5664

    Although the suppliers try very hard to ship their goods in perfect
    condition, there is inevitably some spoilage - i.e. products gone bad.

    The suppliers compare their performance using two types of statistic:
        1) The five per-product spoilage rates for each supplier are equal
           to the number of products gone bad divided by the number supplied
           for each of the five products in turn.
        2) The overall spoilage rate for each supplier is equal to the total
           number of products gone bad divided by the total number supplied.

    To their surprise, the suppliers found that each of the five per-product
    spoilage rates was worse (higher) for 'B' than for 'A' by the same factor
    (ratio of spoilage rates), m > 1; and yet, paradoxically, the overall
    spoilage rate was worse for 'A' than for 'B', also by a factor of m.

    There are thirty-five m > 1 for which this surprising result could have
    occurred, the smallest of which is 1476/1475.

    What's the largest possible value of m?
    Give your answer as a fraction reduced to its lowest terms, in the form u/v.

Solution Approach:
    Represent m as a reduced rational u/v and let x_i be the integer number
    of bad items for supplier A for product i. Then b_Bi must equal
    (u * n_Bi * x_i) / (v * n_Ai) and be integral and within bounds.
    Enforce the overall-rate reversal constraint to obtain Diophantine
    conditions on the x_i and on u/v. Use exact rational arithmetic and
    divisibility checks to enumerate feasible u/v. Prune using bounds on
    x_i (0..n_Ai) and divisor structure of n_Ai,n_Bi. Expected runtime is
    modest due to small fixed supply counts; space is O(1).

Answer: ...
URL: https://projecteuler.net/problem=236
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 236
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_luxury_hampers_p0236_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))