#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 561: Divisor Pairs.

Problem Statement:
    Let S(n) be the number of pairs (a,b) of distinct divisors of n such that a divides b.
    For n=6 we get the following pairs: (1,2), (1,3), (1,6), (2,6) and (3,6). So S(6)=5.
    Let p_m# be the product of the first m prime numbers, so p_2# = 2*3 = 6.
    Let E(m, n) be the highest integer k such that 2^k divides S((p_m#)^n).
    E(2,1) = 0 since 2^0 is the highest power of 2 that divides S(6)=5.
    Let Q(n)=∑_{i=1}^n E(904961, i)
    Q(8)=2714886.

    Evaluate Q(10^12).

URL: https://projecteuler.net/problem=561
"""
from typing import Any

euler_problem: int = 561
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 2, 'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'m': 904961, 'n': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '92HHWosEtbYBfWd6hAWhciKlIFYKzlmL23RmVvrFB2g5O4FK7G9Pr2Ihl7ygUc/w/P9GsSac0am/LmJv'
    'LJuSejywuLeOFs24bV/4fa5UKFz14xvdPGJNbI9v1AQ8+MJ/OMsiUUzmr8tEiYmTt87GpsXY5/8FXVdz'
    '7WkZDtKdJMWF7rn/idNU8DWrO6AIq5NsJVJKp/BieYjgD7dOI0Rc5e5RBehy8a24e7Zr1L9j7kPlvXPG'
    '9dIzE+he95qIYGoJY5FBZXsYECOyTRF87efWE/Phx9dkBb9Z6I04QZ+vQ5fALg75FJBGBzTIAIUm4nPX'
    '7ZxDFRj4DFQoLppATPGfPXaPoBBDXKBMhe0rJKgBgmx1GRxrX9YYIDt1A7w89NRF9BXASiX6duTE4yrb'
    '/CAQHoICqoBXIEZoW6LwF/THcp0jbazEQOEjB31pgwzqCyrF1qZ4tZH9zmSabT1LC+dbN2eJ4VIwA3iK'
    'NJEqAPvuyHwTDzYqjV5+zv7HPYhmGz/7N0bpHYIMyCD9+ujrRG+T1WKm1ldiv047Agtk8jl/7X2cVHlq'
    'uE+VVLDx9ie7PAgEIEeNDf6E3LYGvm3VSkJ+Yp6hWtf40bY5fDysdXsWtkDOSReiuU+q6Sh7rgqxrA09'
    'ikDmFEKXaXwZn7zCY9CU3dB1a6YKZdbuiqSliVEuzZOElEt3uc/9byAuTcajfepr0nlUzzU0d+iuEZmF'
    'q1ZAqj9tpjLeg+Nx29BlRKVK4CcHXn71XMNhKF4qGWBo0GHVf7MlBupfLSTF36hYO35TlyBp6Pxe2BIg'
    'D39WYnssJ9bzFlZ5K6V1lWtjqKcZ1UFM5ziLWGm8RvqhNZalgkgytB3bjgKiCWDCmtASrFMxuciSmgGp'
    'rrgsUmoWc9cEChfNZ4+O51tt8kgdOf7IqwZlbz79DYOczQftLLN2/pGQUf1E+Glq2tFHGLx8oWjcdOZB'
    'X1cD6Yw7l7bpRqmxw2p/6sxSQXf7+uFBqRTt7/O42ovSotfXMfpovWe8Zw8hM3L+mik/k9sijygXS2ny'
    'zvbraQxXRFSf9cTcR2Xn53Zt17Do/gYMwBXs4lb+USBEtJeJFvJp0kghUipy0VrpETl+ZqGXul2KOFQP'
    'dBqrbII8XYbNT8lYR3OHLbVZu6DrJBLUphaM9jZHrBGnCOKyxla1fhM7hc96I3KzIPJIXPcjVr/ul0OI'
    'njF3pqpWVlXxUXGi5ygE5iySPr8DMm4D4GdKUhrFY0t/+LBmPKIoXzHAF5ZXlCXHPeMLDfvNfAFzE7Gg'
    '8bx555vs8teu3jd7TcUKPOacOtTTLi1uFvMIXEo0L9vSsW8VFR9izTAajwmj0SuICwLGE+EE4E/8WLDd'
    'T6uoWdIaJHxpda/XjTjqECV1O75zQoXKTR+gK9BKNCj2lAY3KjzAqpkQr1gNy5Jx1zAXok5kNncdwc/A'
    'QUERcwL8baWwbWIkZTYcgujm628X5GkIOjcA8rtnuZDNNvSdzzqPiI56WiBgq1hQs1TNPgh6i1ejSkSf'
    'KfOjimFYQ+xt0tjv9DCBcnxeVun313o44xDucvDckEVjQwBDBvcG7u1F4vqWguZSyeC1YsM9eBVDYIte'
    'mt3Q/ubvajN7OR8nfNkPz+w+eR6B4U6iCIvnkdym1sdSpmYlCmQXAo45nmSf75W6CxSHB7uOrH6wGrH0'
    'PyU8LSJm3PNkB+23ZxEN+O+y2S2VMh9OOEnocDJXKFQAavzGxUTkpru05MUAqsCANiLx4QbqXhSmcvQ3'
    'G/kpegeHqmUdA8LsZbb82yBzBFQAm6F1QMIxdAm4bbxi05V0W9hZPthr6UnG8zbG7neJZ4BaEhO145vG'
    '/b9n5Qix+I0dQbVNyxRgNlwwNG2/qcx36so/9RcRPctouM/2w5okZNIvho3S6w4iObC95Vex9Y+WuVyc'
    'gqjzDCgTzlo6c3ZKKTN4j0bS7d1jvgDhteCT5g6UJGGJyQoZpnJeYM6V5TGb3QZ3ftBjfXfeBwPetx86'
    'xGylA3jGw9wuPO+6Fnsn8psolZ26WaC5nl1gx1pJE/3nZiFZcrg7JIY1lBY0bqs7EAkzfGqrhmcx6hVm'
    'akmtL2AeoJzSmpr4sAqEByYilrUV73WypO8OMevz0HOGv4EBocqmlw27TQ1nSigRFF5ZLwiY4eXwUd79'
    'ogcRWdstVx295XneHbZ0p2/YCT8qNc1w1wArsbBUpADKKhvIR35kzzCPaZupKAv3dyROpoYu9Xtkv0RC'
    'yUQJDqHdCjR+Ao4oXiAFqrqmEADS34boDcvT7xIKqgi105bKrtRVCEy2rcJeJ37N5oHuimsb9molIaan'
    '5D+qXD0h1A7Yn7TJnh6u9MHcjIBVbHyaeWb9mYmoGvgYm7ySKjUL/DZ1MsHQBEV9+/shSIJ57mUVQSz6'
    's1Vg0PuHVD69wVfAcwsdGxVVUWsANvVUbue+x89VAp28SaVQuNzDrbWv1Y2lLxJTohB+6a7TBq4bVJD0'
    'mdzYYW/961RaMY+yKmF1FcICRqPKLcQPFHVZ7mUjXInCq4ajdc73Azj7gCJtcHTDMfTFByuQ56b+bwWW'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
