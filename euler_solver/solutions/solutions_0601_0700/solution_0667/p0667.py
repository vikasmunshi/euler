#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 667: Moving Pentagon.

Problem Statement:
    After buying a Gerver Sofa from the Moving Sofa Company, Jack wants to buy a
    matching cocktail table from the same company. Most important for him is
    that the table can be pushed through his L-shaped corridor into the living
    room without having to be lifted from its table legs.
    Unfortunately, the simple square model offered to him is too small for him,
    so he asks for a bigger model.
    He is offered the new pentagonal model illustrated below:

    Note, while the shape and size can be ordered individually, due to the
    production process, all edges of the pentagonal table have to have the same
    length.

    Given optimal form and size, what is the biggest pentagonal cocktail table
    (in terms of area) that Jack can buy that still fits through his unit wide
    L-shaped corridor?
    Give your answer rounded to 10 digits after the decimal point (if Jack had
    choosen the square model instead the answer would have been 1.0000000000).

URL: https://projecteuler.net/problem=667
"""
from typing import Any

euler_problem: int = 667
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
