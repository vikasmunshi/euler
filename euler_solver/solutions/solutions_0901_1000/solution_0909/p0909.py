#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 909: L-expressions I.

Problem Statement:
    An L-expression is defined as any one of the following:
        a natural number;
        the symbol A;
        the symbol Z;
        the symbol S;
        a pair of L-expressions u, v, which is written as u(v).

    An L-expression can be transformed according to the following rules:
        A(x) -> x + 1 for any natural number x;
        Z(u)(v) -> v for any L-expressions u, v;
        S(u)(v)(w) -> v(u(v)(w)) for any L-expressions u, v, w.

    For example, after applying all possible rules, the L-expression S(Z)(A)(0)
    is transformed to the number 1:
        S(Z)(A)(0) -> A(Z(A)(0)) -> A(0) -> 1.
    Similarly, the L-expression S(S)(S(S))(S(Z))(A)(0) is transformed to the
    number 6 after applying all possible rules.

    Find the result of the L-expression S(S)(S(S))(S(S))(S(Z))(A)(0) after
    applying all possible rules. Give the last nine digits as your answer.

    Note: it can be proved that the L-expression in question can only be
    transformed a finite number of times, and the final result does not depend
    on the order of the transformations.

URL: https://projecteuler.net/problem=909
"""
from typing import Any

euler_problem: int = 909
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
