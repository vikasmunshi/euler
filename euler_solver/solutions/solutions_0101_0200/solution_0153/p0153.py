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

URL: https://projecteuler.net/problem=153
"""
from typing import Any

euler_problem: int = 153
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
