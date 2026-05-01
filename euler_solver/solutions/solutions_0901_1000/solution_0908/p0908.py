#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 908: Clock Sequence II.

Problem Statement:
    A clock sequence is a periodic sequence of positive integers that can be
    broken into contiguous segments such that the sum of the n-th segment is
    equal to n.

    For example, the sequence
    1 2 3 4 3 2 1 2 3 4 3 2 1 2 3 4 3 2 1 ...
    is a clock sequence with period 6, as it can be broken into
    1|2|3|4|3 2|1 2 3|4 3|2 1 2 3|4 3 2|1 2 3 4|3 2 1 2 3|...

    Let C(N) be the number of different clock sequences with period at most N.
    For example, C(3) = 3, C(4) = 7 and C(10) = 561.

    Find C(10000) modulo 1111211113.

URL: https://projecteuler.net/problem=908
"""
from typing import Any

euler_problem: int = 908
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000}, 'answer': None},
]
encrypted: str = (
    'rCoeZjFQlJ3MZn0KsUn3iY0+ufMJR71U80XyQp70i1Q/YWwmNY3JaVlqat/gU1HDJItjMPOKfQpJepga'
    'xcAz74b932ZNTWLEX9LW9k02/APiinzYSKR2yVYoA3P0w0RJnZ+RgTudCpYVo+qhMqyGIzHI4nXhN1lP'
    'Sq5uTDkb8HEIjq3I0k6kNieUJp2+8bGfibQ7wub+vEes8fdDe+YPtr5n47dGWT1L6GGYxMhY1itgaF2w'
    'NvJXdytOA09fLEbjJtTJMCEIbsJtCcWgRzHT0kkJZ59wIsA3QiZ7fDUI2oWvZ7Q0Y7lIYkQWfFy1CXnJ'
    'FKj/NVrv8V1dv6vB3krnQ/jDz4XDDm384E1juz8ufBbfVkhsWikE/cDz/n3rKrZyb94JiSZzYqTgsVTN'
    'U+BW9CyKZy/DU/bDkPgfNYyg+COKcxMcmOtdswFpiZxhGmFpf0eRnSgXbwrC6bl4pO9MBx6YTkbFHhm7'
    'HkubtfXQqBA8Opag5BKu/j7WPEGY62Aplq9s/Qbsq+3Hr0T87KcMpSURO6xlqR97bcJBgXqKRBe2Asmx'
    '/1ZyECBqexzGnWhjVlEWauANwhKC3P+7K678S6mwzUoaMvMIkgeqk8vc0gDFV3l/Yb13QXdMG9KEVfkA'
    '4I1/fvzflVSJuIJuuQ3OhQz7K7KY6axUfu2cqol09Hn2LltJv3MxySHzgqgpIn1zuI2aqRbX48OFpekR'
    'wDFog2I2sOukch48/ILg5kzI/xp49Rx43MIvBlcvn5HtwDT8dmb/Imr0Pex6cthivEe7I4rFUkQ+yfOO'
    'mFoo2GygiWPIVZusC9Ych2l4Z3Fy7fRL/y0Dq0QmGi8qaQ45tp3vaRtbemuxFlU+7RWIZoKfkcCyM0zB'
    'wkWKP5gW4eGH3Xxlxz2A9NgyEHuG8005tI8lRR/0D2w1bvSoCltNBNP4QtAnDQDYbBxXBK5Fyude+9Vb'
    '4wy/f7YB5/Tp7o3GC+Y3t1pgq1aTzW27HE+W0QOKdRNSg19QXnCDIs15MiQHyLE/eTSyAfvD7Wxwb1za'
    'E/p94VQwH4LxB7wCCfxEZrkcELSkwvNT5qROVpQ8paWMLR8X6MJ5wrSpkdevJt4/6Qn7fAo/k1t/qtMy'
    'b6Bu4EEvntZkD6/qexcNguZzG3M/MzWZ/l/p2XP1Lpb9f2lddG0Earvig4VS6cz9RdILefHhmYIFh6Sf'
    'dpe5VrRc89mQFJLu+rYUcPWRISOAhoNdz1TZ7zupzjKERqWC/ro4d5/UVRSC3DL+sygkf2aaOuWHUesE'
    'pjYrjsfokl7CZavtGgebktaIygoG/y3Rz0YgniFSfR+7O/xRcG6oIWawx+Ymi6N8TzDhI2SngCtE92eK'
    'Vb3ONjvyUlubSaVl/vp0BWAtZkfN5+0HK+zS9RTlriMqgvWQ7yaXDBb4wBIbakch3YLprnz/MeHQseIr'
    'lXioyevUVFaUX2TO5wL+MXyrm71Jy0OBSL3XY5PSIMiKd9q6rlFjnvgf+yHzV+NCPVduDXoBygrJe7k1'
    'zqMkm5jXGiN8xhGG67yxpCMHj5aM/ChXVwkZCYJVnJZkmRCdFPEPqRWuLaDvohalZQNA22TL9wrTArP6'
    'SQDDue6LkIbcoB+N2DOMZgkuyBpKrFn8YGGJZnYocWKyLniTYE3YOXCD4vANX0v3pzYsaistzS5BVY/7'
    'zD+qd0cp8vXsRZEm6IcUl8uSgpxgL9oaa3b7vFNnWs+xCw12pD9Z59B0B5kDWuq7QUB+B8DRj0EgP8NW'
    'qn6Us9L44gyaPDv7YgTiJLPzA/LAGwOWOHM+gXgYjquYVtQtbbwyYpQV4EsPtlA1HPY0IyH18nove3TX'
    'g29Sd6vthL15paw2hp53MqAcc1qwPJoHFziUMNykJ7oW7bVL0Ga78/B6BLwoY4aSE2UYcH/abM0R14lI'
    '5rs80DTtcbM8jJLLJx8hy5cxJDYnsFEMByVgQNYkWLGa5Yan3mSWsDTntK/Ep5hDWx2KCXBcsOiLOWpJ'
    'Jioaddgfw0Ee6svWfvuGP+5KGYP78A6wv+0MZZuTZJ2VqvKCv1bt47hbk0rYSX0spblSbifuSmk8v44Z'
    'YgpOIMEEXvj3h2Bx77Z4fgBRt7N5bwOHjXzY2Q0s7PZaXm6KWg0i8QWK2wgjwdLAgrf/JXlVoEUvWrHt'
    'rJ4Da18NoVFLMeUcJzo7AOwQ3nHTBwh+HbUdx7nX6ra/v1oPk+QbnDZVVLO3tUe3fK1eoTQcoDrsaNPH'
    'uj+qYL+TjudznLy3O6RzTkH0DnMgDIt0BBTk/aT6XyuDChPg//ZPJnIOqQb+/PegBoxMPIuYiKNI3Pud'
    '7NJChaRMz2rcrP63Yz/axFpMmJ0QgaNIkfJ/Vd4zC3VEqP1sTqyaJfqEwcQM0TtVYEBlHupqbLWPR8+6'
    'WEV6sgxVVYhknclThcHzHl2U7BpX/PgO5YGBY/p6N7eh5ANVwjnLH+Nt/U+AXUNq48ATGu5PQFRtR7eP'
    'ww5DHZMg5hmQ/c/QR2o9RBXkKmBwmuc0tGkcaiYHtF8H1hxzQJVcraNRFRi7dsXtvLS6+RpIwBzTZOR6'
    'lfmT1hAnNNoePgogcvKgCA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
