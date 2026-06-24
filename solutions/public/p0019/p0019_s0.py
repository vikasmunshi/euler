#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 19: Counting Sundays [Level 2]. """
from __future__ import annotations

import datetime

from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    """Linear scan over every first-of-month, counting those that fall on a Sunday via
    datetime.date.isoweekday() (7 == Sunday); O(Y) for a span of Y years."""
    end_year = runner.parse_int(args[0])
    start_year = runner.parse_int(args[1])

    return str(sum(
        (datetime.date(y, m, day=1).isoweekday() == 7 for m in range(1, 13) for y in range(start_year, end_year + 1))
    ))


if __name__ == "__main__":
    raise SystemExit(solve())
