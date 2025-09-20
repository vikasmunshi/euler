#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 517: A Real Recursion.

Problem Statement:
    For every real number a > 1 is given the sequence g_a by:
    g_a(x) = 1 for x < a
    g_a(x) = g_a(x-1) + g_a(x-a) for x >= a

    G(n) = g_sqrt(n)(n)
    G(90) = 7564511.

    Find the sum of G(p) for p prime and 10000000 < p < 10010000.
    Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=517
"""
from typing import Any

euler_problem: int = 517
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'start': 10, 'end': 20}, 'answer': None},
    {'category': 'main', 'input': {'start': 10000001, 'end': 10010000}, 'answer': None},
]
encrypted: str = (
    '1neTVZSkYpzQ+Tjb+nT8xaP+hgKyLBUrlOqb1gzwD8NbP7dykcBOYBfW+RhZatNzn1S0ScfPChspXQuq'
    'yJQl9yiDYhPEnG6XzpqUv2Pevy0nB8q4uIhUUR2fo+7HVmi5am5gSUKC3FbafI606RYt3Z5EO64MUOj6'
    'IxWpwPXLmdVwg/0sG6WvMkrFTrZAoTdI3H5+OSm78khb8Dmsaeyc3zQY/ZN+5Su4yDSuaYcqYe6tnlSP'
    'MybIQOaCkGj5+oeLAvWvTEUvEtRsOa3hXzdYP0lhdDadMo4nEPh+01PKoT1E/hpSwAbKEp5fSv+KDAhz'
    'BDm4ITbsL+BAtVIqGbJgckdpHRSV3EU0BviJJajFqBpTP9hj4JPi1tFt5b6QxJ//iI5WEz3tgnWvBxFl'
    'N8qi/rZSDLB2g2uKTEPwzUo/P67zJdPbhCd8YzRmeV9xmX4TMbBSx39SZVaDYNVpNoJHObMKOW64WeMx'
    'oZwI+BZKiHFynfsOmttpNcllCCLz3ahfVru+WxPujYQDfelb2boE+lCqnVkCvvjfqOQ05qxSgL1E9o+w'
    '6NUaklCvnpa3og4YwUKqkIUuhPxUgpQko7kyliaOaeqbAihepjrq0XIMqvLHib/c4hRmC5bnrNI6tJ1n'
    'P0bp/ATRDuGBgYDPZQsD17D6wtRfe9JIwWtn4R843YjBrDkn7dA4xkSj0FESF13yLIs1O+6+Ol4Bmsiy'
    'v88TfA65+b7878YO6oqfGpzIzX3pHXQquuHG1s8PhWaCHQDYoaAQ46ag4C1cwCOv3e2G9oLrefKhs6Oh'
    'yqP+h4TIJDJtERGYH+3/Ob4DnV8LK52AXTyZtKEPA2SUuoVlFsjDy66H6edfo8jarnz4UO7f+hzCVN24'
    'Nvl8sm2vMWimGR8rx+p2FO8aJTU7ba8LO3nTREiHizePn5cO6ZnNibUt/L0fmR2uOVYakZZExht8LxhB'
    'DfgfLODpzv6mqf7nGiLb1m1q7cdz/1bDp2AR5z7GVCuS94Io8pEMY0GqLwWSMckPQnn6tkp29gv6bWaP'
    'JNI2L3aGZDKN6BOq4aMorxtBf+sICLwFKdwocisxpcNUdg+hu2Hn5c4vBWBssA3SJvwqwDgslQR+QkWL'
    'ycWqEc67mcj9qdr/F8P4j7zS4Z4n9fcDyx5bHiZv70JOD++oN+SgA1L7iLHv7iwmJlxOeVHv3UDRAINC'
    'wUE7me4jE9wjAzrMjFv3aCJvklbW1LJm1t1munmjGXgGPdSu1wKCXT1GtEE/8FwqdJOyhBikJuhEiQzc'
    'jYPpQR1pFMjv1+qAMmb+ZlLT/SONaW0S1zGdpqfzARBZMNvc6KOKPVmgxwns/jQF0318C8at5llQQosS'
    'E9OoalYPVdYtKLJwBZ4SKEraYQcBhDso0PkDeXAbmlg+TRy7O/gqOM5Z4oyJxDQntCRXeBg4Ahbkg0iC'
    'HaG8+M2STGovNYcfmFtjJUfwoHvzDvdy70VpJRsBr1S2zpuV0LQt34pPm5m6/GpsZi+mphpjE6FOY3vG'
    'dcke7gzppS1fonJ8/oe3XVE3YLVH+ElJMuK26nfvEpE1qORc5M8DZSKvPZMcNkL0pGJ2mLQOVcre1+aP'
    'E5CMISgSPLoCor4KqoNmV3MH8im9i9EltFQkjyob9xcqloD0Jr/KGPUBAeTmWZEtOdljD2WFAaxMYtE3'
    'uSJC70XgcqjiK6Ia7WgjlaR6eHVaXNIZ8BwGmVx29D7nOey7K+qBbVp9lZ8eoG0L9ccS+ZWpK6Y7PnOm'
    'we1iM9qZ9EaplgTZMT7K6JW1FKDqiDjkgB8W0LXW2fIhjTBldQdMnVuhGma+B9jILiJgI91TPimUYn0a'
    'm/Jdl3mqow9BT68lrpcYzI3yI+LcWMFjpD3OUcSxYlWfhEI4/CUH/hBV7ls5Q8UH8gBj6MmRVPwHIUvN'
    'PW6/hsxSjqgU120Utq72k4yRgExqpfVDzOYjCxjJhMFMkJQVNlVc+rP3if7lLEMR0BJrr+nwgDc6tXR0'
    'kieYAkyM3jXod64tVCbTEKAa1GShS/iUSI0j9GuLgZDKWz1PH+ooWuFNTIi0tT1+k4HNW8YF3nUNWLzc'
    '0O1UIDGwMvkC5aKGs0H4/hALWyyseiJ11vcQCLT7PWc2Q//HoiQBB3Bx6vVL2vcyVuZRafaXqK2ruDs/'
    'usB+aoGKbFZxyFBSMjxg0GeRiz7brKju8VXUnmAVKdl5w9oSMzPFYJtRB0Y='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
