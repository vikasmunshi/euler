#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 681: Maximal Area.

Problem Statement:
    Given positive integers a <= b <= c <= d, it may be possible to form quadrilaterals with
    edge lengths a, b, c, d (in any order). When this is the case, let M(a,b,c,d) denote the
    maximal area of such a quadrilateral.

    For example, M(2,2,3,3) = 6, attained e.g. by a 2x3 rectangle.

    Let SP(n) be the sum of a+b+c+d over all choices a <= b <= c <= d for which M(a,b,c,d)
    is a positive integer not exceeding n.

    SP(10) = 186 and SP(100) = 23238.

    Find SP(1,000,000).

URL: https://projecteuler.net/problem=681
"""
from typing import Any

euler_problem: int = 681
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    '1GK5mDJDXvoVgSMMDW0znjPo3K9OFgZNVwCk3iKldIM2mtgniz58btVxJHj2LlDPUGU6tT7og42I5sm0'
    '6JVTyeDJXX/GWofGwTwMD+EUb/J0K/XhJwnE4Jz2cqhXXdGpsJhIXPOoGj4Lo8JUE+dGy7sEv5wbRv/F'
    'qvUgJVeAMUCs5aRR1SXeP/j3o1wxvMsp7Ekorokg+u3vP/fFYdft6dMPHEK2Mc7mz+KJRTlIL4ROHqMv'
    'TD3N1xQPppBKDVNmDN1XhkuedaiwDw8NTDxt9pCTplg2IQzhfRV7bFhJXItakyY1Na8sal608vmX9AMh'
    'RLtH2gTnWWMlunweZsmViQypF1fwKfuC8t/hQJJod8WWmm2cPswZRnAkd0cjOGpsybLwAq2mcUkC9xoq'
    'MosLhVaLpWdpn13RmRBjzbbFBTif1B8ADPYVsONW2T93S6GTVJf3QXaAnPxHPWtKjS5XD2Vzo0DqSIW2'
    'BekiO+N9iuqjE6n9rOETD2hHwo/ie+a3xt8JlAYa3Va+Q5S/gvrlIbx98GC+DRExeQE6PLr19DHEpNvN'
    '1WhObijB+tCFy2vf6BvEqVSvVSWNZJj/t9KqIUcN0hIvxD+mIpTBOPVsDLA4jLWk4A64kJBKkBz6oUxd'
    '3o2plH2ktCGzlYXT71Uqhsp6E1CIOAd0dl/eGoH7rLTMCmAfuYMCEp1fqvbz/R8RaLkAhLLd+r5f1Tt7'
    'rBLGcBGpFrbLN3pZ92n0aZawfBMz5UiMp5ZLb0oVboLUe08CT6Cr8qFaEUaCxLNtonCLADktYdupcMFv'
    'IV+fDimhcvNkaNV9Oq45HOOno0Bd3pz/WLJP2yPz3tt8mFpbdhhYXLcl3Bu1szKcAUO7X/zpGhsWGjzv'
    'wdt78T6SXGl4gP5SITFEh3WgNT1EoKpKiK8lQNA3mczAgc6r6xhF/JgtNwmNImvIUgckxNAJgezZZ+3k'
    'R3RjixaK37eu4IzctpStgyI4bWbTS5HHUsMwJWZpInhbIBuBeccOUBqdiMjIhbinqVPM5TdMInN1j8PH'
    'MgScOXPcuCNX3S3rCvfaNC+a9S4daBFzmOvsJTJVnXtVXdQJM7fZs8qpxyTJCOSv+KSpJlmrYgVMSj3D'
    '7/gUzSz5W/obDT/5Tfs53F+rw4DWMZ9Kn6M4e8R0TPLiLkZZQom7nOZCENFgPXM9WY4fUwxsSSeOfwr8'
    'TJnEzaesdM85ib37iVz1j2rF2rgq9bbn0IDC5mQ3UlHGz0GMOZ78HBLf5NTA/gFFcBRaK5es4fxpHs3z'
    'Q9TNh6P2q7Cv2RdHTzTTN8ZN2Z/QxR71w9mNGqRgXBot80A4sOKDbyViwW712picQihnw5RHAvZk4D2t'
    'Gt8azE9By4stPhsK4jxyY9x+A+fy4b7l4yUceyHEXK0RqaultDLcg4eVQpO3zPZL3MlmRP7dLStXdzgy'
    'd9IOkvzJnMQStppzOiUT2iAFrdj8+PA9D2RNgEbi74lA+ZCKbMrg4izYAAEWdqq641m4nH5t/ZU6Z74h'
    'HBnApaQgADRbl/cHJbQ5P/OHOMzerHZ8n9+JSWNr4etL2zr64ifxDpEEc80xFu80VILy2H5eFGy5Hmk8'
    'AnIewbVvHhawopQHY5tjdWvpdfOzkTx1jnaPBzMTtLA+PZiA4C1oAROGthMypIEYIZv6M2UKpuytllxR'
    'Bo7+hmw7gwPCSqKxpOUXjYYJAuc0wqBzJtdC0ed/vnGXm0hiMG6/ztMTVpxiCwYqm3UWH8UaeZ7BXLux'
    'QZPQUFeIsl6EFNU2eIv98vkDeyhlI3WYv8i2UESRQw17aDsA5s0/dAoxlGmLM+hIHQ74tFKmFcMJ3fbK'
    'YsWH7WlRXCH0rtJR25zeBrnP8+emhVAg4IIKB45b+7w56RwktfR+rxIWhwpw+L9HKBSfnjOhvRVPXAqJ'
    'EmFtr8ojGyAaA7jrYqB1YzDotHskYN7Bg0QumfjTYa7nCeRMffFHJbQ86GOeGp4i5hIfqYezhXG77pv6'
    '6Y6GznD5rimeVg37PiK62Ze8aTL7pXuCzEtuxGk00QDssiSMZ2TvhXI6ddZPun71mkzR3OXgK24AlehM'
    'WWOx1Y7v9NSBLZaV/ky9NFwEpyfEgs4BI0ws6ZoQWCaFFiob28D3E/NPX4i1IEWII2QKY2psQ3m7uRE9'
    'C4Sf1/cXLuNteOrecR6O0HRaX6hme2pAsTTHgZcG2ZCxgwAMY2nJkLaxksonk0RLmtbbAQ9wLhwvX/GA'
    '+IZhaFrMPVcxc3GxwMhX6xu917EBux9GRd0oPdU0MNjAi4FMjvXH8jqaqOVypIvNSkZpVdNTRqgo+C3q'
    'Z5XtOPSug6QUjVUFalJassIrrmTORaYD+kvmLma0nFrTzs+7aMANXlywt7VhYe1dJR7pEfrMd0hmKihj'
    'jye+oZmQ4/7JDPJv9AAVPJhCGkbJEvjJBrNykI4ju5/+dmwVRJWlsHBMD3HDVqcTFDpL7SL9rfrflA21'
    '7tZaYw3tO0oYwH4GEr91MPorkO0dzBfFLO7MzQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
