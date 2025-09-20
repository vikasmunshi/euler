#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 273: Sum of Squares.

Problem Statement:
    Consider equations of the form: a^2 + b^2 = N, 0 <= a <= b, a, b and N integer.
    For N = 65 there are two solutions:
    a = 1, b = 8 and a = 4, b = 7.
    We call S(N) the sum of the values of a of all solutions of a^2 + b^2 = N,
    0 <= a <= b, a, b and N integer.
    Thus S(65) = 1 + 4 = 5.
    Find sum S(N), for all squarefree N only divisible by primes of the form
    4k+1 with 4k+1 < 150.

URL: https://projecteuler.net/problem=273
"""
from typing import Any

euler_problem: int = 273
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'prime_bound': 30}, 'answer': None},
    {'category': 'main', 'input': {'prime_bound': 150}, 'answer': None},
    {'category': 'extra', 'input': {'prime_bound': 1000}, 'answer': None},
]
encrypted: str = (
    '2sRVPqSe/Vks6Um5bt0R5C4CkIpoN6lz11CT+3EJblKByr8l+eWZP3Vs0+99B/7TZX+4D1Cxucig0F9/'
    'VH9RundnbO4NQaXSjUqvU89nUmWgLFKLqeXok5M9AgG0pQ37yRGLeoqVmFnkQR4gei9hUbtRDmBLx3Gk'
    'gPupatMeDZgyIyGjJHL1WnxVDTyuZR6sv+l+HH2yfDjVq8ygSb6Q5LSi1I31jW54IMAr+E+LutwrCOYf'
    'Y7t3yHljqoTh94wsWQrS0CDA0xHTT2xDRS1z34aITzeeeBsN+0+EPC1u83YEmzTSR4GriErwcDITso2u'
    'jtRunetDfkJPteM66tqCR9ZGdtSTu6E1xmiYaOmupbSgyIuz120G6SG8bE/cxpbhs9XDL+zDm01PREUW'
    'C4rtE3ww9cXyQHF82KVt8di6Upg88OG4uNsFpUrFp5MDmru9/dtTSCm2WWU7CfMEDoxB2PqRMZG7cU0H'
    'R8EvfMvFwUyixKP4MvEBOXqXlA0elbbYJvzyn1eq1aPr5VTvupRtcWnpHR5lZMmtfnYoiVhPmcD8KO9U'
    '/XTYF9kfgLRcJcbzTGwfcMKgL2tv0gzuYEMGbdOqeP0E/NFUemYI7T1cyLLNyHB+bksEvrrWlWSeERQu'
    '1kbUI2mhvFlbwDnJ3zSDLxctwQpGM3qVzZiZhnkQjgA0u7I2ZvQ9mnyj600/LBRPYjmOWe5Pn8r0EQfV'
    'Kkzn/zSLhoI6U8RAAWSJDyL5aI9CqL1rXCKo/Z6wEbKn86uBNV+CEOInHSDAzqmYVz4tVQ/95sF+uLX+'
    '0WAyug/SEkv9cspwTb9j9fv4AC5Ca9ilNhqeN6IaxmIuZQ3nt4s4SpsjM6FWdQm50zVuuzdC1aKdeaOR'
    'AWZ8x8N/oHHWQsPCzaIdqyQ0DhZxj/6rOnGyPfN7MuqXydSeLR4pELBzvPMDJ99eR0ihHNb78WZ2wgn/'
    'j8d3QhIpIVCjGymOdTtp989RSBK4AWVeH3QDv0/bHWBwm/bYyka1JVO2XIyrWxpZmK94EeAzrKP5y5JH'
    'pMTO2ZyfldBgxlGB9bJlmpGE+xB1UWYqqqKXDjizn35Xy43PItpmWusE+QnwhH95hhRkHLtSDQwKOgN1'
    'eH2Pb1ROjETjy8Tiu++bmsrFrt3ffqloHpZMNFvt86yB1115mAL1qo0YXV6TfcIS0Z/Ac6njrxJ3/dwg'
    'jT9lXVCEPF+4EebMEwKfHK3zht4XyI2F4OtE0rDP6mtLzMLS4IRy12wINJaiZWJqgb6omsDhtsQWMVH0'
    'xvMfcCXq+ixPzmkj4i0FdYyHvPiO/bPEBmjm90yrosR989kVvog15Ao6//wnyJu5clfMUB0gwdrLCD4j'
    'Ob+6rVvYER4HXcXbZ/k6UPfYrZQd5KaXlH3RYdxWQYXRyAJtlqCazVdKsjUPXbxbytgjfdSokl+3/99w'
    'SHyReyVxvngQt26qGsh7fqcW1JnK89Sxc6oR8ilvXbEf/EGQpbQQrz+PRk1ZP03+xTzedzQRQEVBn8pe'
    'vaBsKCENaDve24ZnUTeMGsQ6v9S8oipPAULexlUVh47UnIgQMSW5CHDsaMQDYCDQL6Uq12c5rUIpGWgW'
    '+DHZFr5DZRpj2Qfiy7/qUHlLZl+Sg9namt/5XaWcWYm6/IPhMIZUgJPReo1MeUwMwN0GF3+SHcFSyDFD'
    '53YKbPp0XMNslvrsSzOKXzGiN+Plto0HrznB4AsdZPMcLWYrrqUmgHbSTVyGuKGGDX9oSdAOyVS93DAq'
    'xaPX9Mz+rdrd1jx82/qND8KIDcZIaHtWI3lJ38xV4Qui46uHwXkpggnLwaPBa/mTPhx3PFOPOTEZ3wjy'
    '4nuZrW35U6fY7FkuWmydzh4DT5UPdZGKjj7DNbSIcaf4Pa276yFoAVh6HuSonbpNYi2GI3nnL+vfo1t0'
    'TAfInsEBV//EI8jrI6FoYSTtZP76JCu5ycGjUDKzPEPjx/wYhmIGkVT1kMtFBgJBlqWrGaAEwG4qT3+5'
    'TOgTLpPcIezPAYQE8paLJBxBDKzO2IiKWc5b1X7vS3HDSZ6cDiqNBCJqFAsITaASWYNLxRD4313dta/w'
    'RYzVcHWkG2qhB46EWsKX0NxMgyTq9eqGcuYkF4/3WfM8EOlzAhU3I3Jk4f8W82pb1CdOjYQwdPc1WKtJ'
    'CFpApsSFSYPt24Ynm/C7HjCSY87JzOHd+FqHD8opWsRGvv5naKGnJAsKAD2WCXsHRAnZHiRO91nOqZGn'
    '2BqlLIQNCrz+UQfLrDqi2mk19rOSH1wzuuk4oqkdqcwfQ/479eBqC7i6ZUeofOLAYdkYuGcOjgmXFWn5'
    'xJgxSlBn38OABC1VkBAZL5s+12s9dwAVzYGu9lFMceDEAHdt1ei0j6TmiKGTQQCfQ+TzPVknTS0/g+yh'
    '8z8rochNzZhoqcs1tx8J9BqHeEaJ7xskNN020tMPAo4KKOAreK/Saox4TMjQ3GbGBtxZOX92ZThae5Fu'
    'FC6VyoMW4XIVqEdQlPzBNXjqEkwy/xt2QUqyOFxCbDUXSYD8ZYqyCf+0sk1UYjzjVv9unc1lNfeRv+WV'
    'gUp0JDmltgFK4WLPEi8PdlDGnYNrPBSjZLEa2tjGgao2Z7R148NS6SLW1RX2tgPW0RCweUFtKbLUW0cZ'
    'Z3gBHi4c6s4ZiKHV2aleNPRseTVK3hSZQL29AsEY8H7m1zi/Neqt7WoeuhtNdpAmbaIOHUGmyGBP8iGu'
    'yqFYB9km1anFHv+YNwb+S0aLl9r2oa3iBMGbvgLxBSERMBafP7i+gfqcjAKTPdhxJjuKEaYdWy4ef7a9'
    '0XvIS+n6SJzC8AnY7GXarg29VndH89FOfYVRwg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
