#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 836: A Bold Proposition.

Problem Statement:
    Let A be an affine plane over a radically integral local field F with residual
    characteristic p.

    We consider an open oriented line section U of A with normalized Haar measure m.

    Define f(m, p) as the maximal possible discriminant of the jacobian associated to
    the orthogonal kernel embedding of U into A.

    Find f(20230401, 57). Give as your answer the concatenation of the first letters
    of each bolded word.

URL: https://projecteuler.net/problem=836
"""
from typing import Any

euler_problem: int = 836
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'m': 20230401, 'p': 57}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
