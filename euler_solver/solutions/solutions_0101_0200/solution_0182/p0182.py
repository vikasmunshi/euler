#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 182: RSA Encryption.

Problem Statement:
    The RSA encryption is based on the following procedure:
    Generate two distinct primes p and q.
    Compute n = pq and phi = (p - 1)(q - 1).
    Find an integer e, 1 < e < phi, such that gcd(e, phi) = 1.

    A message in this system is a number in the interval [0, n - 1].
    A text to be encrypted is then converted to messages (numbers in [0, n - 1]).
    To encrypt, for each message m, compute c = m^e mod n.

    To decrypt, calculate d such that ed = 1 mod phi, then m = c^d mod n.

    There exist values of e and m such that m^e mod n = m.
    Messages m for which m^e mod n = m are called unconcealed messages.

    An issue when choosing e is that there should not be too many
    unconcealed messages. For example, let p = 19 and q = 37, then
    n = 19 * 37 = 703 and phi = 18 * 36 = 648. If we choose e = 181,
    although gcd(181, 648) = 1, it turns out that all possible messages
    m (0 <= m <= n - 1) are unconcealed. For any valid choice of e there
    are some unconcealed messages; it is important that their number is
    as small as possible.

    Choose p = 1009 and q = 3643.
    Find the sum of all values of e, 1 < e < phi(1009,3643) with
    gcd(e, phi) = 1, such that the number of unconcealed messages for
    this e is minimal.

URL: https://projecteuler.net/problem=182
"""
from typing import Any

euler_problem: int = 182
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'p': 19, 'q': 37}, 'answer': None},
    {'category': 'main', 'input': {'p': 1009, 'q': 3643}, 'answer': None},
    {'category': 'extra', 'input': {'p': 10007, 'q': 10009}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
