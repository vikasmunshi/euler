#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 378: Triangle Triples.

Problem Statement:
    Let T(n) be the n-th triangle number, so T(n) = n(n + 1)/2.
    Let dT(n) be the number of divisors of T(n).
    E.g.: T(7) = 28 and dT(7) = 6.

    Let Tr(n) be the number of triples (i, j, k) such that 1 <= i < j < k <= n
    and dT(i) > dT(j) > dT(k).
    Tr(20) = 14, Tr(100) = 5772, and Tr(1000) = 11174776.

    Find Tr(60000000).
    Give the last 18 digits of your answer.

URL: https://projecteuler.net/problem=378
"""
from typing import Any

euler_problem: int = 378
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 20}, 'answer': None},
    {'category': 'dev', 'input': {'n': 100}, 'answer': None},
    {'category': 'main', 'input': {'n': 60000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000}, 'answer': None},
]
encrypted: str = (
    'QpulsFJgn1SucraUIdR8Rgf+0BB28LG5b9OKEbWtrcswH02n1mVPuogE0St+GSTfgdy3dU/zZMP3Sfow'
    '9k+iz6y7CFtIjEsJbgiIIpItxUP0Kum9W8d0cso+KcCZUAdJbm7wEzBW0yNq0a6bLI4gih+YV+cvYyuL'
    'dtTsRWq8duv3Z88yyzUh3LRDMhrq+uZeYxoAo0ZHd6jffwPI9FSx232BIRBi3T9akt6UTVLuAWIQp1n8'
    'kR0hqF0urAZi3+uH77zVzKxAtgRVuip2oOFef+5WQInitwfBOsJ94Azy8p0Oq97VWq6rw2pDQCrHhYNK'
    '76a4Uj1R0lWjNBpNgWdkcsOgnWkU7UsiWmRdOD2ND5eY8wcSPTwJpGzXnkyHrG1eFrXg6oyVf8XWwpGo'
    'xLY6JI0vqHvwOzwZ7xJRxJRus5H2ykuoECvHhdFmW39g+nKWtW3NthLWC+Em/Ws41aH5vb3r/oXAbEA9'
    'QXdoiwzHbRQAcmLmsggBULFMq9KZ6MObU/C1aBQSIHZkZzD2Vv2C/lVRS34VqnJo0HFkL7Xp2vmiQ/3H'
    '7w0JM4JPg+7SO7sqgaoREoZEPa2K4A+QXc3/a5XsHmduPT61MmoXVz98fvCAzAT5v2c6ikeGnCcgLlL3'
    'd3IKd1fDKwpnLHiv+Bygc9yEvdP5O1+ANGtYooyNtMXZVlqEx+vB9JSN4ho+W4PAI/M3S4pt/9nzitB/'
    'YLv3U9NUp5doq7ykdRkGJHYhkC6rb2qnkd2TCV6sBN8F2kyCU//KIXdu6YMlLVAFf0jfZfDVrnJqBm39'
    'O8OOZfWd1FSoyvfYPYmwPPjzseLRYqzi5EpDpchEsi+nqq88IXygPdumRFR46mf9pKZnDcFgi/e4TeJn'
    'sTiWJY0MH37jbNUcFw/MhqiFMYGCxQ0B9Y3bFzuFxxoq0cU9AN1RrkndgqUkKxzSOmwcNNsd2cSa5Asm'
    'FVEAlbw1tQgactgHxhGwkgftOSVjg9NUulbn2eXmvpE05AGIuOhtudrFtMqPWWj+pu6OKbONAsDXGtf1'
    'dI1JzuFEeAXYv/qcrRhvxQGHmjfLITOTaSZOWiGlHN/b29vbgc3AlJJnH8L6hx9B/dubqHswEgiyXF5E'
    'cEuuMXZMZfjaLk1iHa5dpUHB7xrtGBskOYqkUXJ0RoMZnzaiZ5T5n4yKXgtkMnjS6u6YYlYh1xXRUGzk'
    'wdCwvFl3zVVZIDIgI8h4BZqgqIdPESkLK9KPk5xT/iqkChkr/rGdQ6E356xbL6yaXL2A6EjnP0+7FvlB'
    'XYnU0e9S9/0aTZ3RdjmeSkZknxszj5Ede63tLIDP9LFu3yszqisI6HxT8+R2biQZ8MBFgIx2cecJ5Pi/'
    'dKvd838OP4/3A/03mRJcCLwec/ORPlsfGqa91vqca52/uCjVQ1bYQ7N63Y+Lv5K/9joOu1YzuQoab9Sf'
    'MDINnQiXZmWNn87KCji5LafT2GlmjJmyFAxUJCKcd3+g9cC3bYcKpX0IMtH4c6KWsJKMIGlqt4BZY+Ta'
    'sgWFsHuB2AqLPO0l9/am82X+GvDtRQ7AeK4JOc5CiC6jVCpck4RsWZW8EkD25YFbRl3MNlxn3Ul27XR8'
    'ZTqhGyK80mn8zJTwfn3hbscIMIJZeGz9kxnkFpoji8lBjs5/Pn47s6YFazF25hl58LVM2bWsIhjtzG9d'
    'Ee6nHy4fHegB9TFxNHATs1t1KiNKmVF1ahlKfpXefzC68yUwCj2c/+Lhzr/zBO4vbYOxbvpN2MVBLjqt'
    'p971Nzol4FE225RgARsnywzCdTWusnroT6L6hG1HiNbWJHz4Xg9TINv/dTZs31M0RnB4ph0G+2uF8ksJ'
    'llgPuHr0FZHNSV38uQVnvmaa9TqgsGSqvZTEul7u56yU7bYFEh5zCJ085QVpTx9tA3mJb4pFmq+ZFzHl'
    '9vTXE2XRek0LgijdwQbNr+VkxJR/fGVO+drtVWOr5LGKqk0rXuKAMFNLtr/ZVKxrlwuDpyJipu9MOF/e'
    '1uT4fbqJz8DR/ld0F4Q8mPgq0ekEMX2cNnYgXlsZgyKN/Ha33nmY6/q0sFltaW/lKW6Rt/1XGv+fWrKv'
    '22JAKBNUKyJSdV17j0X5naYSxXHcPOc2B4fU3iTkM+Z2aSqmZYbXrVbDASxcDxdkQcT/mbrV5NFZSpKT'
    'tpfpDMbVGhin4TZOxBgKjgIMBFNEcBJ53jSKiloyBPS9c3Fs/IGb3lXybjQZhKu4vINmgDUeV6uAGQlZ'
    'ZPeg2hVjTpHzc3P9sLBYRpDGy/oTOQ5uTpy/zT0qASra6UsSekXEITm/ofE7TEJ2KIFvOVVy1ahtoPUv'
    'kcjUzANNKaTY5BWIBKHvqQU+Or5p/0fvswQaw4RtkCzrcqQ35WTbsRReoipdz44Wpo1fAYu8/HtDJ9wX'
    '6D+7AmBPvb14HzoI/0I8yQT8nVwMoPRP8cW/eHbuFFc8KJw1/UFudYINrBPv6OWBHKm1ApTrlDF+z2qP'
    'AKY/2KZQBYPSQyuLB4ve7gu4rDpZ8dhveTW1iPCEnEdUSfMGONUjq2JVByWezY5hvGheVCqF11D8yyfr'
    'RqXWHNwc77ycKid0Yk8WaLOmqUf34ikNOBjfZR3OdMjnvs/hhC/ZWIy3yfhxw1m8mpLFUWI7Tt6xyFHa'
    'dckQ8tCNaBOpT/hlvoa2RfZI09xpQkm3v+Ih5Cbu4pmvUlxpUDJEcDiaxpFM01WebpFiMys16l6EvhZ/'
    '0+o4VKvUkFWwh5OuYBwxZSKwiemiAljxU9gesjFtwBD5OHSD7w6ANTBwqNzXJMuvzFLJi/u2+fY='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
