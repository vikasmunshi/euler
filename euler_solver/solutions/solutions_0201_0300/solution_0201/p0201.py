#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 201: Subsets with a Unique Sum.

Problem Statement:
    For any set A of numbers, let sum(A) be the sum of the elements of A.
    Consider the set B = {1,3,6,8,10,11}. There are 20 subsets of B
    containing three elements, and their sums are:
    sum({1,3,6}) = 10
    sum({1,3,8}) = 12
    sum({1,3,10}) = 14
    sum({1,3,11}) = 15
    sum({1,6,8}) = 15
    sum({1,6,10}) = 17
    sum({1,6,11}) = 18
    sum({1,8,10}) = 19
    sum({1,8,11}) = 20
    sum({1,10,11}) = 22
    sum({3,6,8}) = 17
    sum({3,6,10}) = 19
    sum({3,6,11}) = 20
    sum({3,8,10}) = 21
    sum({3,8,11}) = 22
    sum({3,10,11}) = 24
    sum({6,8,10}) = 24
    sum({6,8,11}) = 25
    sum({6,10,11}) = 27
    sum({8,10,11}) = 29

    Some of these sums occur more than once, others are unique. For a set A, let
    U(A,k) be the set of unique sums of k-element subsets of A. In the example
    we find U(B,3) = {10,12,14,18,21,25,27,29} and sum(U(B,3)) = 156.

    Now consider the 100-element set S = {1^2, 2^2, ..., 100^2}. S has
    100891344545564193334812497256 50-element subsets.

    Determine the sum of all integers which are the sum of exactly one of the
    50-element subsets of S, i.e. find sum(U(S,50)).

URL: https://projecteuler.net/problem=201
"""
from typing import Any

euler_problem: int = 201
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'size': 6, 'k': 3}, 'answer': None},
    {'category': 'main', 'input': {'size': 100, 'k': 50}, 'answer': None},
    {'category': 'extra', 'input': {'size': 120, 'k': 60}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
