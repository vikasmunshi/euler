#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 450: Hypocycloid and Lattice Points.

Problem Statement:
    A hypocycloid is the curve drawn by a point on a small circle rolling inside a
    larger circle. The parametric equations of a hypocycloid centered at the origin,
    and starting at the right most point is given by:

        x(t) = (R - r) cos(t) + r cos((R - r) / r * t)
        y(t) = (R - r) sin(t) - r sin((R - r) / r * t)

    Where R is the radius of the large circle and r the radius of the small circle.

    Let C(R, r) be the set of distinct points with integer coordinates on the hypocycloid
    with radius R and r and for which there is a corresponding value of t such that sin(t)
    and cos(t) are rational numbers.

    Let S(R, r) = sum of |x| + |y| for (x,y) in C(R, r).

    Let T(N) = sum for R=3 to N of sum for r=1 to floor((R-1)/2) of S(R, r).

    You are given specific examples and sums for C(3,1) and C(2500,1000).

    Find T(10^6).

URL: https://projecteuler.net/problem=450
"""
from typing import Any

euler_problem: int = 450
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    'Z/RkSTVNtuS8zxAYQPgFkkeAynhm4hjG5lffzalPtcT8I7zj6Tbfj6WakRawxcnvKmO5wbQrTZMCvJLB'
    'OdsvJT5Px6W59cyjL2qN8QlH3ZOrfvV5Q3vdP7uYyvZ60cLx4cRiZNFAKkrBtnHxKknnXjR0ZYNGxfFo'
    'sFUsSE6ZPH9AFnD9ZypqPQCtR2+4NN/dhZHGTvW/o4hN439hJxfc7ChIMojtHivXvD9rEJkfhEwcQFrC'
    'INGpJ7RyLZ9g3ZxP0hTWQDIGFSx6K9Htl8VbJb6sZTzGnONlcTBox2JIIkRHKTXUPzr5Vkn7UaCD+eOu'
    'xYnC3NjTN2VJh3UnQy7PnyEpcx81VAG+S+nU7mdVt8iVNKim3Yf1iBZOERIJUPpEVdzC8HS6mGzn1qIj'
    'xId8X17lU5vTt4gDKtHK/Y41PPgJ7EmXL80EYEe3e+MbkTfw1ZRTh6VWYbHm08E3PAt7wtazt4QMSXQD'
    'TPyNLKvUjP5xVYElV1KQ+TK9n4BsswlHvDHmpPqDd5IcjmVMEayfJirqVVll2zXJ8FrC/++7wANUYc6Y'
    'n+TmkYRvFN/gp8w7cN1QOV6ujL0NckLR7AcedKXsMrkwN5Y76UHNWrPUYkL53QadbHucAQ8zDr2E9Zcj'
    '8DwcxhHxcyqOi5yOfZ9FFvi9/IMRZVsb+uL2nu+EhNTBGVkWD92rP4NpcdiRWqvGBeKBrOEph/WxPR8Q'
    'pJi80it7e6ldJu48R6oKzmtXcVQXLJqnPayDF7lbg/AyIx/LZylYi2MdI85OiGRba+E5CwaHwwLv3UFF'
    'CdA/MMEZwTqS4Uh3+w3gQb3NM0T1Xfim0lEtVdSPYX8+s3FSZE3M9U2c9MCvtXT6mdC13ivQfDX9ZSyB'
    'VqNCQEPPoaFJ3HU449r5OB49UnhAcVt2KclgBoGxU98TngRxHNVnN71DfPLPZyFKaGVKjb1M8jXRLUpt'
    'bhLUSd5kfi/tjKS9RRyU6YiP16sLSUsNRaIDP2WoZJdA0LJhyxfvN3AdqvKVl4/E+yStrwmVXmIr/niN'
    'XDqxDgFrga/68byHDYk8DRj4bn7kd99/AvG+mjJWCCzHjWdRRUrWzoGH7sOgIwiH1wxy0D+mfAV4yG/9'
    'oxAoXlJYUkZsdgk1XDWo/NrhtlMwV5RyfC7rkCwzQ1X/SpDkIGvb2EJf61Wb8USSbDJKo1dMso4n7pSY'
    'SA3fHPJdiUM8ex0LmHZm5U/2v0VmAHwO0klFWQPM1Mp1k+Tmi1fzu40B/MD8EcWbufO9uRqTLjpkicZR'
    'J3GqF4mPg2NBnmKUQswb1gLVGUENnMoIn1TeBTZEORoiAk3/rONlgY/368wqIRGvmFH/I1QdKZDnNuLG'
    'MB4Xip3tgmSLqTU8G3MTdlkJXWOFCUALRV9YJowT9Di26UgJabRy35ENJwYBH4J8AxptyuJgolJFMUFJ'
    'SWM/DXFRhJoJIH6Q4GNZ9TIeDBgQ67CpXoLQrXxDzL1eULE+saK0vgRIyvQf+t4rF0XTrRPi/LI8/I+H'
    'QfekujEYFixiZWFKBKwarm81nZ6z5LkshGxJgsDetf6cCaDA81A53linYjrqyUhDj+6Cr4rQ4/+n7HKi'
    'IQuN3h4QZlaDzxA4IYPZh37NImr7H73zVEr0AdNcJri276eUGjhlEYDW4rB3pXjWU67fjS3fCMqvFHPk'
    '4ztLwkdfCRUdb82QDkwGrfkq8+gKELw5hjPME7ILREyshtKYLSImSoZ0ZqMVY8tQDpwmUcId07UjYsMj'
    '3z633pT3MsE4L1x80uj1URr19gRs751QoKse3r6L50YI8pUGQ6rK0h6MkBdEUTdFLimY6httXN4uGYUE'
    'hOGRdHbqY+Pv/ZWXhNL36WhK4H4WOQEew9n/2yslE03n5q1fR5l0kTso9GpNyVz/w+Yonn802bxbd1yx'
    'oF06p8HFYnDbLgBeTJOTiSKHwlV8WvfU1wuC5wTzg4cSHn7gsINN21NN52OlxDR8zYZdsbp2y/p3pBp6'
    '0Ln+UTV7KxUJHULXdBRkcpFD1CruwbIt+XMZocfjoyQQlJLB3AtmXUn6nbQdMPlUrsCoexKvFsWguuVi'
    '9BNN71VfzJuTxzTS0dpiWtTK1/jJepmqK6kWScCx7EExGLp/XhebhQZwMdJY020HDJnEbvorY8JHkSfR'
    'FcnQYEE55lrh7HgOGuH3gnnH75xm91hNuxwQj26y5x6p1ylsWvUTOj7PSB6REM8FhQx34VAMHyZDvpMO'
    '/re3QlMFbgwYph96nkLMJk71zsNa45pTiHqx1+5VI0rcSX+At+Z2Q7PpMKG1bcU7nGWvONkOBbxMdaie'
    'msdAgiKNLLNkrsVvnDfW8Ss70U5oTwNQemO1lMWmR+/XEAj+VE3x612iu5r/LELUspTtu53m1ONitwls'
    '+EdVYf732rtIFyGejo7bXBU/cKXK5uxNSc1JelkpjaT6dlVa9gDEtN3f5JHpvTd68wH9WFcbXHS2bsy3'
    'vNOz0P8wP1k/8M8naRpK/uf9m500OyGeCywL2tjvQLpzmzMejgCUqKYwr9wjNokklkU9OoJAVUCQAG6v'
    'OmVz69+ya3DMLZstRmByERm7MjB2QcNZSeE1dq9sTZLstfScGSL5D8ZGjgu2LDAYHcKYKzevYvZHllAR'
    'aXLkIVoUFDZrI4sDLFVLCBi345oC59OOOWO6zncZBSrRa05KUIfxW3ndaUEUUD/xU5zdTE/lxN9TmIvE'
    'EuPxQRz2w2KxvoQVVXYXKXKxIhE041ij1OahIW4TxCKIb7Xb7HuleCouNttaJZl7TxltPq4wQ4vVncy4'
    'bTKsfH5d/gLR20WF95EsEX0GXhIDc80tOOPxzU3TQ4JAGUT5s96VeFDxTId/YGH0E0wxX7BI9c9G7cuH'
    'ajPtTkyNI75b3EyrT2AAA2shskvsc9oMqod05+H5E6/v2BJSvgZPoKMBm6SL2Yr4i0luI+rPf/AH57ux'
    'lnXdUjecjSaQsWgzJreLlhXVMpRw1+ZPM7KyPu2C9MaszIVj2a8y9nkELo8S8RsNFHZ+0l5nybUf6HXB'
    'kq2IlWsAdrdBlYQ3kP7PrZYCFunvtuRn'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
