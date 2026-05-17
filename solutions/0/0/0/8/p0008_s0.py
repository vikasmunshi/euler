#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 8: Largest Product in a Series [Level 0]. """
from __future__ import annotations

import math
from sys import argv, stderr
from time import perf_counter
from typing import Any

number = ("73167176531330624919225119674426574742355349194934969835203127745063262"
          "39578318016984801869478851843858615607891129494954595017379583319528532"
          "08805511125406987471585238630507156932909632952274430435576689664895044"
          "52445231617318564030987111217223831136222989342338030813533627661428280"
          "64444866452387493035890729629049156044077239071381051585930796086670172"
          "42712188399879790879227492190169972088809377665727333001053367881220235"
          "42180975125454059475224352584907711670556013604839586446706324415722155"
          "39753697817977846174064955149290862569321978468622482839722413756570560"
          "57490261407972968652414535100474821663704844031998900088952434506585412"
          "27588666881164271714799244429282308634656748139191231628245861786645835"
          "91245665294765456828489128831426076900422421902267105562632111110937054"
          "42175069416589604080719840385096245544436298123098787992724428490918884"
          "58015616609791913387549920052406368991256071760605886116467109405077541"
          "00225698315520005593572972571636269561882670428252483600823257530420752"
          "963450")


def solve(*, length: int) -> int:
    return max(
        [
            math.prod((int(d) for d in sequence))
            for sequence in (number[i: i + length] for i in range(len(number) - length + 1))
            if "0" not in sequence
        ]
    )


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
    raise SystemExit(main(length=int(argv[1])))
