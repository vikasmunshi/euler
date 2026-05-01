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

URL: https://projecteuler.net/problem=327
"""
from typing import Any

euler_problem: int = 327
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'min_capacity': 3, 'max_capacity': 4, 'rooms': 6}, 'answer': None},
    {'category': 'main', 'input': {'min_capacity': 3, 'max_capacity': 40, 'rooms': 30}, 'answer': None},
    {'category': 'extra', 'input': {'min_capacity': 3, 'max_capacity': 10, 'rooms': 10}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
