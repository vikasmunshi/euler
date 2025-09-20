#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 780: Toriangulations.

Problem Statement:
    For positive real numbers a,b, an a×b torus is a rectangle of width a and
    height b, with left and right sides identified, as well as top and bottom
    sides identified. In other words, when tracing a path on the rectangle,
    reaching an edge results in "wrapping round" to the corresponding point on
    the opposite edge.

    A tiling of a torus is a way to dissect it into equilateral triangles of
    edge length 1. For example, the following three diagrams illustrate
    respectively a 1×√3/2 torus with two triangles, a √3×1 torus with four
    triangles, and an approximately 2.8432×2.1322 torus with fourteen triangles.

    Two tilings of an a×b torus are called equivalent if it is possible to
    obtain one from the other by continuously moving all triangles so that no
    gaps appear and no triangles overlap at any stage during the movement.
    For example, the animation below shows an equivalence between two tilings.

    Let F(n) be the total number of non-equivalent tilings of all possible
    tori with exactly n triangles. For example, F(6)=8, with the eight
    non-equivalent tilings with six triangles listed.

    Let G(N)=∑_{n=1}^N F(n). You are given that G(6)=14, G(100)=8090, and
    G(10^5) ≡ 645124048 (mod 1 000 000 007).

    Find G(10^9). Give your answer modulo 1 000 000 007.

URL: https://projecteuler.net/problem=780
"""
from typing import Any

euler_problem: int = 780
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'N': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'Ego3nw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
