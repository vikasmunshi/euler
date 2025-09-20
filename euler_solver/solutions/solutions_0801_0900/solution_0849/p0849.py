#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 849: The Tournament.

Problem Statement:
    In a tournament there are n teams and each team plays each other team twice.
    A team gets two points for a win, one point for a draw and no points for a loss.

    With two teams there are three possible outcomes for the total points. (4,0) where a
    team wins twice, (3,1) where a team wins and draws, and (2,2) where either there are two
    draws or a team wins one game and loses the other. Here we do not distinguish the teams
    and so (3,1) and (1,3) are considered identical.

    Let F(n) be the total number of possible final outcomes with n teams, so that F(2)=3.
    You are also given F(7)=32923.

    Find F(100). Give your answer modulo 10^9+7.

URL: https://projecteuler.net/problem=849
"""
from typing import Any

euler_problem: int = 849
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 100}, 'answer': None},
    {'category': 'extra', 'input': {'n': 7}, 'answer': None},
]
encrypted: str = (
    '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'
    '3gt7eQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
