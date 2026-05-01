#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 820: Nth Digit of Reciprocals.

Problem Statement:
    Let d_n(x) be the nth decimal digit of the fractional part of x, or 0 if the fractional
    part has fewer than n digits.

    For example:
        d_7(1) = d_7(1/2) = d_7(1/4) = d_7(1/5) = 0
        d_7(1/3) = 3 since 1/3 = 0.3333333...
        d_7(1/6) = 6 since 1/6 = 0.1666666...
        d_7(1/7) = 1 since 1/7 = 0.1428571...

    Let S(n) = sum from k=1 to n of d_n(1/k).

    You are given:
        S(7) = 0 + 0 + 3 + 0 + 0 + 6 + 1 = 10
        S(100) = 418

    Find S(10^7).

URL: https://projecteuler.net/problem=820
"""
from typing import Any

euler_problem: int = 820
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 7}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    'wOji9iFQxRxqIlAGm49qU1JCsEdwo7Yrfx5HxC2HS16Z3kKBVgJF1dumXZ04TDsUwBucjXgM8s7xIeEA'
    'JatH7UFEuXHtmPqelTnlxj62e9xAqU+l9aHGa5P7Cf2wJvUeo1GjlgiVpcgNNGxvnxx/1QkyW/xi1ElD'
    'aWjLBMaUM8+dJcC29PyUq00tCQ3rooCi7d13ydzYYKFiWuXwV7rklSLUbgnjqoObHPZyHPcHKuJpX3vR'
    'Ki5IJjqFZ8Sj58yn79yvhBvmCZDnKVU6oz6hDLQ1jHtRxCoKY6ep32lUhMVVWsACKiG3C9urE9JS+4sR'
    'cvMtkNz/nT92sHB7wiux/lo5RltL8f//aqCRMlq2ei6L0UhqzeJAVVz/xjJB7ZGMwo38xjZwRkWQETG4'
    'sedKi3W4pcyqPIR41XSiQOteDRBmgE9mLP16mTiQsgfe1aXQ+71LZH28ih3IIuaxqf5C0r/s9IuYvpwl'
    'FV1Kf8ipkUBvUS/gHjHsCvIM1QLFh2AxDkR7htF/mnfY3x9IUc4N4jSuPM84i3UxCgiFYztdLW8TSttQ'
    'mL4cJc+sI5bhfsWOaMz0WvROp2/NcUOSfgy3PDF97GooDnxl9zP3cxPnlaUx5ZwtJlr3dFc5tlAEsdvy'
    'ro+CwxO205dKRu+lu0izmhzjkKb1eK2x3knEiC3gT3CHX3UPxjoOyX9tsu/f2KFNFQXXDzs7jifR9Vjz'
    'aPmDtG9T+e++Y9wxwPJ8w2xb5MzSInyqJgoTRoraAlUg9BCIO9hCPzekb53tQ/2hnBGwkr2xqAIyGpQt'
    'JmK6eSkUYcHKLduFKfAtFCbQIBCG8nGupJa/e3HsukMln1xry2vEcyEGpPtii5Fx/AyFHZciJvfuVu9h'
    'C2VtlKwUlBsuVuWFno9kHwqOiMyKyFPE4fma/M03v8EeXR28gpIPBWXtcoVyLEWaCyv3khLQks0Cey02'
    'eV32cIgjN3H5hW133XwMDigs7v0M30natt5OZfXWIswvUhIduDZAVb+qTC4Ack41hr+SyV0PIWOXFavM'
    'B5kdlZak8H+03zGTegpwc5JCPbNzOzcdT8L3bzkc3iXDv/rvXnNrOUtIbEkEbkobV00NIfxJ0kSvQSCK'
    'QmJ6ltX/KbuMsdfByy4hCmzNSmD9DdipohjqFDyLroCImkVj+qiM08D7WZhG+NdjGhGe9WZAv1LTckat'
    '2t9G5hj5fCkWiPNf3GqkZeLd6u5T99olS5UGMQ6t8l6mqB8iLTVz4xOjYGzHW+T1eZ0VkjCRE0N8blsd'
    'Y0YzE8syexHwtXqwnjj9Hw34LshE7e91W1RPSwhW2mwSiXBeZstVgCO8qhrXqPQ9iEcXK9gEp+5+8imF'
    'X5xURXguJ5xDwPlbt3Lm0F0pQas3XVujfuUFTJZfdHaxZ1DTT/vbe6ZmPN7YJ+DQtsjPvJpbdsj2JXrR'
    'iVupjH8WufaMYp72+O4+NWsH+phE74kGmnqHSAzqQHAfZyyc2iJMJn6w8OxpnhZgjxbSuSce9/s5mzQT'
    'rIb+xLAPilQGAoWmGVTmvetSis+RPcJ1duwnvk7YvNA8gN9xvW6VZca7pxOu1sjWOjsNie3sHpgJEh8W'
    'SMtfl6yaqgehuxGfG1Q7mcEdXGVpk1/N1KULEsgzJjNnGg46CNaeHJ46cVt6xXh+uLf+QGoDIHGO+Ugk'
    'yjrDL8V0fLlSoUx1iZAdrdRys4E6Zp0Ff3qJFZJCH0iJu1DBe5qLFwqFiXpckiaY+As/qJGyDAj1zO7x'
    'Ibm7LV8WrupNVLQCVARTQrWE0hvGhl8vOnF+D50pQe7qUzhJ6FuuBTln8r0Yq2LChR/D7QGDGRX1sc7B'
    'PgTBZiSXfZNgCclpcnpC8hu1plfgjAhmFZXJhrtSgrgmjRa/m0iUVw1+Y/XPnImsSnV9Pk/BoKZmBmhX'
    'XHCKkETBF9b71DpfpCfyz43Xuh57WST+W5duDCMCLJNdsMI+JvNzZ/+C7NBJ/5ItWk0uX0hQmU9ind+1'
    'm5OJY0Q4Jvl9VlOp5AEJCVHQvwXSh9h4Q9C9+u6gFcVoEOlAeSvuFpNxl9zUJmdvWp1gpzrdDNXHHpgw'
    'DHbKUflxFrxD26ROwGzqgjxa5nQcQnPS6PZsgzAcHefCbp6QWnoXaJR9LbAF5ZEtpvGGICWJg5B/gFPu'
    'xIAQflbz2WVXagbmwfYmVWPfbRfHzfBkUF3DaWKJzPPg09Gpk4aeYXQo6gaKDx9XW0w8H7qyDlJaXski'
    'sduF6mv88y/v0KQGcoldLq/LcEYvybszhPzIfRfDyUWKburY7uxtPi3Pl6WJN6x6gDUdhyFJW0GBpViH'
    '/kGTQ2xZjZ3g64bT1qn3srCsRYBs6gH9ua7E+F4Gwp7Lgd0EpACPElSlKo0nX2OzcsKlLG/3mMovGmyU'
    'YZatq1kuJpWpApLVAKeKGZ55aH4kihyee74fhJnzquRnRvF85pSeQNaIJs69JdS/TVWhx8hXihAodz4u'
    'JXAYf9KnawGHL8s9'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
