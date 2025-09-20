#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 740: Secret Santa.

Problem Statement:
    Secret Santa is a process that allows n people to give each other presents,
    so that each person gives a single present and receives a single present.
    At the beginning each of the n people write their name on a slip of paper
    and put the slip into a hat. Each person takes a random slip from the hat.
    If the slip has their name they draw another random slip from the hat and
    then put the slip with their name back into the hat. At the end everyone buys
    a Christmas present for the person whose name is on the slip they are holding.
    This process will fail if the last person draws their own name.

    In this variation each of the n people gives and receives two presents. At
    the beginning each of the n people writes their name on two slips of paper
    and puts the slips into a hat (there will be 2n slips of paper in the hat).
    As before each person takes from the hat a random slip that does not contain
    their own name. Then the same person repeats this process thus ending up with
    two slips, neither of which contains that person's own name. Then the next
    person draws two slips in the same way, and so on. The process will fail if
    the last person gets at least one slip with their own name.

    Define q(n) to be the probability of this happening. You are given q(3) =
    0.3611111111 and q(5) = 0.2476095994 both rounded to 10 decimal places.

    Find q(100) rounded to 10 decimal places.

URL: https://projecteuler.net/problem=740
"""
from typing import Any

euler_problem: int = 740
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 100}, 'answer': None},
    {'category': 'extra', 'input': {'n': 150}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
