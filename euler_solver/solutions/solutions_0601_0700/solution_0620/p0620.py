#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 620: Planetary Gears.

Problem Statement:
    A circle C of circumference c centimetres has a smaller circle S of circumference s
    centimetres lying off-centre within it. Four other distinct circles, which we call
    "planets", with circumferences p, p, q, q centimetres respectively (p < q), are
    inscribed within C but outside S, with each planet touching both C and S tangentially.
    The planets are permitted to overlap one another, but the boundaries of S and C must
    be at least 1cm apart at their closest point.

    Now suppose that these circles are actually gears with perfectly meshing teeth at a pitch
    of 1cm. C is an internal gear with teeth on the inside. We require that c, s, p, q are
    all integers (as they are the numbers of teeth), and we further stipulate that any gear
    must have at least 5 teeth.

    Note that "perfectly meshing" means that as the gears rotate, the ratio between their
    angular velocities remains constant, and the teeth of one gear perfectly align with the
    grooves of the other gear and vice versa. Only for certain gear sizes and positions will
    it be possible for S and C each to mesh perfectly with all the planets. Arrangements where
    not all gears mesh perfectly are not valid.

    Define g(c,s,p,q) to be the number of such gear arrangements for given values of c, s, p, q:
    it turns out that this is finite as only certain discrete arrangements are possible
    satisfying the above conditions. For example, g(16,5,5,6) = 9.

    Let G(n) = sum over s+p+q ≤ n of g(s+p+q,s,p,q), where the sum only includes cases with
    p < q, p ≥ 5, and s ≥ 5, all integers. You are given that G(16) = 9 and G(20) = 205.

    Find G(500).

URL: https://projecteuler.net/problem=620
"""
from typing import Any

euler_problem: int = 620
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 500}, 'answer': None},
]
encrypted: str = (
    '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'
    'E454N3AD+etRiOsyf9uydQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
