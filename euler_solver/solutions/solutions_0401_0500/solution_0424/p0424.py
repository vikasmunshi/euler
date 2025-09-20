#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 424: Kakuro.

Problem Statement:
    The above is an example of a cryptic kakuro (also known as cross sums, or even sums
    cross) puzzle, with its final solution on the right. (The common rules of kakuro
    puzzles can be found easily on numerous internet sites. Other related information
    can also be currently found at krazydad.com whose author has provided the puzzle data
    for this challenge.)

    The downloadable text file (kakuro200.txt) contains the description of 200 such
    puzzles, a mix of 5x5 and 6x6 types. The first puzzle in the file is the above
    example which is coded as follows:

    6,X,X,(vCC),(vI),X,X,X,(hH),B,O,(vCA),(vJE),X,(hFE,vD),O,O,O,O,(hA),O,I,
    (hJC,vB),O,O,(hJC),H,O,O,O,X,X,X,(hJE),O,O,X

    The first character is a numerical digit indicating the size of the information grid.
    It would be either a 6 (for a 5x5 kakuro puzzle) or a 7 (for a 6x6 puzzle) followed by
    a comma (,). The extra top line and left column are needed to insert information.

    The content of each cell is then described and followed by a comma, going left to right
    and starting with the top line.
        X = Gray cell, not required to be filled by a digit.
        O = White empty cell to be filled by a digit.
        A = Or any letter from A to J to be replaced by its equivalent digit in the solved puzzle.
        ( ) = Location of the encrypted sums. Horizontal sums are preceded by "h" and vertical
        sums by "v". Followed by one or two uppercase letters depending if the sum is single or
        double digit. When the cell must contain info for both horizontal and vertical sum, the
        first is always horizontal and separated by comma within the same brackets.

    The description of the last cell is followed by a CRLF instead of a comma.

    The required answer to each puzzle is based on the value of each letter necessary to arrive
    at the solution and according to alphabetical order. At least 9 out of the 10 encrypting
    letters are always part of the problem description. When only 9 are given, the missing digit
    is assigned the remaining digit.

    You are given that the sum of the answers for the first 10 puzzles in the file is 64414157580.

    Find the sum of the answers for the 200 puzzles.

URL: https://projecteuler.net/problem=424
"""
from typing import Any

euler_problem: int = 424
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/project/resources/p424_kakuro200.txt'},
     'answer': None},
]
encrypted: str = (
    '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'
    'oBL61+ceWuxr63Iq'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
