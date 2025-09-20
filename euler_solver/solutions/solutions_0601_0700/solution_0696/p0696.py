#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 696: Mahjong.

Problem Statement:
    The game of Mahjong is played with tiles belonging to s suits. Each tile also has a
    number in the range 1 to n, and for each suit/number combination there are exactly four
    indistinguishable tiles with that suit and number. (The real Mahjong game also
    contains other bonus tiles, but those will not feature in this problem.)

    A winning hand is a collection of 3t+2 Tiles (where t is a fixed integer) that can be
    arranged as t Triples and one Pair, where:
        • A Triple is either a Chow or a Pung
        • A Chow is three tiles of the same suit and consecutive numbers
        • A Pung is three identical tiles (same suit and same number)
        • A Pair is two identical tiles (same suit and same number)

    For example, here is a winning hand with n=9, s=3, t=4, consisting in this case of two
    Chows, two Pungs, and one Pair.

    Note that sometimes the same collection of tiles can be represented as t Triples and one
    Pair in more than one way. This only counts as one winning hand.

    Let w(n, s, t) be the number of distinct winning hands formed of t Triples and one Pair,
    where there are s suits available and tiles are numbered up to n.

    For example, with a single suit and tiles numbered up to 4, we have w(4, 1, 1) = 20:
    there are 12 winning hands consisting of a Pung and a Pair, and another 8 containing a
    Chow and a Pair. You are also given that w(9, 1, 4) = 13259, w(9, 3, 4) = 5237550,
    and w(1000, 1000, 5) ≡ 107662178 (mod 1,000,000,007).

    Find w(10^8, 10^8, 30). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=696
"""
from typing import Any

euler_problem: int = 696
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4, 's': 1, 't': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000, 's': 100000000, 't': 30}, 'answer': None},
]
encrypted: str = (
    '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'
    'Bw2m3Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
