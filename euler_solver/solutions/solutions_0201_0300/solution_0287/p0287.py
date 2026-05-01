#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 287: Quadtree Encoding (a Simple Compression Algorithm).

Problem Statement:
    The quadtree encoding allows us to describe a 2^N x 2^N black and white image
    as a sequence of bits (0 and 1). Those sequences are to be read from left to
    right like this:

    the first bit deals with the complete 2^N x 2^N region;
    "0" denotes a split:
        the current 2^n x 2^n region is divided into 4 sub-regions of size
        2^{n-1} x 2^{n-1}, and the next bits describe the top-left, top-right,
        bottom-left and bottom-right sub-regions in that order;
    "10" indicates that the current region contains only black pixels;
    "11" indicates that the current region contains only white pixels.

    For a 4 x 4 example image several sequences can describe the same image,
    for example "0 0 10101010 0 1011111011 0 10101010" of length 30, or the
    minimal sequence "0 10 0 101111101110" of length 16.

    For a positive integer N, define D_N as the 2^N x 2^N image with the
    following coloring scheme:
        the pixel with coordinates x = 0, y = 0 corresponds to the bottom
        left pixel;
        if (x - 2^{N-1})^2 + (y - 2^{N-1})^2 <= 2^{2N-2} then the pixel is black;
        otherwise the pixel is white.

    What is the length of the minimal sequence describing D_24?

URL: https://projecteuler.net/problem=287
"""
from typing import Any

euler_problem: int = 287
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 24}, 'answer': None},
]
encrypted: str = (
    '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'
    'rWeVeg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
