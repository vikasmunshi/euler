#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 757: Stealthy Numbers.

Problem Statement:
    A positive integer N is stealthy, if there exist positive integers a, b, c, d such
    that ab = cd = N and a + b = c + d + 1.
    For example, 36 = 4 × 9 = 6 × 6 is stealthy.

    You are also given that there are 2851 stealthy numbers not exceeding 10^6.

    How many stealthy numbers are there that don't exceed 10^14?

URL: https://projecteuler.net/problem=757
"""
from typing import Any

euler_problem: int = 757
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
]
encrypted: str = (
    'ASfopvUGVJEpUGP7HIQ/7/9JsNQi60XkwX6SyKfvT6rPlUwKS8FmcZfCcnIP063WW7S9A2QyZzWmhRJF'
    'pH8mHEeyTFWSEzH0Ijif9m6WwAFFr9JxJuvlb+/hbDmzqvK7/zec0TG8IcwapmDjQWmEqV/M8MD+U98E'
    'LWroJH8NY6TCl4jBQNtDI2AHGltAY1yVgW17EIH/u3JlU2hK0a9LNvFiLBvm3V9bG5dcxPKP7eU+zGAB'
    'SuA7ta93ELR6sqlySQC/IipMJZ/bFaukIeWgaWdinC6Yt4FPYnSJ6yxciIhONwftntsYpjeyI0U/X3rd'
    '2u7sIhf0GkxFcUGVsm4HayhSKLXaBZzLYRq5Y/ArcPtSVr3jA/lEzuoluVEJyRocU/SWAtN+UAYgl6Xr'
    '/3TQa0XJ9GvgY/KsxtIh87vgmzQtSZZ0iOMoVZ1mmn+XUG9dnellrDdgExo3XjTQWO4G9Yep7yZ5dai+'
    'tdr9EOvssS2nri4Wf2nBsTy4dlKVtx5VPEeENGkOgk0WNXcz8BfCWFMpJyEL0YDdHZAVm66K7a6v6iCC'
    'aKkkw9FnvB8r691NGJlZhjLXv8LXdpYnbgNMtM5zUkUQkbRlN1RRCzsW8/rkouX15b31SCYfMbq33zC7'
    'EEF0acIdC9hCjhKjdRlKU4eYmq4i/tDgRr4A7+Ez32/mz/TdcvkQij6j6/anrOvl5gK4CXQ5whHr0J5S'
    'NJhsCWs8x4J3m/xEa1z9jPM3/8KWj4N4slPfRLhjWA+tjxEr89xX1cIhpLUKb2DD0PuAMAM4i4rdfbba'
    'i96hj4C2qJ5mVujdqN63Td//4kTmLPj2GU5dLXe7UJLkWHl4TNzBIUNBXE+3piRzms6VC87q24QOIwlg'
    'oHHoe4OooHRBO7KQ6y1iZF0AXR1kwAX6Zc2chFzD9dCHMarnN0dF08kMBzjF3S8UIrO6/e2wPXko1zNf'
    'w9OS4HJu2xOuqrbslpl4M2Ciu9wyZNzayTg64JKVD/ZrpBihWZ6A7lHlDH2MLIH+7AGEz7XKXJpN57Ft'
    'A1D5S8eSNgm0oolzkKQeZFjzb22tqoMwSekT6RN7N+m4FMLHTb4HdKuWaIF6jeu6I/ny/9aeEztXQGFg'
    '7CsFNJKxe8wLFrM8+NdAVYE4fBTri6bfrYNuSRAhva2emSeIXKc8Ydn+PAWLl7l1/TWjnrQhq5q7UIhM'
    'UBaXsV3yj204sFl64E6JbOn/SghmDj3a35xoJQalNJrK17cGe2gdYT7dKbSMafCSU0xjmqokX91H+iAw'
    'sG7920jc3oh8lOCmKmQ5rH+EHttjzz6PQ2dGD1A5HUYiKv4sWidqZdtqsSc4ekadWQ/J3+G1QGEZX9nh'
    '9D/6f8ntgBWGWLsDjl9aSuYGOCPam0VgatTakXSor97r1kInoyVKTAV/k45r0TnQ45wg0qpODBpFqrB0'
    'UVGnQ/uRY/zzRiVplB9QV7sUhBPS0FnEPE/AIrlj7Cg8QifUdFe8TKaan3u0P+oBQk97wZ6olxeCMox4'
    'B1cdVSgjbp6V3x/RYJtswOCLtyzJq+58iH/nknxUSfrrvg6i1B4+S1yROId6U4o0PuN48mqKOWfqjhUr'
    'yxZzk+lpFVNw/Lvvk3nErrJLR2hG4laDmQX9F7vL9IhQ9SVuNygpkJ7n1AY87nAiAA5Zb+RhM9gEG2Ny'
    'N69sTImfedLYjSS27hqDcIzhKHizbzvbG5R1CGk1l1vA1eoLzt2i+wotBYFiHrV8scOKjujluRB2gl9n'
    'cUuNROIPXXomvOtFBFx4L/eaxOVkD65X1LZtwZx4NpEtFrYhDdurGAxPTfyuKk7XDsFeT5yMAAIIdk7/'
    'e3Vn5ykHBCu5wjwPwMmgwgCTU3ScdbGXsGIhnzCYax+tEzLHYLkpyhFM2dbStGxqOWLYlhwoUDQXl47r'
    '9erEmb6qq0CdOZVHEHDiXrJnLZUNx3oUwLsAsPUdPANXXx4pD9RwM2viLvkJ1pcZfQyh0SBU2eHUp3Sm'
    'Ri4EwA3iz+vbD8xZMYgHjuclfIHikruwsOR5BQ2U/2hwLipjQT/O4vAetnA1Dpbu6bdfZpi6RfZehMp3'
    '2XA4z0GG6+gtdoVPVkdjxsHcoIgtZxaUKylr+RHWfE6aAJooc0ftVayF1+md7pfEY47T4gSGYdEgefTk'
    '67VyTlzTAuk1WJvC70kTh/gDW5CYDEw24mu7VBLQCed0XSN0Kvn2CRWquhMmw3NwLJRPekHtjdDlrX80'
    'xnLFvG+OTNzVebuu6YveJHfyAZqLyFZmNiOSxpl1AZQar+BH1Pt3Sb1chUO3HVlXNjXePc7mUsUVWPpL'
    'XPN4zQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
