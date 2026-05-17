#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 29: Distinct Powers [Level 1]. """
from __future__ import annotations

from sys import argv, stderr
from time import perf_counter
from typing import Any

import pyprimesieve as pps


def solve(*, a_min: int, a_max: int, b_min: int, b_max: int) -> int:
    if min(a_max, b_max) > 100:
        unique_powers = set()
        for a in range(a_min, a_max + 1):
            prime_factors = pps.factorize(a)
            for b in range(b_min, b_max + 1):
                signature = tuple(((prime, power * b) for prime, power in prime_factors))
                unique_powers.add(signature)
        return len(unique_powers)
    else:
        return len({a**b for a in range(a_min, a_max + 1) for b in range(b_min, b_max + 1)})


def main(**kwargs: Any) -> int:
    """
    Usage: ./file.py <kwarg>... [--runs=1] [--show]
    Output: "<runs> <avg_seconds> <result>"
    """
    try:
        runs_arg: str = next((arg for arg in argv[1:] if arg.startswith("--runs=")))
        runs: int = int(runs_arg.split("=", 1)[1])
        assert runs > 0
    except (AssertionError, StopIteration, ValueError):
        runs = 1
    elapsed: list[float] = []
    result: int | None = None
    rc: int = 0
    errors: list[str] = []
    for _ in range(runs):
        _start, _result, _stop = (perf_counter(), solve(**kwargs), perf_counter())
        elapsed.append(_stop - _start)
        if result is not None and _result != result:
            errors.append(f"Expected consistent result, got {_result} previous result={result}")
        result = _result
    if result is None:
        errors.append("Expected a result, got None")
    average: float = sum(elapsed) / len(elapsed)
    if errors:
        print("\n".join(errors), file=stderr)
        rc = 1
    print(f"{runs} {average} {result}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(a_min=int(argv[1]), a_max=int(argv[2]), b_min=int(argv[3]), b_max=int(argv[4])))
