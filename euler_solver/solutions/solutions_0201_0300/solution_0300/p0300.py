#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 300: Protein Folding.

Problem Statement:
    In a very simplified form, we can consider proteins as strings consisting of
    hydrophobic (H) and polar (P) elements, e.g. HHPPHHHPHHPH. For this problem,
    the orientation of a protein is important; e.g. HPP is considered distinct
    from PPH. Thus, there are 2^n distinct proteins consisting of n elements.

    When one encounters these strings in nature, they are always folded in such a
    way that the number of H-H contact points is as large as possible, since this
    is energetically advantageous. As a result, the H-elements tend to
    accumulate in the inner part, with the P-elements on the outside. Natural
    proteins are folded in three dimensions of course, but we will only consider
    protein folding in two dimensions.

    The figure in the original statement shows two possible ways that an example
    protein could be folded (H-H contact points shown). The folding on the left
    has only six H-H contact points and would not occur naturally. The folding
    on the right has nine H-H contact points, which is optimal for that string.

    Assuming that H and P elements are equally likely to occur in any position
    along the string, the average number of H-H contact points in an optimal
    folding of a random protein string of length 8 turns out to be
    850 / 2^8 = 3.3203125.

    What is the average number of H-H contact points in an optimal folding of a
    random protein string of length 15? Give your answer using as many decimal
    places as necessary for an exact result.

URL: https://projecteuler.net/problem=300
"""
from typing import Any

euler_problem: int = 300
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 8}, 'answer': None},
    {'category': 'main', 'input': {'n': 15}, 'answer': None},
    {'category': 'extra', 'input': {'n': 16}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
