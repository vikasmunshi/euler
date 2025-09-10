#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 327: Rooms of Doom.

Problem Statement:
    A series of three rooms are connected to each other by automatic doors.
    Each door is operated by a security card. Once you enter a room the door
    automatically closes and that security card cannot be used again. A
    machine at the start will dispense an unlimited number of cards, but each
    room (including the starting room) contains scanners and if they detect
    that you are holding more than three security cards or if they detect an
    unattended security card on the floor, then all the doors will become
    permanently locked. However, each room contains a box where you may safely
    store any number of security cards for use at a later stage.
    If you simply tried to travel through the rooms one at a time then as you
    entered room 3 you would have used all three cards and would be trapped
    in that room forever!
    However, if you make use of the storage boxes, then escape is possible.
    For example, you could enter room 1 using your first card, place one card
    in the storage box, and use your third card to exit the room back to the
    start. Then after collecting three more cards from the dispensing machine
    you could use one to enter room 1 and collect the card you placed in the
    box a moment ago. You now have three cards again and will be able to
    travel through the remaining three doors. This method allows you to travel
    through all three rooms using six security cards in total.
    It is possible to travel through six rooms using a total of 123 security
    cards while carrying a maximum of 3 cards.
    Let C be the maximum number of cards which can be carried at any time.
    Let R be the number of rooms to travel through.
    Let M(C,R) be the minimum number of cards required from the dispensing
    machine to travel through R rooms carrying up to a maximum of C cards at
    any time.
    For example, M(3,6)=123 and M(4,6)=23.
    And, sum M(C, 6) = 146 for 3 <= C <= 4.
    You are given that sum M(C,10)=10382 for 3 <= C <= 10.
    Find sum M(C,30) for 3 <= C <= 40.

Solution Approach:
    Model the maximum number of rooms reachable with a given total number of
    dispensed cards and capacity C using dynamic programming. Use the standard
    recurrence for these layered reachability problems:
    F(c, n) = F(c, n-1) + F(c-1, n-1) + 1, where F(0, n)=0 and F(c, 0)=0.
    For fixed C and target R, increment total cards n until F(C, n) >= R; the
    minimal such n is M(C,R). Sum M over the desired C range.
    This is an iterative DP with time roughly O(C * M(C,R)) per C and uses
    only integers; memory can be O(C) by keeping the last DP column.

Answer: ...
URL: https://projecteuler.net/problem=327
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 327
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'min_capacity': 3, 'max_capacity': 4, 'rooms': 6}},
    {'category': 'main', 'input': {'min_capacity': 3, 'max_capacity': 40, 'rooms': 30}},
    {'category': 'extra', 'input': {'min_capacity': 3, 'max_capacity': 10, 'rooms': 10}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_rooms_of_doom_p0327_s0(*, min_capacity: int, max_capacity: int, rooms: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))