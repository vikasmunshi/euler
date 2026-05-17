#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 79: Passcode Derivation [Level 2]. """
from __future__ import annotations

from pathlib import Path
from sys import argv, stderr
from time import perf_counter
from typing import Any


def get_text_file(src: str) -> str:
    """Return the contents of a file from the 'resources' directory."""
    local_filename: str = "resources/" + src.split("/")[-1].split("?")[0]
    return (Path(__file__).parent / local_filename).read_text()


def solve(*, asked_characters: int, file_url: str) -> int:
    char_index: tuple[int, ...] = tuple(range(asked_characters - 1))
    content: str = get_text_file(file_url)
    values: set[str] = set(content.splitlines(keepends=False))
    successor_graph: dict[str, set[str]] = {char: set() for val in values for char in val}
    for val in values:
        for i in char_index:
            successor_graph[val[i]].add(val[i + 1])
    passcode: str = ""
    while successor_graph:
        for char, after in successor_graph.items():
            if not after:
                passcode = char + passcode
                break
        else:
            raise ValueError("No successor found - possible circular dependency in the constraints")
        del successor_graph[char]
        for after in successor_graph.values():
            if char in after:
                after.remove(char)
    return int(passcode)


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
    raise SystemExit(main(asked_characters=int(argv[1]), file_url=str(argv[2])))
