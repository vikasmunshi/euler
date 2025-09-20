#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 274: Divisibility Multipliers.

Problem Statement:
    For each integer p > 1 coprime to 10 there is a positive divisibility
    multiplier m < p which preserves divisibility by p for the following
    function on any positive integer, n:

    f(n) = (all but the last digit of n) + (the last digit of n) * m.

    That is, if m is the divisibility multiplier for p, then f(n) is
    divisible by p if and only if n is divisible by p.

    When n is much larger than p, f(n) will be less than n and repeated
    application of f provides a multiplicative divisibility test for p.

    For example, the divisibility multiplier for 113 is 34.

    f(76275) = 7627 + 5 * 34 = 7797: 76275 and 7797 are both divisible by 113.
    f(12345) = 1234 + 5 * 34 = 1404: 12345 and 1404 are both not divisible
    by 113.

    The sum of the divisibility multipliers for the primes that are coprime
    to 10 and less than 1000 is 39517. What is the sum of the divisibility
    multipliers for the primes that are coprime to 10 and less than 10^7?

URL: https://projecteuler.net/problem=274
"""
from typing import Any

euler_problem: int = 274
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000}, 'answer': None},
]
encrypted: str = (
    'i8xFi1OEQ63DdHyFVu4M5azNkqX45SCYZLPcQXWF3Afpt4r5Q7CQwfwfrgTW9RS/Wjy/SKGOalNvogxD'
    '7HrneCGh8vxXXjxjqel8p6a9Cxu8LSeP6aElM3vfSiSbjQTDHj6acY8jyc12pzPCeL85wxYdVmfluSko'
    '/fRLu4CUCgG8NYlE+QixRDYA1ef05K8Auw6VFcqWRNVYN+T3y8aCREoXtsmh1yWlU5LY2HYCoRz2YsE1'
    'Ref/FIuoyfi7mnFjZ0WX9DBBq9BGxoUNsU320vli1W4KxzJpkM6/4kGonHwdTdrRL0lJ9GDJTu+f1TMu'
    'cK8rGfXcsMA1FvAf/K+tMlpmYWTc3MU6ce1ZRYWZBOpvAj4eCwQhcIgUr9B0+wT1KPvirct8bZR4JPwZ'
    'ASVI5NVM3nJ+8+NpR90l1MH4FraJsDiKSSWKyjJCk03ujx2PTlaeW8QmOIHbMtoeXYS//OiOX8Q6W7nV'
    'X+/tw92SZQf0KB3Rnh4bBmt0YDabTuRNzrt79y1b4SnBvG+nbc2b5PiQmmCeYXXdv1i/XdkspU4CIadg'
    '6008nNdwLjZDc0r4pRQCwHaC/xA/QM4XW5Ob7N+31w3CaZ4T8uMr8s1aYCIo7zxjfRI9CFTHYuvbs4sf'
    '3ww1/j2pslouI5afrRfiaShJwPdZkdAxTardnwN8qUGayXycbY3oUkU82BhIYwTNu7PkT1iagToOmV7+'
    'SAfGBTwD6LrCalQFtIOAPetXrqc3bPt1ZQ+zQgK5AAjea2LQxZHpv9LVHnQ5n0EYJawelBvyoQ3WVbnj'
    'ncRgD7WvyMlWbKjX9qEEDYT2AkEUB19GykgO+sONlw5T0GL4KW076gPbiXRScIOLWR3v4ZQEMI1fU7nm'
    '/TXVAt76GDapgXrwUqvTW6In/02rF4FRTWBoo7iHdCZ3rxc26rg+rxQsnxSNKaueQXL9EHnQu1dYHOPv'
    'ZdyIFhWrPkKQcrdixzi5oZLwG8jp7BmYZM4clIkfZg7NJkLDrIgWnLI6x1MnL/5edK8IjLEeRAM4paj4'
    'vgBph7q5wQV3CAnAeBP5syWELLLdvKL7uTrp3g5VuCijioSS9WDag/bqNJRKV5hdYXjE9ePtmFytW64Q'
    'HhsuZnuEnZDftouBUhkoB0buS1RL+zjxDz2TxYsvreRJxkeLncw4UOalFUWHC6PeLjGx5+INshSkDyIF'
    '6P72ivgBhI2dpuBGNyqK9rvayfl81a6A7ggDOisk9333zHwDcysqT62YwzrjQ++Wb75ByHti/F0kXb/t'
    'dXGelLM7vdE7NdgUHAbawRRAsWhTRYfep4yWr2T55PcUh1ZB1hGSdz1y3Bvp7SV9bAe3BC+p02cOvuaA'
    'roolGJW09sP5I7rN9H54nQOKxV6zjAQxpQCsqt6cq/EnpVzjDfAIIDBvXjL3BcdHfWOLW6j5TkfJQSik'
    'dd24emLJyXPjsklDoqQLmwvroL2cQlUVod28kSWa4UlYrdccJmzzYf9YtUzytOX4OxEr6q83hhCJ9KfL'
    '93fSv/11TlXM76RY7RNC1GWeZr1jDcGqJ0J5ig3mAmor0JRBpM1yHRLOGRk1ZphwUrc1pJ4F2Np14c9h'
    '+VcrE1WJshhC011U76oufIxbSZSvlldSJtConyYj9vMAQHVQ1peTQ8Q2eeF+6Jt6wyAiaxzdodmsgZRH'
    'HgVlNHQiSB3fZqeFxMDqmq4uFv6jdO5sUwYKyMz2F4NLAzOLor8tHaGbi7ALFlEvoBq1I03ywZAOnbd4'
    '0qKeYbAWwmmwjZPnaeowzGDehDFwv4UzbZ5/hoYNXJMe92BpkF+Z3f9nYtkGKCzdvuKTTjeurorf8+7e'
    'cdpYmWlZjYQy3/5yxZXIIFdm7HWxCA+wvmJdZBBR3w7o6r0LHOF3reCPggieoteXVVzYxU1lXk0vru/F'
    'wRzB8jC/Fi8gm4yYrClKHoRkdy6tH+Jp6cIk/0V7vn9EduV1HtU9yDPcDWOfGG55N4MgKg4LfOJ7hpGt'
    'RmALC7YQho9hgG2bBrl9m1csVCvlmXnIh8vHkUYIHFix0KI2BqACA8aXbWNJjGZCmRHcwt6BIppphVsp'
    'v82JeYyqLmG/cGoIMtOZn9EDQabQJMrM4wRjf0LmPdEzpwLaq3+GUnW2YvyIiiwUWXsI4sETSBb2Imiw'
    'UnIGUvwk6Zzl990Y8h1wK86oDsCvmqJjsCqlZKN94UUrDFrRQ9/5zpgQw9+WP8y9BY686QXw6mlIDt8z'
    'dGU/GakjWLo2CXWdQyin0e3gnPqitUKjyZ5MRK739MsuVTtuwGebfOPgAarIXbh2bGLtNWOWypRQK0G3'
    '9FZyu/qU6ZT2hFE50BDqemsOV25e599nLc3Pu20KpS+og17eNNLKG7XO7QMzn8CDLQdNeSK4O6JGdTbi'
    'jGrlEYsSIeVmcNFav6NKVZXkrPsdtAq3/8hQX8v90DnjI3C24onFu9atKVlnHr1oB/HOhDOy5DFkv6Nq'
    'xCwSdin2p/ukF1bjoHBqnDSAIVWPScw0l4uLczCuSKLTG+LuqL0GG5Y7MOXKrDMh88Bq2fsBOuxSEsvD'
    'IYeJyFmcpxazdALisvbdO+ll8xyTdbwdCr3CLAIEktRRuQGSbKhjUu0Q5wwm3oO6hqXPhZd6OpRKTSY4'
    'w7gBIi7TMkZsJ+sunf64JIYDBXi721Kylg69NQxPD9Fy/ZfZl0fLCUMV5Ie6cKoEwkvmIb/Hj5vGYKh8'
    'qfcasW5I7Two3WaIDqegOSElDV4JJwSoGxQG3ptOr1AJ7tQ6kj2RaLdQvrRubhUA03imrF8dvew625no'
    'sMOzWSH5uyHAbtSGOhuKqIWyT9ogTEQ8Wi68BLEiCI1kV4NLJ1w5EFyHrXSQTlk95G+huJ7nS532KtYH'
    'mAMdyFtslV6PTJggaLpinXOfPDdvESuTu0vfNAwPVbWFsAbPoGsCNcQN2jXmxVi++IpVw4zJZdADUdN/'
    'PlQPJja9QL8XPQE0YTLO5431Rf6jhHZqOU51SRnOWtWNnUYeXyPR8dxOv5mtB2OUO/1Y6lRDQhihyOca'
    'Vh78ZJkdO1Cl8kezc8Mv//XEFGj5BhEUHh7GSj197xvB/PePLIFmb1Qaz6SSxnbWO58UneG4IhO1acQm'
    'rygy/3khn/xChnsDDtC5npjBJyESwJ7L59eXDxjMVwYQiyoLSQVLiCzJ1RRycngZATzi3xhQGykyNH5P'
    '4P1W09fMux3XWbdFoNhc8hUoP7SBieupuG5utV9N5wji2XsHcCAmqv/K94Zvu3YzWrkOlE4zcUW9leay'
    'PKNCdJyYvKxqPGhSxY6yznjSAKVQnsiK5aD+l7b9MYAdK1MgPjE4W9CL+t8L7zNus4qkUFTQwuXzW+cz'
    'nXb8U05zKPdL5yNDOd7PJZB/9/Amp2r79rFxzwMe4qHg74ukzQFbgcsMdHaLmpCBHlhRvrZN+xV1l4tA'
    'wBGKoF0ujWQyYDvhsu1pVjjUH81Tvf6VV8Sk4aGasFjplSeNQeEqTHqGuSSB3+B9QmZ8mv+YTgRGbd02'
    '5Bs/hWlcsHRJNjG4CM9Qh2P9yAYWmzFzPXd3EC7sSUOSST9+0/LijpuwhSUjv9IDiBlxIow3IAhjvvrV'
    'r/OqWW16oG7ClzUifL1MHJdu2hyEZDBlVkCIzxcP64lXDrn49obhXbr3xjsYs7K/y4w9Z4rsrVoReG+j'
    'ITEsMIXbkeM='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
