#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 241: Perfection Quotients.

Problem Statement:
    For a positive integer n, let sigma(n) be the sum of all divisors of n.
    For example, sigma(6) = 1 + 2 + 3 + 6 = 12.

    A perfect number, as you probably know, is a number with sigma(n) = 2n.

    Let us define the perfection quotient of a positive integer as
    p(n) = sigma(n)/n.

    Find the sum of all positive integers n <= 10^18 for which p(n) has the
    form k + 1/2, where k is an integer.

URL: https://projecteuler.net/problem=241
"""
from typing import Any

euler_problem: int = 241
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    'ouSvP1EyX6RjhGcjaNF0ynzeZKDJkvyekyp5qtMoCKof2fVPeUMssc+OUxTtHq6c/O+O0QHw6x4EmMqT'
    'w8UBJtLrbizhlQB+xbXE+ZrOoKYG08kj8W6/yZJR5RBtuEkdXH9UoIZ1YozZmMcQ1spfyGzroLmQQ0cW'
    'vUaMqKyg4UXGw1zUHhXL8r4wjoMQLT1P3cHT9thDkRXk0fjgkcNbR2sO4Ugcy8IplqHwa5CyRs7t2wUo'
    'IvW+rIWW1nyGQDq4zeQ4138jkSuJwsSfQ9IUlrJtI7IDs80fewb5rfHHrhnjGUkcrQ4a2mXm2eZ3uonG'
    'RvzydFrNL4RHNE0MLJnakUiMtKz+l37KGvu8iiocsHFP5ljjsovUrbbbtlTcj9c3DrPqHaSdpFrF0V+i'
    '/19pFBD3mfkiDWNWNtoGVTQU+enajp7Ziw248/Mbf4JR9WHrbcQBR/b4JzZJwJ6mMnRpSZDnRQ5EjV3k'
    '0UapSlxYV+CulPuyY/olVYWFbewolBb1gyCnfdINQPyOv2d54wdyJG0uMFBTM7U1WTnYgyC/EwWhoefA'
    'nCEYX1swGNF8Dt2RxE+mSyP0Yui22qP2mXMeYqU60z2EaFIQyaTsHX9m9M9PiHByqCkF+nH54L3o6PoX'
    'o7Y5raFakzgAsQs+JXlrCy8713iKtRWn37nqjRMprO0w3OHyBeVnxqVGeavAXnAnYEIxr2TLzZz+ldjd'
    'wU7jFxe4ZV1DN7w/Oa8FpEae7PArY8/cqmIEL54jyXGmPxZTElyuP80iHI9Ibrdiy9hqu7QPthy3szhN'
    'kYpuhLvtEoh1RObPHYnWvMPN0Z2ga0ADBUksBJaJHkaL33EFOCQou3vekm0u5UvGabSRD6rw1PphthtL'
    'BTR7q9XC015xPzNC9mgTnmfxQFaS5y/8zm7FNphX8O/28HRwB4IPAdpNC04OFhn2fUDecMUWfr8KbHf3'
    'inSKoh1vTQF9DeHmPrQnh6QxF98Nk6JcOOws9i/06nyUL0jacoWWc7F2wKKyvTmQtJ1N7DGhVeJqK9D3'
    'SxMCCifV1aq9EqkXAbinAitjtcqqmhw3eE7wf5yqaPeoRK2vOHeA2kebwQvJIk/yoRmVv0jxvZRytioS'
    'KBcL1G8TbqNQAih/g9L3Ywk8qEFmLM/lezuB5Awpj6GrQiTUQP693eY4y8/1+EEwdjRCo5+znByLyc2m'
    'eSwapkiHF6QwytUl19VY5QTrMxZJXjTGl+9zcRYAFSY90/TQj8DVAFG2im+122ZDuB4tKyupguDKZOXD'
    '44/3Hp3dPjApaLYeEk1d3TBVAQ/aRqKmUO3CM0xO8fMpCme77C0yNbAMpA6Qz2/GTVDbK1rfxG8ioV++'
    '3KX29IgvvrIXnpMLW1iCqTzupQSbPdaiHxPVPqtRS9Z+iOjoGNXcR/IXenIxdB6Im9wy6K9RCHIgtIN1'
    'euXi70FQVKuZIE3gp4RlWHmBIoUbT+7oqF/S+vvCv5mi1IHqDPc2iYCuIb+MOzUoMslRc/ppXXCSgs+C'
    '7ectm/E7M93c/3HfGfbaCTZ7lqWpHB70wCEX+o19qm+GJgaRYetHl2kPkLOxYEd52adQlowAAMgKOm2r'
    '+ibs1JR9Vqt/4WrGxng0PLHslF/ACSCvMacXO3zGKwA4bckInYjuYbuMf9CopYmWBq7YfrJiMUMcgz03'
    'ZbePWgexTtVVgSZzPkqQAy6U/NOk3PiCmBYVkiArGTshgVWox1NrBKdgnJ8hgOLo8fIA5AKNfULBlNw6'
    'i73ac70zK+TapLx1Hz3MmU0qjjyGYdfEmL79AyvEKJ6Gyi23luY5Vs2JOLyVTbn/VTdn0j4SgzjOzP+c'
    'z9VJrPvD3HPbVUzN+pP1RthDLm/FnKtvqTbQDATPysEXchhS2p/qR8+cledrfW0XM6d4AtHR8Clyz7oV'
    'VUtJBUTscwU9HP0ORLNjG/jN9BDh5EoGeobm0ChDGuLt0+lF3DmZXdbvkUjtJK5pB9eAcFBBQXYxivPa'
    'Z4TayvYBNYV3VRiyOQLwv+BkqXtFDCaDxkxjAiyyeHfXWJB2ciPLgsmSRyG5nJitc33HI51DPcOYFsFW'
    'MbmT1i+m0IMVYf4gZxZnZTs67yhsN9KzbSGGc/Qlh7UtmbGxysLF+7lotVo0jjGecdUxDD9KSjcaP/96'
    'w2XtmzRb+j9ikYQwnOBO6GSOczvKvXX1Nik7lv8Ov1i/v65UQ6nyNi8V6+JDs0s27WuuJdMsG2rEZXlT'
    'NzJVNBB1j4UzmHEf03BeI63D6hnbGeyKRsC1RESso4LxsEEKhmkuxVNP/M+pAR2sYPlth0osBwKGKCVm'
    'QupdGBFHg9zOb5kXvyI/AEdEVs1fC5snqLA75GGRqGNMYSTFCYQ0qnISqd2jY0nmho0rIcKhULgX+qkS'
    'lg1R9RG81px/Y2bgOBe+ZK+3YqTiYJlKfc/on0BkHmjeLQYFlnusp2rqc4mpok5M+Du1eXOWjPjxWgIm'
    'rMx9USbUBE2Af3mAH4a8qOiRh3R3bhojB6SYfgqh1nK/hnBuhEZriTJLcon5G/cWn8/YBNqrrcZ6JtMy'
    'Dpy62OPgnty/Y1GjJZLbYZqCAOOScGGYj3Qz/Vmgzo7lVoNCV2uaC8A/PArx83qv'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
