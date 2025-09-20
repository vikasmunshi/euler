#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 151: A Preference for A5.

Problem Statement:
    A printing shop runs 16 batches (jobs) every week and each batch requires a
    sheet of special colour-proofing paper of size A5.

    Every Monday morning, the supervisor opens a new envelope containing a
    single large sheet of the special paper of size A1.

    The supervisor cuts it in half to get two A2 sheets. Then one sheet is cut
    in half to get two A3 sheets, and so on until an A5 sheet is obtained for
    the first batch of the week. All unused sheets are placed back in the
    envelope.

    At the beginning of each subsequent batch the supervisor takes one sheet at
    random from the envelope. If it is A5 it is used. If it is larger, the
    cut-in-half procedure is repeated until an A5 sheet is produced; any
    remaining sheets are returned to the envelope.

    Excluding the first and last batch of the week, find the expected number of
    times (during each week) that the supervisor finds exactly one sheet of
    paper in the envelope.

    Give the answer rounded to six decimal places using the format x.xxxxxx.

URL: https://projecteuler.net/problem=151
"""
from typing import Any

euler_problem: int = 151
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
