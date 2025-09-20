#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 540: Counting Primitive Pythagorean Triples.

Problem Statement:
    A Pythagorean triple consists of three positive integers a, b and c satisfying
    a^2 + b^2 = c^2. The triple is called primitive if a, b and c are relatively prime.
    Let P(n) be the number of primitive Pythagorean triples with a < b < c <= n.
    For example P(20) = 3, since there are three triples: (3,4,5), (5,12,13) and (8,15,17).

    You are given that P(10^6) = 159139.
    Find P(3141592653589793).

URL: https://projecteuler.net/problem=540
"""
from typing import Any

euler_problem: int = 540
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 20}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 3141592653589793}, 'answer': None},
]
encrypted: str = (
    'jaM5sXHUTR4uIh6exasMuGq8pqF2CWVL12ROnEF9YDxEILTVDlHt7zfS7plIdDylPj/4qdq0bCGLiYuc'
    'nBTXXOi3EOLYOuJglxDapel5gSIqpAQkT6C+d7cIUgWV4FeQ5vO1UvDVA4nwE7T2Kz6x6iB+siULYHzP'
    'jiAK22ux4vV7omS6Y128dCHD5hHIQ8nP5U+xIy8LsIwcQ24yZGYAxrT7iMiC48ra0EMUU6WbTv41xRFf'
    'BaZ1viTyD8B4XFTaMGtHNzOsZOdiHMRi9U6XjuzJ8zpeVbAf3vUFZ9OkROlxHgbubqlVgY8Atzqk0qSK'
    'qqbod5Qw0+rO4GztkSsqztuw9IaV6AyNHl7RZ2CDGS5YtRBgdzJI3/TdXnm6DjdWkV+Yl8kFXtC2Vza8'
    '3qmMZevpKywhZzrJOUQtdJmYLilG06Jn966dLbO1pzySns08UmtYyIEGKHB5fv+uwn18M6MucFpuXPhu'
    'Z0zO4LNg84nU2JSGonIqz0DX9tD7iMTkA1xGAwi4b6G2WEZFxQALqyF9w0gqseBqwH6J5mMisHDH2f4Y'
    'GegC6thR4vzZB/5R4r3H6UI0vO7JWTb/3uFQnfxJJDueQp+dYBlorswGQGfu+IlQL1lgBswjSsqGzWSJ'
    'W60FtiR/3TIGf0zpZpBwVG8M6eA1FV7a7kULkcKyUpXO1yPR1/BDrqmUuwqVh5ej4xd5hiH58f6duSvv'
    'c7whLTlFxQiHJv2KkSR22iQd8LGcNm53qUJva+jdRHI609FBjp7ktFQ9z8VTMZKLgMSGDxadj6vkBFGU'
    'xEK6mvvRimffBTdHoLiynrVxKaZqd4KuOGkRVKHpuJnzkLzMtaYLHybG6eN17ntj2vd5RNkhe9BLH3H2'
    'hSnL8sJ6Aaems1zq1FKfNDktpMweEuW8GAO0q/fGzulEM64XAkT4iGCXebEoZkbIjif8IRZES5XBfML3'
    'eaG+Pj87+BsleWmEjOVGs7f9EjDpLFgJuZuVYzFXqdjhpF0zuiWUPgNd1gzJXytfzaawhWpp10qA6q1c'
    '1Gc5RhvsQwhupxqcRPFI6/MPRqjue8ghGYkNWu8PpPQPWY0RYZnuBwcO4kiINGEZ5/YL3Ci2tSDat1V4'
    'e5LCHtbyLu8bIL0pBvWGiMnG7VIPsLNEMSzrfS/mPsHu7se9eKFyt1LBl9vO2JQI33+o8lIC81QQnuu0'
    'w4SFPAybqaaG/D+pK9cd6duWnxOijqBVZABbCybkZFrNXrl4vVSIH/LlrxWr1JXPu9Op7IFa1zG9VdwA'
    'Dy6N27XmfyO4ojxBY2Hj+fSCqgK3PT5khR0XNC3zzXPYOTAE+tzAseae9HTJH77zIvHxUz/fRoSTjsqp'
    '6uZn81ycSaSy5vCVcGyyuV6xuxFNlN0JtUdU5Mvby2P2n8JxbZ7pSeJELf/zgo7x4Bk/xzQp+9DmqKD+'
    'KpwholvoDMWL0BDt/krmysi5y2RoxLj1/1wm0YeBGdBYW4NLiqCMS6uvtc2UoIME9vzdMN1QNaLHKz7A'
    'Ou+gBwSFnNQw1pDUCH5vjH7u7uEMd8dbMjI2GTQhy0lIYFsIky9Imea5a6bYNL3u8DAjHm6lTmORdyqL'
    'e6BMjOjNQP+bnpXsHgvir0ikrsS5d43YDX1HxqNv3qMbjKlWzjgj3nXo72G2YdlSyYNMZZedjcVzF0mS'
    'h+RQQ+RotjbFksfKdMzLWNKUmCIsv6zA6WmJqEkCTtQHDFCQirqdK224u4OD1BEFUvM+FJE6u6cYix5P'
    'uTym7gtPqPRFsBtJMqKfqHY4OaN8DOFgyZlctBdMwV+FAzHreftsXux7bfxlBkStqOF0c2WfoAecrMIH'
    'ZYN2IvUJ5Jxutr3dJN05mY0UFk2lCz9JHBr7+wEXHmxtkrP76bgCCdQM6naHzfwrW1FT2zOIsSdWM5Up'
    'afwBv2Iuo1/3AdBrkHbfwObXVVKm0Sw28UQ+Tob9MZqWjd0+kU3mhm3Ecuc4aG1+99fl0NIKMm+xel44'
    'JQUbK+hL+6rkSegUTasCpjBQFXpffufHwfe1ALjYrmXGaMak0BD1uHJrUWnZ8nmyIfS5bYENhKhVLfGA'
    'TA1vvIUeB89rIn3fzPNzgKt6sBEF2vq7kpnt5XA7h1Cc6jszbSXxdgmJrtrnHbVoqYix3pG/C+sGLsmX'
    'UIlaQ8/C+cyteNW0cILj/q8WJPs7cLkndlQsXAjyloHKkgfvFjmqXhy4XtQ8Tt3B3Ajd8sME59p6tVcV'
    'TZvcGMUR3pm8rC27BxEQ3fBfnS7yrvOpXo0sE9lNgaTQU2FYMhkXKwo95zvbzkulAWiK79Vm5V2tc52Y'
    'PdTqxA3kA5yb7GMRW93tlP7zMDaHg5CDIwqsrN/n+RrWckdSN0/s5MzLqrqumLxcL3QvcwfpHp621AW6'
    'zNeqDkk/Kn2x+MEjX6BL3GVsdwQ404SrA9wbEcjkwZW0hANe5JBUsYdSbz4VLi+125/lIVfZpbsg5KLx'
    'Y1+1s5sseFPUa1hkCG8Y53c6m0W9SoMfX2sskzHKMWdniLKqWxTgSr8DCZVfTXGtWIx0TPRbzeuiUweV'
    'ColnyR1S8CwVTA6l06IakQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
