#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 612: Friend Numbers.

Problem Statement:
    Let's call two numbers friend numbers if their representation in base 10 has at
    least one common digit. E.g. 1123 and 3981 are friend numbers.

    Let f(n) be the number of pairs (p, q) with 1 ≤ p < q < n such that p and q are
    friend numbers.
    f(100) = 1539.

    Find f(10^18) mod 1000267129.

URL: https://projecteuler.net/problem=612
"""
from typing import Any

euler_problem: int = 612
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    'i4VoiuO9MZOdbwHuzCubtI1O/QJ5LOY7alIsls1C9EC5/xxyrgP2CvcZbgmeGhyU6YHu44RG+R39KMWZ'
    '4nWYe1tDWPpzVCQoi9wAqagPTY0ga1j9K8JiYK5xi8Dx9CkNCVHzU7p/ZamkpVmxeCWU7iZwI9bE3mtt'
    '5r/ZxJ4aES0LdLOJcJNcbtrNX5UCt1ZxxHnIH5+CoZT6W3WbU8irgTrQX6+fhsS/enIAYluvLPqvDJK+'
    'H/zLntEh3uWEGYJ/XFllroCXtcvd7lNSIaUyHljfbdDP2tB4wdP6TnaIjkNLzsP0R9Y3AXz6AD7XZyao'
    'sRfEJisYez6B+SR4i4qhlCalGJOxcbxt2RFnBHRn6ehKbJajGdkO2EmZ6awra/LLKVoZZXVopHcbOSzS'
    '4rOQDkpGHw/icO6e9RMuc/VFeHvYgmJsLaHftdippf0r2zfhTLNF0JuJLNN+yKb3IaDTLCzYw1gn2/CL'
    '3FGYuBuDz7LoyY85ccO8Iah1KYOQc9WbzijsUu6nmzGx67Yv9hYhAAFTzpm9G9+iaO/BUaij4YG2GEr4'
    'fzPRZS4iSKoe9lRkCvqATbmArJaW2e0ckTEkeqJFPx70DkMg3u+l9V9VSAnPk4liHVd4yiTQeX5gfh5A'
    'QmS4HBCiNRHiQtAyj2M6y9Vpz59FWAnfp8ZCyMJUP724tFqjQtOOY9YWhRuuHnqmEfoqfdPFS2oVtq5d'
    't+ny3dg+ucTfLlPLkYXOyHVDC+q7cUkbEdeG4nmOHpqADoqd9aV7mmfm4gW75qEvqk/K4d8ygs0vEMBU'
    'jy9W67cTGdkU+Gv+EcyOQr4DAwDwjuoPRaSClMx6Gx7Kmxj0VEWhxphOvT+AJEKhSi28cYwCTzGQw7Ni'
    'Z8ABZpCyBsylw5zlUMhsNjnPEZcdE+DkxL40I7bjXJBVZzlec8q59qhq6PXCB0xB+amsi6Dv5t1SFWKb'
    '3KEKT7n1KZlgnd3WuOrdmKgtjIQx/E1IRcurnmSNNDyRylafCHCUsF+JHbeTxBlzHnxqMbcomQzE9iOz'
    'wqsY/XNa8fKWerwnHDvBzqPLjkkNMO3K/JeNETMQSyJWrO8pO5U+eZVm9ykvic//abSsSC++a3hRy8j8'
    'aJ5qUu/wSZ0lJEWj2YePullVmoUPeIhryQxwuwdar+VrxzZ1oqxS0pERfGbgTAiRpCw9EfVoqDyQZ6qx'
    'eiRLOIv+1djAxM0NvA6JceQhhAvpLzG7lJyhaRvwEcjFbkX9JzYi1lZS/VcqPrkxRrXrJaeD77x5Zvf5'
    'h8Xoj1x4dLNON6qKDU7LJERqaT4XdbPbTT1oiX7KcTqmn5b+Emcu95hjWFNlEhe/GcZ62Tt7ZnvfrAdK'
    'LjBmEFwM6tb86XtGDZmMb2fVGzO6HufXHY3WpdDOnnKVQjtQqFb6fiw2xvVsHdX0HE0Xswfd/+GTpYWi'
    'y/EqOKDjuevnpskZLMKbPSCqErDMnT41k4i2u5MpaD0zdcAaBvjIhHnRdv9MYibJmPxXcKAaGrmlLROJ'
    'DQpvtMOxACV+nofndcX2L5f46+5M7cEKI3alqppfIHTNYNhxu6Nn2qhOGVFM3pDCtLpmrKIfkS138otn'
    'lLS0beESSMNUJhddSHYEM8HDUIGob0vC9sTBosfMGMMnNeAsA8DPx7BDmhvTRTpsF1gpNcwQCSJiFhQp'
    '8nwGJWKiPJGxIpEKORUfP3gs8qmJA5etX0cWMjH9/TvrXLJcnRcV2O91FovUDlm60i3eAJLY+MAgeMwj'
    'J3m5nQ20Wn8NkReVFO3N+GpO28aabNqzhA5HdsqUB/4uEkYYTRtPqp+XoxC4lJC9kFmTX8A8b7K7ExZN'
    '80zCfUKxmhaD76H9Bc99+JTMkXeQ/q5+ntKDgaTrv2Ybx4648GXslwUHAuexVSqIrm2XKkbMxuvYOoBe'
    'Ypog1ra1evP8nbqMARBlMjomPKubf1W39tR1d8w87iuzkIJ12V3ngkSG926x9Dgp3s+VzPL1gLaIXmgU'
    '/CFZSTPsS4pdOHMlx4hgpwzZdIHuCT+N7o0OLYJ5+r5kdh63YEF2A0rbcIy05UGOv6v3ZT+7dBTYKFct'
    'ZJMoSJeuk0fB7Ku+mzpPxwu2TkYVuHqYD+NhwcSQxDeX+wREWQ9jwv7WXvp4YK9BZgEyg9IFPCVrnzSX'
    'y6KBbg6MOkOE/LdP'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
