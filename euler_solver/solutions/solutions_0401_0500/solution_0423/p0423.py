#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 423: Consecutive Die Throws.

Problem Statement:
    Let n be a positive integer.
    A 6-sided die is thrown n times. Let c be the number of pairs of consecutive
    throws that give the same value.

    For example, if n = 7 and the values of the die throws are (1,1,5,6,6,6,3), then
    the following pairs of consecutive throws give the same value:
    (1,1,5,6,6,6,3)
    (1,1,5,6,6,6,3)
    (1,1,5,6,6,6,3)
    Therefore, c = 3 for (1,1,5,6,6,6,3).

    Define C(n) as the number of outcomes of throwing a 6-sided die n times such
    that c does not exceed π(n).
    For example, C(3) = 216, C(4) = 1290, C(11) = 361912500 and C(24) =
    4727547363281250000.

    Define S(L) as sum C(n) for 1 ≤ n ≤ L.
    For example, S(50) mod 1000000007 = 832833871.

    Find S(50000000) mod 1000000007.

    π denotes the prime-counting function, i.e. π(n) is the number of primes ≤ n.

URL: https://projecteuler.net/problem=423
"""
from typing import Any

euler_problem: int = 423
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 50000000}, 'answer': None},
]
encrypted: str = (
    '0mud6FJPWlmSnkRzPYw/21J0BDEeGFLadOCfLh1ZPZwc2fTrIWjHZnVfQrzJh2oyHR+eteQmwOO1kvu4'
    'B6tdMa37Z7H+JLX/IKBdpKKj8maGVj5537GxRo/iMNjfQeTimgsXlXdGLO/Go4TREyM+ICB5PBHTLLKC'
    'XSI3noVeslWb2kkpWFowbrbUN5WcPjBGjU5c8He+1PNoGjHXf1pA5iDczVT/lfzvXsLkjCSQQqe0Cdsi'
    'KsZ6we0waqsyC5KFvoC5OXM2/lHOqJlVo+vdwcltlbyj05bRU3mAgiaQPq2Mke77TPZMxCqgtNJJ0YSq'
    'yFjo6Dzz3Qryeca73aiqRTC8Wdvf+Gf7CElXRluGifmmN8CJS7PMGBzZkQZ7n6I5XXQg07YpiJx9H72+'
    '1fpiwZa2OItTVA6Z98AQWS8PzRSrE1/FJppO41K0x3DeVlPKrs5H1qqviJgBAQMWHOsWOHgdU7JyiTN/'
    'uBI4gBd+KFNCNXEGQc6PyQZ5Z4V3sYc2P3J5qTD9FpPmPR6B3XDsglp1EHQzjoxTQXS4FS0z5+hkSTyA'
    'Y16daY7CLWzjG7cthBFkS2ljhueTb9UH9E6Xgi3jtsmjttbVm5Tbc/6OYoJ12Z95/rM9X51bBfiMCEi/'
    'hc/FEjVhNNK3HxqlwhTUbMgLYSRia84YrfGtCdaGLhgVDhTZI6dSDt96xelSd3Po5ZugR5vk4hotfWFe'
    'xiXGdCGc4gYI6fdiHyhI/J3wtPdXide1/A06mzjOSc8l9aqLstXk88SpKHlw7HcBTUzmA0pqtIulgzCp'
    'jgsvHYJUf/MSCNZCMTBFHkpBHMUuBJQ00V8nqELYtajX7ZbdRNpFWJTKDFhJF1MX3k/w+brycwM9zww4'
    'yVKHGtwWXb33cWzknb2N5CfWpw8vOJPiZ9nS2C1gTJyQR+Y2aTzNl+uROXRGLceg6CF3xe8thkO7CH74'
    '7zCYvPnsf3n2Q8EyPkiTktPIpnOf5O/CfgOeIJefmigsnHdLHdjsBwe0a0x5f4bEBnvf/4i2NxvqeVyX'
    'NN0QneNPSybnaRjgAHdJ8fMsJrAzfwOV8JZofupcIlExrF0+VvbO21HyhpDplKyM7mBgdwTtiKXuEWwK'
    'NjxP77L4vZbgi+e5s2URlssvU+/CwlHaQTGCb/ArNwI27P+Ae/oaBZRTrhs/01vb+R/bFSUb9nksaxF5'
    '+IdXqnSKKOM6UuTFQMYkpdt2Nj/4JetENsC+T7DFZc6KdN9ythYUY4Cx/JZonjtS1QHyg5AqX+LTaJrL'
    'agi4FH60KUD1AYlu/MTLjMhD6ia/0HaSIEH1xtNoK7UvNZMRQLsALueoM+gawbaJqXcCQEexZxhDZZLr'
    'R4qY44nNmS4iUJPAVGDZCWsHalFyydwYb+LVH86KAzT1ni1Ue/eI6JmzcgEh18GQvY+52aD/XgyUXdIS'
    'LQzIVTUhZvbK+Z+hJF6Uc/X69TALuDo6/R7Bj1Wp9JR+u1m+3qbH5F3eZqc1ighh0esu+ViCmgjU0g32'
    't6j/J27kGBGEn4JdSEd83C/Pibc4LB5oIeWG0OiNPeh9H/oRUYXnXQVsr2hb7VSeN+ifzpUBxkeoHeRm'
    'SXWTg+qR9hPIKrnz13Cm2e/2+PfYiOWYWT90bydwE7Zj9HwmtoYyZlh08c6KJVd08IOqoG/M7xUDnu7a'
    'QANlq2E+hp6Q45BT3/e1KmO4F9w2uj266jQsohMxnsrg/vYzVOVoLetp4bD3Pt836IYKTBLqZad8P/l5'
    'STFd9sIitbn/GKLXxEdHm7pvOxBA6Ik2vAW9eL6b5M+u8I4+28nQdyjZS72vRBQ65upkz0z4An/bTYEx'
    'phD0pjp8n+YU0DVYvixZMcl83HltLEAXwOWLN0pPsFyjfSAMrdKANNOlbAJeKEwfVP7ugzTZGM1Hh471'
    'KOMvR9gpdaSfMfbZNkRhLiwwVlgm+bicJh6uCKgved1GT2QDVsrkHOnmL8dN1RNoHZGj5QheoMmOeWAo'
    'uCBqECJ86gLI7GIxIjzUlEaYnBBZYvMD/2klmc6GwYFs5X0py8t+41b6DtfaWmnubp2WOESVlC+f3YKo'
    'M5YR8DmRo2kcAz8+KeNdWeWqTi20bwnjW7OFABq3o7Pu+IxNOtGDmkG3XGWdDI6pLEEy3+y9IZhF8lj+'
    '4fJslhDfU7L+wMV/2F1T00+8RxMlCQO0Sy+uX/mss/5iIj5FdBoMeGQWFWChGatDUGp22zvLerpCWqL4'
    'GzYvUPMrY+EHB9Ym/whbW6CEC4XhxFwooEwGBWflESiTRzPKCdX4pSDn+KauQljU840XvTh35HaJOv/R'
    'HGQbnH+wBbVJGfn9+VMl2hTLqDfe+YmKuYHwqyPb0BGIgUL68R4kPjGnFxuiOismdA36fkHFoKZgzxzJ'
    'VFg42mtyWneJh3UOmg6X+bDHAhYAWgFuWvkliSHeBRE4AuIXTX40i7HNnvqv2VwYwSQzx87u6JhrJXQe'
    'c+S6fycEkMPoeavjq3qmy8ZTcxYKrZsb1SlBgy4+ClkCg72o55get4wyxSKlyy5fCaMCCIXavTzL2KSo'
    'zZeitoUOkqbEA/WM+hOCusrAs2s6l5b+6ucbvoPBN9yVhMjY/iBh7APjY4qpbmBpnFJU183GVOn8aHQD'
    'vejei2W/gr9lTiuWAZPdfjDbcP6uGLM1wa6bsi1zWf/oPmhna9in2V8RYMXn2QXUmAebagZLzeoAjrCq'
    'ebf3d3drMCDeACE8AN8THldIw2n/WUw1PDPLejvboYzTMLfHXRI8MGJmDELUrLU/4rpFpgqc9CmKTrWi'
    'B5yWGV5bZPbR31BHKhLh0SdqwEkXNOiFbBauhtmXXXdRFDJijwYdUQEW3cc='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
