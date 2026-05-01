#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 897: Maximal n-gon in a region.

Problem Statement:
    Let G(n) denote the largest possible area of an n-gon contained in the region
    {(x, y) in R^2: x^4 <= y <= 1}.

    For example, G(3) = 1 and G(5) approximately 1.477309771.

    Find G(101) rounded to nine digits after the decimal point.

URL: https://projecteuler.net/problem=897
"""
from typing import Any

euler_problem: int = 897
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 101}, 'answer': None},
]
encrypted: str = (
    '7Y7Wt6mOB0yV79+Ye7Xt3WAew/ENPQ2z9Icwm7hLKeKVKe5LyyBLgFvZjzjP+mZ+vlxvFsruYxvJoGuo'
    'gh6dmoRk1WykkKz9RQOnq+0S2qOY4ZM+OQXuq3D5v3m//hx2Jp8HNsfGZLsN8e/A7fEKQLIz5B5/2mF5'
    'r+3DnHTStznaiIw/CQrIC07flto+O1XnXRJsIHRbB3Nt35QtipvuJNQvUwwaMEfNqjbth5Xj7agkUxss'
    'XHLAm5FvTqRImELO3kHaEp6aUCk5CeRvigXLvnyphOnSLJfkqzChMhkL5bC4JoBdqOvSQbBZjb0gefYR'
    'UeqJI005SDPeOzKUXbp3o+PojK00jjTBOPBS2bymvi8zEJ6eJUiWUXI/ZFydIV5LrDYMclwGHZq1a3AL'
    'hYoC/XZwYMFEFHeki7WTqzpWynR2tr9IsykNf13YODl2AcJndxTLSeBUb808c/kLwvuXECSJKomQFRUx'
    'OGFBL3mB8CCH7wNLEOr6YpSPwDU3AtjkL6X7wPxhHLLCOVLdGKbCWejiGXf9poCUFIgmkbNago2+ycHk'
    '0UihccdQdsIPxd2q0fSZBYKMYRxoDLPZeW3rXsuHezjraIkKatOENEpOt6y5z3RD1NrYLbu2FLC6vmd+'
    'V9Pp00NOgqszddeekSFK17CytZnnwBeC2Cj0I6RKZyy9ZIwtKCImH+Kupks6eqeB2kYcwA6gNisAjNy+'
    'FXGfDxzzphpwsiZhTLNGz4EIvcfXJXPsYR75D1fLkBb+ZmfAoKnh1aKZiQ0tzN5UVOWPRbQWOw620ara'
    'efWY7G4RP0twbGaiXt6DOUuZHDBYF2jQQZt2iLpB5a9S7UltcfhY853b0wOAOdQCfKOTM1zdja/r93Dh'
    'J8F/2vLGkBi1T1kQnJzZ1BiWGeEoVgJVL408s/pXpJ3CpjQfusc8HormcLuFGIamXJHSP8t3XoKIkhLV'
    'DAGQETMEZB8ku1CUnfPTmD8NF98zaKA3lc0rH0RpF9oGAFkvW9XUhG7gl+f09cNJnGBWD4Zt+76P0z1k'
    'eDcf3i6LOgm11TJOfqCNnWZvWXq+irww5sc9eUmPWMTk8HB+qcw+R2hdvk7l3NlIqn/3l7opPs/FM9HG'
    'BlJwK9otEskQBGYD7qParDOb1Mmk891bi3P/3/ZFZJ5QPacR1oSXp9ChWJqPfTAYleKjdeNsiz/tjf/7'
    'r3bmjUTYWdXHEsH4gQM9twxbdRLAzsXlJst6ESOd1Z0NW9XvX5eTvVFyH6x5aIy3MFUVPsMC2MZmyKVT'
    'ZJiXu9EwD7vB8V0IQs6dC8YirEhIOGZTwNr5eTCxX73nYg3yWdjokIzt2VDI5bgVIeCLjaSbbu++X8s+'
    '3rYsG/rXVyCaieKt/mb9r6v5PZU6NfORYRb34PSL5k4QL8z7P4JzKMQcwrnvEwlaNb+KN5G58TUNzmHF'
    'YEHtAJ9CElL0UZq+SsLfzxeNcDIo/xgczNBaqUgmTZNop21F+Ft8Kp+C0oyTTSTpadaUaS+C00qSjAcH'
    'aKD10zgIy3xkyxbOGkRGEXOb0JYI7B0lxo9ayKemVY4CaN6VDcSwoBiEY11ExbHV4Y/Niq/9Hr2fVgZ6'
    'NIXy1MGKhHymRMJu0puIwqRvi7hrQdWnFCRcScYF65NonY70O9BPNhcGdczG9WyF1UtwsSSBb2h9nG+P'
    'YSXU6nmwpWOODtpQvCfMN673W7G+zz2t8NhQ+Ga7z65puTCWY0z3nVDr0yfb9orbI6LyaZ80Liv9i0L1'
    '0AvxY7iY+eMB4Fuk19KNGkwSTe+M9W8DHJxP0NYFrmgp9G5qoXN63JRyiEYUvWwQ4U4wxQrYKEY7meak'
    'HC6wPr8zH7ST6e6Bw1XvP1vPRvGcwmdinCRgTQAZHlUk58H+tcudt4g2Uq7zuiGi3hFMI/wRbscJ8qOW'
    'SXFvz3CcaEHPAZyBknaWS1JW3YjxR43LDGib0fAGMdTj7Qzym0bAe5KUTVe9mn3lRkaVzL2D6wLbgWzV'
    'uNdGKi7raH3fhxlXCROEa9VeDdi0pukX1Gnm/o9azyXw+CvKHAA6qQWmvMh0tMCaI0egx9hqUnan/dQ+'
    'hihwpP/c9FZtD21PhSObzLaOGVCEhLvPgTElgrJDV4VO47Vxla9UZR13KZFzvLg9I+mGzga4SoLJpcOs'
    'o+UXuN5IXsQHXBaZ'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
