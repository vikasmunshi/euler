#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 345: Matrix Sum.

Problem Statement:
    We define the Matrix Sum of a matrix as the maximum possible sum of matrix
    elements such that none of the selected elements share the same row or
    column.

    For example, the Matrix Sum of the matrix below equals 3315 (= 863 + 383 +
    343 + 959 + 767):

        7  53 183 439 863
      497 383 563  79 973
      287  63 343 169 583
      627 343 773 959 943
      767 473 103 699 303

    Find the Matrix Sum of the following 15x15 matrix:

      7  53 183 439 863 497 383 563  79 973 287  63 343 169 583
    627 343 773 959 943 767 473 103 699 303 957 703 583 639 913
    447 283 463  29  23 487 463 993 119 883 327 493 423 159 743
    217 623   3 399 853 407 103 983  89 463 290 516 212 462 350
    960 376 682 962 300 780 486 502 912 800 250 346 172 812 350
    870 456 192 162 593 473 915  45 989 873 823 965 425 329 803
    973 965 905 919 133 673 665 235 509 613 673 815 165 992 326
    322 148 972 962 286 255 941 541 265 323 925 281 601  95 973
    445 721  11 525 473  65 511 164 138 672  18 428 154 448 848
    414 456 310 312 798 104 566 520 302 248 694 976 430 392 198
    184 829 373 181 631 101 969 613 840 740 778 458 284 760 390
    821 461 843 513  17 901 711 993 293 157 274  94 192 156 574
     34 124   4 878 450 476 712 914 838 669 875 299 823 329 699
    815 559 813 459 522 788 168 586 966 232 308 833 251 631 107
    813 883 451 509 615  77 281 613 459 205 380 274 302  35 805

URL: https://projecteuler.net/problem=345
"""
from typing import Any

euler_problem: int = 345
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
