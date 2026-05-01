#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 673: Beds and Desks.

Problem Statement:
    At Euler University, each of the n students (numbered from 1 to n) occupies a bed
    in the dormitory and uses a desk in the classroom.

    Some of the beds are in private rooms which a student occupies alone, while the others
    are in double rooms occupied by two students as roommates. Similarly, each desk is
    either a single desk for the sole use of one student, or a twin desk at which two
    students sit together as desk partners.

    We represent the bed and desk sharing arrangements each by a list of pairs of student
    numbers. For example, with n=4, if (2,3) represents the bed pairing and (1,3)(2,4)
    the desk pairing, then students 2 and 3 are roommates while 1 and 4 have single rooms,
    and students 1 and 3 are desk partners, as are students 2 and 4.

    The new chancellor of the university decides to change the organisation of beds and
    desks: a permutation σ of the numbers 1,2,...,n will be chosen, and each student k
    will be given both the bed and the desk formerly occupied by student number σ(k).

    The students agree to this change, under the conditions that:
        1) Any two students currently sharing a room will still be roommates.
        2) Any two students currently sharing a desk will still be desk partners.

    In the example above, there are only two ways to satisfy these conditions: either
    take no action (σ is the identity permutation), or reverse the order of the students.

    With n=6, for the bed pairing (1,2)(3,4)(5,6) and the desk pairing (3,6)(4,5), there are
    8 permutations which satisfy the conditions. One example is the mapping
    (1, 2, 3, 4, 5, 6) → (1, 2, 5, 6, 3, 4).

    With n=36, if we have bed pairing:
    (2,13)(4,30)(5,27)(6,16)(10,18)(12,35)(14,19)(15,20)(17,26)(21,32)(22,33)(24,34)(25,28)
    and desk pairing
    (1,35)(2,22)(3,36)(4,28)(5,25)(7,18)(9,23)(13,19)(14,33)(15,34)(20,24)(26,29)(27,30)
    then among the 36! possible permutations (including the identity permutation), 663552
    of them satisfy the conditions stipulated by the students.

    The downloadable text files beds.txt and desks.txt contain pairings for n=500. Each
    pairing is written on its own line, with the student numbers of the two roommates (or
    desk partners) separated with a comma. For example, the desk pairing in the n=4 example
    above would be represented as:
        1,3
        2,4

    With these pairings, find the number of permutations that satisfy the students'
    conditions. Give your answer modulo 999999937.

URL: https://projecteuler.net/problem=673
"""
from typing import Any

euler_problem: int = 673
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'beds_file': '',
                                  'desks_file': ''},
     'answer': None},
    {'category': 'main', 'input': {'beds_file': 'https://projecteuler.net/resources/documents/0673_beds.txt',
                                   'desks_file': 'https://projecteuler.net/resources/documents/0673_desks.txt'},
     'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
