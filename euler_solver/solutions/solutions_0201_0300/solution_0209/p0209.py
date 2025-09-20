#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 209: Circular Logic.

Problem Statement:
    A k-input binary truth table is a map from k input bits (binary digits, 0
    [false] or 1 [true]) to 1 output bit. For example, the 2-input binary
    truth tables for the logical AND and XOR functions are given by their
    usual truth tables.

    How many 6-input binary truth tables, tau, satisfy the formula
    tau(a, b, c, d, e, f) AND tau(b, c, d, e, f, a XOR (b AND c)) = 0
    for all 6-bit inputs (a, b, c, d, e, f)?

URL: https://projecteuler.net/problem=209
"""
from typing import Any

euler_problem: int = 209
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 2}, 'answer': None},
    {'category': 'main', 'input': {'k': 6}, 'answer': None},
    {'category': 'extra', 'input': {'k': 7}, 'answer': None},
]
encrypted: str = (
    'hP6ghKMlVuk0STI3MFoLMXj2ROBAytswbopeyp2TRWZesSJMo1Tw8cW1dxEQMzjyLLA+Vu0vPRSlJGI7'
    'bt2YD5vyGPd7noeiRGRirRAiHoTPnj931OQtlK+4M42Nj2AjGuS2wGy70m3vEz31lsb6PQWn9D+t0oV5'
    'FTDUBGjHRBvPbVQE2gse/MK0mgtjAqnK+mpbYN3EpJbDalr0s5Q3lxwFjJOKc501boUohsf5kcZTJ2tX'
    'aA4lVSjCdUYTz5lhTKJN4sauWedjzEJBHU9vFDwQj51gnmEUAV7pQJjQ3SommHitQ7zQxE5Fk0KfeGpu'
    'py7TpE4dmXUlyhN4OvHob+s9AdLahrVhBnwjN+SsLMNQjJoM7Pe2L2dZu35jLN5kz9bhZ2Q1xt0oxZlo'
    'iuH3OeBf1uJwjK6eBvLLNqNAGUjFLfCuUGYIYA7x39ZKIZUNRWpYTArHAkbCrYyozPetNz4YZOLm9gB7'
    'JXy4wQ2cs6i+6qUg2atbBlrjgJEUK7yvnoXoTdQCX6urtCQDB4+/GaYlT5+OWuZLgCwi2FwjcmxCoEyB'
    '99XxyUBd69LMd7/nO4RLob82690vLvFpnXH5GeyEygT6R0CrLrUIJ9wmOxVCl4h+gUF+VvhZ7JQSELAb'
    'w5TRQqsWeK6eAwAp85vzny6r7jfF9odClLmtPxxvoFPy53dXU60rXlpgq5smbJsoyuyYomRcxhzd3M1g'
    'JmzFiu5BfjxSkulD1TdlSAVkNSUK8xr7nRn4ZFyggD4W2TSi/305zC4WGnE29tpJ/ijERSvWSwkFD7qv'
    '/bzP8j4t4o8m4a6ja2wV2BfMVaD6l5gv4lMJ4MP3myeGt/z7gAxrFe7vZ6CAu86VXEs+//2yfMzT5889'
    '/+bOcWXxRkZdLpyPA2BYZQGEXEt7C1ONR5Y2yGgb6kj3cVxOYhzGwbJ93jqGb9FWhrxA+KhM6AbGCe0r'
    'aYt7CynGKpaYZ3CGMW5Imhwp197khAXaTNB6z1c/Kdv0xRtF5lX4FugmbI4ariCNqpdFdNOAsZ47Ywhl'
    '2ODUcSy1gYX6H8hPJnl5+r2DVrorRHStxUpIjBIw1GlfGmuCzTNe/PPecxy+kSwlR5CzG9e2/aCPfK98'
    'jRo6fpHFFSH+0XaW6PTkUDYGCwRwLYXZ0qd6zAfHoEmuOAmT+6q3ApxoNMk+RkZTETLefK6O02RfAH7C'
    'YtPlddfUuN+Lgrt2sidmTngYtbcK2aL64UEiJe8bhLbTNNv0K4BC/S7ympNxEXb9aZRHEReFU6OD6bO9'
    '3nHuxgVUbbg/y4ttInOK3iNoszDd9bZdtOI+l9wyuw+ed8GKca8Wyr74TnNaP2jXXUNogKlYg9nDzIsG'
    'jUyCoa8qUMbz+lSs/qLNk+qh89FbKVl/qeH5gywz75IadjpM00VpM6bBb2f1lROqI7suxx1AB9ItjLBd'
    'NF++urtjobn51myKXmqgDD574755X1Y3EWsL2aMQmDxJKNgl7ogbJPZchz8xzQ48LQM19ENaX1GKxh+D'
    'Cb1bXOuIM7CCxStR22n3AgIQdvYHAkKKtfO9kP1rbsMiYugdavlWKBXXWZOwwOfKHgI3XthCGNDaskfp'
    'FMatTkUs9o5tASnREJ23Jf64XBuCuyBpUIkCASV5aIep2gvvhjMTujtkKlzY7sOc69Ox5z9tEJiETXjb'
    'KfeUDHpupUtljQdBd85BrVHzlmtFzjGm7LucaSE7AQC8ZgYcq8uIFj9+ZVJd9Ed0RNKJQiVWAc/J3DkU'
    'tFJ8F/Aygu3JyQBPPYkkcZpRyA5HjMiXw/sh5q98UFuxJL0vqW+O86XDV22vN+tRpQ3cet7tKWLGm7u3'
    'BS1h/E3/TjdDNLL3JbbilzQkMeijJESvmdM2cLrQKEQ1Acz0SOfOb3GCsq0QmHEwWlom3qZOyH4Mi58q'
    '2MNHxF/doGmC93clmv9e/2jk2RA/9TGlOfCvtRfJeht6eW7ExtTSRm5UJ/eENCP5+PBXugEHaPFXrcmc'
    '5NrsDWpx7NM7VpCPQPTVxWgpn/wp2XwLgTh2QaP341fXzYmLlG8GkJyOw+o9ylFzv7VaDDA0tYtG7izr'
    'SzALjHeDvZuBMOb5PTrv8oP+YCJu2X7evs4ldMl81KsL+OJMXV2Zd3q4nHlTi5ReRlo89KsCO1opkwpV'
    'u78Fyqa2z1BO6IsPx9hZHAdJ9m3r/vXNqJ3aaFpTDlWjCJ6qLBPLuIOBxOE6ZjnNyxRbGOwlG8EWkQIi'
    'TXqjPI6kRYKmG58WbOua2fIzQxIkT2ZB6QpP4YshJ7ZgA7DyA1kLDf0Q40Mbpm0y483dRKcZHp8RI9Pg'
    'n+Mf6FaDzy7Op9or4S7sYnzKLBqA1IiPrhmb/5gjlbgCt+ouQ0Ws+sb8aCpsiidXwj6+uUAf5Wk/Whf/'
    'qX0sKOSpoB4K1ITzOUP4It6J2RQ8TGs/HgTIihtXAHmL3wPgrlFN4j7HkDtfzZ7Q6wF/zjljns3UzNc0'
    'fJ6Pu2kcKdMJkqY2gpGdANq12Ribq911tHmYsKmoWs1uoGsHSgeK2tn8bsU0Azf281cj0e22zYHM6QWX'
    'd4aTuGChHtCZ4e5GAxZVHjAbyDjclXuBo4TuCt603yU='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
