#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 890: Binary Partitions.

Problem Statement:
    Let p(n) be the number of ways to write n as the sum of powers of two,
    ignoring order.

    For example, p(7) = 6, the partitions being
    7 = 1+1+1+1+1+1+1
      = 1+1+1+1+1+2
      = 1+1+1+2+2
      = 1+1+1+4
      = 1+2+2+2
      = 1+2+4

    You are also given p(7^7) ≡ 144548435 (mod 10^9+7).

    Find p(7^777). Give your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=890
"""
from typing import Any

euler_problem: int = 890
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 7}, 'answer': None},
    {'category': 'main', 'input': {'n': int('4377005487342027007648957702663483480928329142496747911'
                                            '4066505362692934753420235110602019415544351383945632572'
                                            '1913630105201068498522094093221194452990640962260851974'
                                            '1568795920632274798010279373901736184583182920604623125'
                                            '6190487292140499634791490322037157912090429054730677444'
                                            '9767219823345201862426316157793360495888933222475962390'
                                            '3465739651203358480479040968345778739300301961544687426'
                                            '4059419285701992800569100129441185500879045149391793826'
                                            '99179672281299132429971159599347945881994095109675757801'
                                            '70388844996513211079070059269245208385656837790466645171'
                                            '16467890961587963057032054199729737850753958691938898801'
                                            '9437117684585097884685751563283203545236625979207')},
     'answer': None},
]
encrypted: str = (
    '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'
    'swuo5nPWU8+cojf7aA0ZlzvA3NUbs8nyZc96Tw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
