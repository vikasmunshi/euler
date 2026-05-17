#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler $problem. """
from __future__ import annotations

from pathlib import Path
from sys import argv, stderr
from time import perf_counter
from typing import Any


def get_text_file(src: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = 'resources/' + src.split('/')[-1].split('?')[0]
    return (Path(__file__).parent / local_filename).read_text()


def solve(*, kwarg: int) -> int:
    raise NotImplementedError('implement solve() first')


def main(**kwargs: Any) -> int:
    """
    Usage: ./file.py <kwarg>... [--runs=1] [--show]
    Output: "<runs> <avg_seconds> <result>"
    """
    try:
        runs_arg: str = next(arg for arg in argv[1:] if arg.startswith('--runs='))
        runs: int = int(runs_arg.split('=', 1)[1])
        assert runs > 0
    except (AssertionError, StopIteration, ValueError):
        runs = 1
    elapsed: list[float] = []
    result: int | None = None
    rc: int = 0
    errors: list[str] = []
    for _ in range(runs):
        _start, _result, _stop = perf_counter(), solve(**kwargs), perf_counter()  # <= timed call
        elapsed.append(_stop - _start)
        if result is not None and _result != result:
            errors.append(f"Expected consistent result, got {_result} previous result={result}")
        result = _result
    if result is None:
        errors.append("Expected a result, got None")
    average: float = sum(elapsed) / len(elapsed)
    if errors:
        print('\n'.join(errors), file=stderr)
        rc = 1
    print(f'{runs} {average} {result}')
    return rc


if __name__ == "__main__":
    raise SystemExit(main(kwarg=int(argv[1])))
