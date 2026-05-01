#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 664: An Infinite Game.

Problem Statement:
    Peter is playing a solitaire game on an infinite checkerboard, each square of
    which can hold an unlimited number of tokens.

    Each move of the game consists of the following steps:
        1. Choose one token T to move. This may be any token on the board, as long
           as not all of its four adjacent squares are empty.
        2. Select and discard one token D from a square adjacent to that of T.
        3. Move T to any one of its four adjacent squares (even if that square is
           already occupied).

    The board is marked with a line called the dividing line. Initially, every
    square to the left of the dividing line contains a token, and every square to
    the right of the dividing line is empty.

    Peter's goal is to get a token as far as possible to the right in a finite
    number of moves. However, he quickly finds out that, even with his infinite
    supply of tokens, he cannot move a token more than four squares beyond the
    dividing line.

    Peter then considers starting configurations with larger supplies of tokens:
    each square in the dth column to the left of the dividing line starts with d^n
    tokens instead of 1. This is illustrated below for n=1.

    Let F(n) be the maximum number of squares Peter can move a token beyond the
    dividing line. For example, F(0)=4. You are also given that F(1)=6, F(2)=9,
    F(3)=13, F(11)=58 and F(123)=1173.

    Find F(1234567).

URL: https://projecteuler.net/problem=664
"""
from typing import Any

euler_problem: int = 664
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 0}, 'answer': None},
    {'category': 'main', 'input': {'n': 1234567}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'jeUEqw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
