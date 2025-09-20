#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 910: L-expressions II.

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

    For example, after applying all possible rules, the L-expression S(Z)(A)(0) is
    transformed to the number 1:
    S(Z)(A)(0) -> A(Z(A)(0)) -> A(0) -> 1.
    Similarly, the L-expression S(S)(S(S))(S(Z))(A)(0) is transformed to the number 6
    after applying all possible rules.

    Define the following L-expressions:
        C_0 = Z;
        C_i = S(C_{i - 1}) for i ≥ 1;
        D_i = C_i(S)(S).

    For natural numbers a, b, c, d, e, let F(a, b, c, d, e) denote the result of the
    L-expression D_a(D_b)(D_c)(C_d)(A)(e) after applying all possible rules.

    Find the last nine digits of F(12, 345678, 9012345, 678, 90).

URL: https://projecteuler.net/problem=910
"""
from typing import Any

euler_problem: int = 910
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'a': 12, 'b': 345678, 'c': 9012345, 'd': 678, 'e': 90}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
