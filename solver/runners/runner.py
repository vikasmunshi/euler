#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Runner framework for Project Euler solutions with benchmarking and validation."""
from __future__ import annotations

__all__ = ['get_text_file', 'main', 'parse_int', 'parse_list', 'show']

from ast import literal_eval
from functools import wraps
from pathlib import Path
from sys import argv, stderr
from time import perf_counter
from typing import Callable, Protocol


class Solve(Protocol):
    """Protocol for a solver function."""

    def __call__(self, *args: str) -> str: ...


def get_text_file(src: str) -> str:
    """Read a file from the 'resources' directory next to the solution script.

    Resolved from the script's own location (argv[0]) so it works regardless of the
    working directory — `__file__` now points at the runner module, not the solution.
    """
    local_filename: str = 'resources/' + src.split('/')[-1].split('?')[0]
    return (Path(argv[0]).resolve().parent / local_filename).read_text()


show: bool = False  # set in main


def main(solve: Solve) -> Callable[[], int]:
    """Decorator to add benchmarking and validation to a solver function."""

    @wraps(solve)
    def wrapper() -> int:
        """Execute `solve` with benchmarking and validation."""
        global show
        try:
            runs_arg: str = next(arg for arg in argv[1:] if arg.startswith('--runs='))
            runs: int = int(runs_arg.split('=', 1)[1])
            assert runs > 0
        except (AssertionError, StopIteration, ValueError):
            runs = 1
        if '--show' in argv:
            show = True
        args: list[str] = [arg for arg in argv[1:] if not arg.startswith('--')]
        elapsed: list[float] = []
        result: str | None = None
        rc: int = 0
        errors: list[str] = []
        for _ in range(runs):
            _start, _result, _stop = perf_counter(), solve(*args), perf_counter()  # <= timed call
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

    return wrapper


def parse_int(token: str) -> int:
    """Parse an integer supporting power notation and underscores."""
    token = token.strip()
    if '**' in token:
        base, _, exp = token.partition('**')
        return int(int(base) ** int(exp))
    if '_' in token:
        return int(token.replace('_', ''))
    return int(token)


def parse_list(token: str) -> list[int]:
    """Parse a list literal such as '[1, 2, 3]' into a list of ints."""
    result: list[int] = literal_eval(token)
    return result
