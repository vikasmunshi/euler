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

URL: https://projecteuler.net/problem=236
"""
from typing import Any

euler_problem: int = 236
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
