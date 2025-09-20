#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 593: Fleeting Medians.

Problem Statement:
    We define two sequences S = {S(1), S(2), ..., S(n)} and S_2 = {S_2(1), S_2(2), ..., S_2(n)}:

    S(k) = (p_k)^k mod 10007 where p_k is the k-th prime number.

    S_2(k) = S(k) + S(floor(k/10000) + 1) where floor(·) denotes the floor function.

    Then let M(i, j) be the median of elements S_2(i) through S_2(j), inclusive.
    For example, M(1, 10) = 2021.5 and M(10^2, 10^3) = 4715.0.

    Let F(n, k) = sum_{i=1}^{n-k+1} M(i, i + k - 1).
    For example, F(100, 10) = 463628.5 and F(10^5, 10^4) = 675348207.5.

    Find F(10^7, 10^5). If the sum is not an integer, use .5 to denote a half. Otherwise, use .0
    instead.

URL: https://projecteuler.net/problem=593
"""
from typing import Any

euler_problem: int = 593
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 100, 'k': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000, 'k': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000000, 'k': 10000}, 'answer': None},
]
encrypted: str = (
    'mNnN1jUWtl4m6sLYGq37O1lAJyInQ7dIUz6lIOvtWAhPhOrnoNeGjhdb7mg97L+zR5omYcKjlGHumPPD'
    'VkbjQhn7vEfhojlt3znMlSu04rIqtDNgkmvhjFujDpO0te42VQujN8UVkzgO9q+yToPw64L5xLQT5Rjc'
    'PfCpBoZZMPkCd8h34upb4cvZ19aok3Kxx/pKPggLMcmKBgFnQt85d9A5Q8lv6LlO12d3aNCrQ4wgI8lJ'
    '4LZvyfb+Ad7KbGzRQjeT7ZQEVqPhcKp+e42OHAZC7YsuQBkr2/Rj+m66QN0Za5l9xpaFbEo2g3n2QUHQ'
    'Pq1Q5uJBxENPqpmnfwBTY2IOwI4Xkzpa6/weYIg9yjeAwGtlm1eNL/ZNCI48HQqlyZ81lwlw/W4FVazV'
    'WSZo/gQ1oG1LWYqwvtHD7BX6vD1AepyNgNXTrAHmpJEHybEmYp19XQjGPGEGZm0GmjgavX7huoJ0OJyb'
    'OrlV4fVAAa0XHN7CnN8izuaVaPe7avQkjaaXblCzGfNxT/upgUVqK5igm7wT90zW/b2/zA4h3XBz+LyG'
    'FPEPBoRND3QDJXJcWb29++1dDKMqTf74G3PoV88VTB8ERYQg97Xt7qhAV0EOQTnzPZdMV/QTiQEHMEdS'
    'l+gvyyiczatOwujioiwRWaqcrbS80lLCeaCW1gSkaCD8i9VoPU3POYN/bqHbTcfTMVQVJuTC1G1/MgqQ'
    'b/JR8SV4vyfkDMBTbPjceP7clfuObcwheBbXA2cAjJ+QvZakESBCa0pSdIMBP4/wHLTr+kBT2Lq4hF4W'
    '0rgxYmC5SCmQKMBPtbmKmuG/AwurVIguIIVVDBXuLt29gz/BFvkp30PgawGYauslUPTJcjW4b7AuQPXw'
    '/Td5PXXN3YhBs7zM9wceMAWTuoDDFZRoc4RaDqJ4BlBg4usjZSXx81CAAlONdJ3I0bdsNizs/r2H6/1E'
    'E9mNN1ljm3XN8QPeohEnarEBSUqbctlnftGIpkbN9QzGQFcf3n0SB1Hw6WOy+bmIJRSC31dKJ2McFlPG'
    'AmbDmS2KdRt2Tc09qr8PohJfehBGRGw5ztNvxnRJUBN2u+umxb/eWdEJ9LdiloNIGqjEW1ptNk8sxVwK'
    '4g2JTlApxnq5LOrqdCKZLgg8mhIoMcek4auM2QJMKl94eAEhixGCZjuL1b0X3nL43j9SBuf5R9Tj1YBi'
    'kug3vIYXG0yMkMGXaeL0CT37YURYZxNr6PputgSMoehmyPZm8a8ljOTFHJpGmnpKgEgDoyGGhfJxGjX4'
    'e7sOqKZIO6mlV8H09GcqcOT8vrjcCIVqZjGBpxG9keFw/pkPQ54Bg/8RKnKQC/aCcKxDZLCJNcdFNx96'
    'a45XFejtlDf/X/iFmxWbvob42sFU2sYMMAmlskLUM/dC4iNsxZKvsKAIj3dZSkS00d/71hpriXyM2vJq'
    '3tPecKy0/MzgFVpzbM8FXRsHXTlMdgtKR0vpi8sj/G15VLUt5psyqptL9juz/dT+VmC2dLb1CueIlDCv'
    'DriY46pm7zjS5H0b+GcWulW2Kws/9EhoxX/JBKGtFSpdwskH0EfLFta2po1gj/FUW902yyg1cmMRdA+O'
    'hn+NGBBWk8/1z2nrEZwpUT4+lKKF09Vhxevrq5IRHysrV4XrUBxTK90gPGbQTbNa26UyxlwiMX6gw7IG'
    'OVBDqFGaBRmJpdDjPe0o32ysY3c7qTtuXL9g0K2BHoCS6jBwNm6iofgYxcPES5uhjkXN5KE3NYXECruT'
    'fnM1adyiJXhkJfk4ul4FS0w9Cc4sLZcAfO0q3hsxikQZ0vLvNVU9L5cjTSHBAN/pS5xeSCXNgErlQFLp'
    'vXjbyk1ThybFVwr6r3ZgeXzoTA1f8HsQHnDSQyt2gYPWfXTIejoE5+ODT9xYYxtq6ZUbqDBvwcUBhInK'
    'SJBEFgu6b+HDHjGwkR9j8wqq47hAX6YdPRPgAGSJ6iw13N2rgOj2H4yCUpmgyEABDiBmy2Fnq6sE1ENM'
    'iu9v3IHE8GUo4xyWqJcNf45WM873Me/eOlKcW5xvGKmSnq/TCo/PcFW6wEIAO5+2DtJBZS1T+BvDurth'
    'KY7jFwsE/ZQUJRJYAFao1rwahemSgXlF2aCbttGjjfleaoZWBel3dsXpCMYV63bS4Ulx7QUvheCNeNyO'
    '11Y1JYFhMeKNdjEjNjIxrGgOBjXon6ljQxRy7dWDPOC3kaQJ0UiM/Quuco4YE2MWgtuVx/xLHBZkaoZC'
    'q1f8vLnMeFmp+/v2TWzSPAuEwQowcr/mB1uOh/Ve6faBOGRzbT35a391sl8yzO4lFZnfwww1FFDpPtlG'
    'IYytCZZ9drSsy8IxdonMfdRXfUIOdI1cyY1ZE2d5W6e3ea1T2C00SoB3CR4m6uQxiAvcKpPyYSVRGqEs'
    'pU6VcVTOgDxnDJjZGXLNXi+dtGyC1HOLYmfFa6qxCIwbUH0Fs3G5yg3ENuqW7n+Nx8iyZtT5yxmH+jxy'
    'RdbYWc3NcTXCjZXbZXUaZS8gvKgX6MyYWNk7SpTS3ybfc79O3V/KLz6zGFZWpPwWD0PWDeFla2IXgGFe'
    'sqLCJY2Ael81g/a7cpMzTqDeR6qy8orXaICmd8xXWvP2o2pJG2U63zLZNYcGhmzYlGkSUgSQFSNhBCLV'
    'sb0h/Uh/dpTYrVWYdfCwEHydRughVGOnXvQ7HAhGBbm8Kd7W0W/WPLei1J+aQWjXg8YeQGL8YddoUc5X'
    'hCozP/H14b8NIE6gAd/9E3kePPVDv6ojkL9L37RTzi9165RGcGD/+nCYS+V6k/2XaIE6rF/TwAY2df3L'
    '0DVHNonGiGFwxmcO3uT2bsCo0XjP1e2r6dHW4OIee4e2t3s48yXGkRq0MvPf/U7mLL9stp9Wn7xL55Kd'
    'i4PHmz4jbg4c9XNwwLnAXKEtw7fNEVVjYDRS6asMBTkvEtGuTaVU6zwlEVZ21tDsseNJhfA1UE7vrgBO'
    'skqmvQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
