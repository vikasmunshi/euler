#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 700: Eulercoin.

Problem Statement:
    Leonhard Euler was born on 15 April 1707.

    Consider the sequence 1504170715041707 n mod 4503599627370517.

    An element of this sequence is defined to be an Eulercoin if it is strictly
    smaller than all previously found Eulercoins.

    For example, the first term is 1504170715041707 which is the first Eulercoin.
    The second term is 3008341430083414 which is greater than 1504170715041707 so is
    not an Eulercoin.  However, the third term is 8912517754604 which is small enough
    to be a new Eulercoin.

    The sum of the first 2 Eulercoins is therefore 1513083232796311.

    Find the sum of all Eulercoins.

URL: https://projecteuler.net/problem=700
"""
from typing import Any

euler_problem: int = 700
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
