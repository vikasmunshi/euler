#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 824: Chess Sliders.

Problem Statement:
    A Slider is a chess piece that can move one square left or right.

    This problem uses a cylindrical chess board where the left hand edge of the
    board is connected to the right hand edge. This means that a Slider that
    is on the left hand edge of the chess board can move to the right hand edge
    of the same row and vice versa.

    Let L(N,K) be the number of ways K non-attacking Sliders can be placed on an
    N x N cylindrical chess-board.

    For example, L(2,2)=4 and L(6,12)=4204761.

    Find L(10^9,10^15) modulo (10^7 + 19)^2.

URL: https://projecteuler.net/problem=824
"""
from typing import Any

euler_problem: int = 824
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 2, 'K': 2}, 'answer': None},
    {'category': 'main', 'input': {'N': 1000000000, 'K': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    'QTVEOB6d93042xyslrd/7A4vYO2WmHKqQFxhgy//nnI781LbVEPYGWMWSd2ucGaVSgzQPGLUNGzPTgvi'
    'ezg6oe9m9YwJcGREp/R1GZqbrR/++eyhVxpsm1v7BVTQqkP/yXiksqpavJQk515H2bPCj8w05I52N7fP'
    'NKeTT0zuvMU5Zkfn4jVo9HyWdneHm1Dd4j1Mym82VjDjjwvkAGEqP5MIK9k1Y83cchQi1G++8wyuMOL0'
    'ECnG/1ivPMjmQRALie7WWum6YACrvHN9Zb/vbcUuStMJZdZyPkw24EEEAeE+oK3EuMtrNOoPaCYyowCX'
    'pq+xkBFOAW3N5F+p4J37lR9Iv4t5nYZzK3mWeEEUiY9fImBCD3+xc5AxD9pl0CAX//f+Kw5Mzi0albQ+'
    'iRufXT/Eu7L/bBdEgW5bIYOqIetrFqV/ORRiSG+hxlEiXIVq8YWNK1ACfx1CzphygGcPV66Vi0yJL4VX'
    'r8tq30GcZ4P3YnsXu/bFH6fBmMDtltc1Oe0DxNaqzHwt2lhSeOPSTopd4sAUsXVyvEQdcj4Y8/GFmYZa'
    '6O0aOEsHPobPM+Y/PLKIyrVKghxCxrmILgQVUpE1bPpOYCJ0qaMQwgHQNt43P/h6H9JEz48q31arRkhc'
    'xoKiUQn5Df2UbGRknMp+INlkWWRjSGnUdDGvbfms0c/W3JVzvCL9/YNWYrxVsyPWuTWeQ5ChKczFl9Pk'
    'ny6KMI4vDvDlXdqTR5Z9sLw05JqcQ2N7PRWuD4fr1BE6fmKC1IaYRIGYCLVG/U5z46d0bmsqy5xb0L7a'
    'pqtBWaWI/Rc4izVfRppVF0IOv5rvQDea2ILiaSdiKsl5NweqVs77GZZiYOnVNJ+97BUE5eWy96t4qSK3'
    'LzBTOoEjAi4hRVoYbsjxul38VLURd/IpKUP/9wddIjUlHiOHsp5vKPD+1Y+9bV5eW3aiO+gUCqQOkKF9'
    'Ea/tP7LxSZsXkTT98bJc9CEypHW/zJyTy3BbEDFzLtRPDRku7elT/yLbJjeoJ/WUwX6s2S6lAs51z9tr'
    'wgP/gwLsUlgBaoP1MZxecW0VoYauMNa8Wgwncldyi8bkqMYAsy2GCrhfvC9w8vvmZqT1xk/b4vRZ6iZR'
    'O6vd2rcyJ3eKnkOrZkeLWHtHfsLzfSOrRkTr5FNU0g2VgBYcG4O5D9AciwuuEksE3MJWG6in4PjjRxK/'
    'S0k5WEXB3K6/QjZe2fQo/nbo4Mkl0a69p9O/sjo/28iscTGYea62hxGkfxgHCfwofb5hs1NXgHmw04W1'
    'y3anmY/yFWn0OuNuS2nysQKktXxHrn0qSgeONUqPBB/FGxGDNwuWaJuAobR+4ijGSR6KlWw0mwTbd9j+'
    '5D8vS0deVW0x1OBoLh/MiPvNGGpfQ5jm7R2BdWDGv9Jeg8lwlkNQyfnNFLNOy8CnoNEWxA3C/DWPUc/B'
    'r9ajvvLqw9V/Pegs2Xxz9FoDVBj+x7AuS+mz1tGMfQR7fY4d9iv1fakfk4iJ44+yhC9RCdVUPpE0i4vi'
    '7FXlkEolRsSP0WoiBtYgcs/e9D1wGLEiz2oTIHUbSI7nLE4OlxiXuchOr5Kd+h26GkHerFvRPCFN3HPM'
    'hI7DpikpkFK7tXc+jhm+e5jRrKJT5jfTa4i0+BPpCrYoO0byqEzyiZvYKybdada7U66nDLZw+utQsCxe'
    'c4fl8zMgUQmWROhOGk0gVmDVzqR1PwhLXAd+d6y3icj9Ji2dE0GtZ5jVONDq9JGEe4sQbzJLMtoG57iu'
    'QaJCtjoAH6g8l/X02D07utTUlI4c03j/mTZodtEqAEmysxxp9dgn1MRjfB1Fi0fsYezqI0Ispq05wsAf'
    'a8BZTgoISF5jrE/b/dweQ3zoOndUY3N2Dc9x8R8dt4kSh9rRyqOaIC6xHLPKWzfMTlc1K23AbIM5Kxqv'
    'VuYEwKXcs2PvyEWZfzrvxT017N3/nUaA5ruKKnqxxixgLn9+CgDpZCZJIcCIsulbuMpJJ1wgMviJABfg'
    'xt+ssUbPiSyVBx4ALYW8lDpXvA/qS+CrI53PCR1IZqGqeHKx1S4ycVGm2SZpu8D439H3vc+lsmhfEYWX'
    'dO5Z0YkWDVFhtfIUUzSutzjwAp76u9IQ7F8T+dEEVhq9oVKv/AWTsPS0JdQWPLoOde7Ej2zSCg5Jf7vp'
    'MEYIyJkkuxahVR1zmCzFDx1fHySJ+5tdy5NEDO9M1d530xZLajUBY/EyqnDsBQ8jXfmXNukC3fvp0Ach'
    'Vaa1qB2uH7Pbcd1Dq2iloBGmlrz+9aiXqwbM7AP80FW7UbiC5f5wYO0EYZwphvfZFuDQpBLdbPcdUIzU'
    's2WSvs4FgJ1x5EtBXaGB4Hlc3AEpwkbCSbbjHFV+KuQF7/X0mc9/VhYQOkTHlU0oZsBDrkFN+7VaRxIn'
    'KXJFDH0B/P6Iqo4TPX8AzUG4CguexR77m/FKGFX5LL72uT4lZsQmKUBLpoAQULsD5H05k6pdBQ3Xh0JQ'
    'UWb3HnxFcIC7Vs08tlmnt+A/Bvf3n+cOPV5qjaLyfZ1hPIJ2FYISAJ1tVo8esXhOmY9m0Wd4X9Yk5skP'
    '3bepNfqGMD1wHspDHq0cMK0sHn0qpE7C+r5CdCRJdWwTLlSbCBevLYJ0JymagJu+in0VsVXGW+hYLG1b'
    'VYJ8ppPRr0IyGDv7RC5s5MOE2h6u6Te/Wgjbi6Fci+KyKgEFY6KrVL9BQq1Y4iOaP+0inz7msBdI8yPB'
    'jQjBUfz2jh0='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
