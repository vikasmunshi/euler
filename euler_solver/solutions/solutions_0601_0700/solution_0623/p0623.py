#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 623: Lambda Count.

Problem Statement:
    The lambda-calculus is a universal model of computation at the core of
    functional programming languages. It is based on lambda-terms, a minimal
    programming language featuring only function definitions, function calls
    and variables. Lambda-terms are built according to the following rules:

        - Any variable x (single letter, from some infinite alphabet) is a
          lambda-term.
        - If M and N are lambda-terms, then (M N) is a lambda-term, called the
          application of M to N.
        - If x is a variable and M is a term, then (λx. M) is a lambda-term,
          called an abstraction. An abstraction defines an anonymous function,
          taking x as parameter and sending back M.

    A lambda-term T is said to be closed if for all variables x, all occurrences
    of x within T are contained within some abstraction (λx. M) in T. The
    smallest such abstraction is said to bind the occurrence of the variable x.
    In other words, a lambda-term is closed if all its variables are bound to
    parameters of enclosing functions definitions. For example, the term (λx. x)
    is closed, while the term (λx. (x y)) is not because y is not bound.

    Also, we can rename variables as long as no binding abstraction changes.
    This means that (λx. x) and (λy. y) should be considered equivalent since we
    merely renamed a parameter. Two terms equivalent modulo such renaming are
    called α-equivalent. Note that (λx. (λy. (x y))) and (λx. (λx. (x x))) are not
    α-equivalent, since the abstraction binding the first variable was the outer
    one and becomes the inner one. However, (λx. (λy. (x y))) and (λy. (λx.
    (y x))) are α-equivalent.

    The following table regroups the lambda-terms that can be written with at most
    15 symbols, symbols being parenthesis, λ, dot and variables.

        (λx.x)                (λx.(x x))              (λx.(λy.x))          (λx.(λy.y))
        (λx.(x (x x)))        (λx.((x x) x))          (λx.(λy.(x x)))      (λx.(λy.(x y)))
        (λx.(λy.(y x)))       (λx.(λy.(y y)))         (λx.(x (λy.x)))      (λx.(x (λy.y)))
        (λx.((λy.x) x))       (λx.((λy.y) x))         ((λx.x) (λx.x))      (λx.(x (x (x x))))
        (λx.(x ((x x) x)))    (λx.((x x) (x x)))      (λx.((x (x x)) x))   (λx.(((x x) x) x))

    Let be Λ(n) the number of distinct closed lambda-terms that can be written
    using at most n symbols, where terms that are α-equivalent to one another
    should be counted only once. You are given that Λ(6) = 1, Λ(9) = 2,
    Λ(15) = 20 and Λ(35) = 3166438.

    Find Λ(2000). Give the answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=623
"""
from typing import Any

euler_problem: int = 623
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
