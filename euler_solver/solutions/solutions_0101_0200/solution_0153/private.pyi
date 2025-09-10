#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 153: Investigating Gaussian Integers.

Problem Statement:
    As we all know the equation x^2=-1 has no solutions for real x. Introducing the
    imaginary unit i gives solutions x=i and x=-i. More generally complex numbers are
    of the form a+bi, and a+bi and a-bi are complex conjugates.
    A Gaussian Integer is a complex number a+bi with integer a and b. Ordinary integers
    are Gaussian integers with b=0 and are called rational integers here.
    We say a Gaussian integer a+bi is a divisor of a rational integer n if n/(a+bi)
    is also a Gaussian integer. For example 1+2i divides 5 because 5/(1+2i)=1-2i.
    Conjugates occur in pairs: if a+bi divides n then a-bi also divides n.
    For divisors with positive real part we list the divisors and define s(n) as the
    sum of these divisors' real parts and imaginary parts as Gaussian integers.
    For n=1..5 the divisors with positive real part and s(n) are:
        1 -> {1}                          s(1)=1
        2 -> {1, 1+i, 1-i, 2}            s(2)=5
        3 -> {1, 3}                      s(3)=4
        4 -> {1,1+i,1-i,2,2+2i,2-2i,4}   s(4)=13
        5 -> {1,1+2i,1-2i,2+i,2-i,5}     s(5)=12
    Hence sum_{n=1..5} s(n) = 35. It is given that sum_{n=1..10^5} s(n) =
    17924657155.
    What is sum_{n=1..10^8} s(n)?

Solution Approach:
    Use number theory and lattice-point counting: represent rational integers' Gaussian
    divisors by Gaussian integers g=a+bi with positive real part and norm r=a^2+b^2.
    Observe S(N)=sum_{n<=N} s(n) = sum_{a>0,b in Z} a * floor(N/(a^2+b^2)).
    Precompute contributions g(r)=sum of positive real parts a over representations
    r=a^2+b^2, then compute S(N)=sum_{r<=N} g(r) * floor(N/r).
    Compute g(r) efficiently by enumerating a up to sqrt(r) or via multiplicative
    formulas using prime factorization and a sieve. Expected time around O(N log N)
    with optimized enumeration and sieving for N=1e8; memory O(N) if a direct sieve
    is used, or less with segmented methods.

Answer: ...
URL: https://projecteuler.net/problem=153
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 153
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 100000000}},
    {'category': 'extra', 'input': {'max_limit': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_investigating_gaussian_integers_p0153_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))