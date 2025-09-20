#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 460: An Ant on the Move.

Problem Statement:
    On the Euclidean plane, an ant travels from point A(0, 1) to point B(d, 1) for an integer d.

    In each step, the ant at point (x_0, y_0) chooses one of the lattice points (x_1, y_1)
    which satisfy x_1 >= 0 and y_1 >= 1 and goes straight to (x_1, y_1) at a constant velocity v.
    The value of v depends on y_0 and y_1 as follows:

        If y_0 = y_1, the value of v equals y_0.
        If y_0 != y_1, the value of v equals (y_1 - y_0) / (ln(y_1) - ln(y_0)).

    For example, for d = 4, one possible path's total required time is approximately 3.1233.
    Another path's total required time is approximately 2.96052, which is the quickest path for d=4.

    Let F(d) be the total required time if the ant chooses the quickest path.
    We verify that F(4) ≈ 2.960516287, F(10) ≈ 4.668187834 and F(100) ≈ 9.217221972.

    Find F(10000). Give your answer rounded to nine decimal places.

URL: https://projecteuler.net/problem=460
"""
from typing import Any

euler_problem: int = 460
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'d': 4}, 'answer': None},
    {'category': 'main', 'input': {'d': 10000}, 'answer': None},
]
encrypted: str = (
    'vfJWCkw/sJ7iZIB8RwjI7b35ZVqBvC072XmAVQaEg2Lygb7Ct7gi1SuD+nf0jCzRdIG1DeMmuKMzUxlf'
    'IjiajK1O1E9JCg9IqEjGPJOCud8icGIOxqMFhhTEvyi/5uI48Ml9mGFxxv5aV5XNDkTiARHpkq91AvQz'
    'tQqlCjEwZMhgxk2lb94VrmJUGEUkgXB48rApdCEYLSIenJV16dBc2QItZ5lAy/YpGSaqqmhrdIu5gHcv'
    'inY+/ZbcJSUkqyEIRUpdAx5NUQUi5AGAULO+Mv17OQkPDcpFBraw1rVT0igxAhs5oY6h2xF3jZv2sg4n'
    'i1cDSGQq5LW1049YTKL1zq94Wjf67bxIL7PkVSbrk/sK8hIc7/IVnPgw6TZg8lMhZjH3LYyW8+dZARp7'
    'DndRtjUN/qCsFApUOVTnFrQIWSpEUosr9KvuUJVjLiiUAfdRzmX2wasIYGLPduUupsk5T2AVIOIg05/4'
    'nBvDIwHNFUkhAzr9JkJXrD06fQdUCKz1Pwp3wiw4DNAgkgfGYGFp3rgWGsEELUaQHeBLzgI97s8UVLnB'
    'Zqx6BzSvDlgLtqkxKkBkTRilPdQhx2JmJkd+DAyPsThdzWUjsCCjkfQABh9AxfL0eIt5cQxlLfnZbFzO'
    '32vrWcuMld10gd//VmX308QtBG37e3JoJ7acckbqvVk8v5rD+Xxx0bMFwrqnLwowdzQK67YqBasdwvZ1'
    'KB27O0tl/CZcNEkiX5wIKvQNN3EJ7+M0xmR0YQcER5R//Vwtj7cdGyxmTxN/1SNBvoUV8GT3pTxxQ8aw'
    'YIc42QMEB3Q5B1dTvTYUjBUPeQZuo0KcldXKUPV5C5X2IWZKPjlW3Ra2kHeUn0ZOA995iH/VqTdtpdt6'
    'vTnxCrYcpi1cPBFYKJCdXK+6uXkmg50PfeiIk5S8p6/jZtlCUQz1OS7xqBqpkSe+cVB9+YtemJRS6OpG'
    'lYE3ME3EHXvopzUYIYWIqcIOtaiy+kLFkMy2S7TbqgECb0dLpjIZF8tcoTCJkAm9MPeimb8jE+Llc1sh'
    'VHwpq0OjLExEdZ4rT4sGMCe1x6XLlXc28aEZyjqgpnEprfdKJVLGzwvoAcYAjRFpluEQhd1XnFuy2RYq'
    'UkQW2Ixa2Nb2wnj2ezkEQSGAoXDBXT1IE8udn3AVLIQ6dmLsg0TYkM7ZgVvBj06Mk++2U3/N5awCLMRr'
    'kCL/7G46vx6oX2C+wx4+bmxZqALCWSP31SPBkA75CPBOFvvPKvHGAZYWxgZtrydy+E17KmCOCHrfGmnh'
    '4/OhNRQOdsz2vsBSrSpd28XphIj7gYxJm5TMUd7m1QDwPAGUOpgO7cnNa5OQ1BGOYxk8B0EsXrAa3xmx'
    'NYUeiknFPiq6VFrg2ToeXDEDbIy8kNibZDeVEG0IZzZpNSNFiXTENokJHLAhyrFkwlcFd99nE4tzse8a'
    'blkcf5ts0GWDSn77CDWQK1Azdcots+3O957HBRgAPkIXg5Wwl34r05754pvnoqER/n8JNj7YQK6YfI90'
    'DxXWURSI6qtKVPJjE7CYIeEatReYFSc3lHlaXPKN+ZWxtgz50dU9BG6kOcTLftPQ6VFMKeE8xCt7M1js'
    'W5nSSrVTeGNZRu4yJaiz+TZhgTkNdCkJH4FLkjRKrspFZnpDH3gMgZKmdvFyRlkaj+q2MqQFU1s8t+qM'
    'aBZMkbL2ZmS9BAgsph+9L4CKhFZM71MrVppPvd8nWYGl5bn0XEDjAIt05E0bftNTgfpB5ee7Y2xrujrn'
    '+X0bIqVeiLjjPatpB5xObI1BhnvBXlfkNu+JgbUe6/8aIdUqLtRlO+PhCykDp4uH2vK25ovkmInr2zTK'
    '3QDQv5BLFNIv4Y8CgxMMTE5/LSHZbwU7i5gxgSyILzezQT4MXSIsROA+MuOuz2k2qd/aB0ytK4S7mXZn'
    'GMFKuvICdxGqxUJ5h3rXkkoQW4xtbA38phAhpSSdWYImB81gEwfqlOTNob62tA/r798vuNq1SA8TcSbj'
    'asSEQfPqw4hhBORd23/WG0izF+3XGRGXgzyrTkYYFrA4t/fwubndKu2orxCG++l79LoGl9ORfvxyUAfb'
    'hu6tFVw6IYIfBaCV+u6VFVYaFuS+0XKbhJLYpwDnaEqGbPHtdheVowaseW4h6peUunGhRPmiWomXV0Yw'
    'wlJ8lGUH2BsiGuMoVraWXDLLMQsF9mac1VL2tXPF5CAxSqF6MJNJloHbYQaAUpGEoMbjpIynbx+TpIxk'
    'JOixDV+lGmvLSlGPEFeVmO+O1SNMih+WHWMhQxt2JLtERFzK5jAD+C6uvu1mqspBAAj8/Zplc/dzUFf0'
    'm5CTaeHhvoN5WjgA6TSpFzsfYUGhbDew8tgQPe/RNxNsTRVOXECE0NYjm6lE+THYiCA9UkT1+93Jjp0K'
    'MGIPZ4/NpruxgCvsUWx4i9tzTzME8drf2cq9AZGWZpeVh1BCv75BHiaDffG4nv65bMFfl4TXWq7GXz9M'
    'TfyvJLWoJ5FPf7yRaYbBNzFzUcV7e3zehXc5fmtKrgislrq0u+2xDmR9DFr6kndJF53zbnZVnobEekdc'
    'sbGq5IBIRC9yMNIs+rY6m10sD8hxIhgm01Y8RdwgHqGt+iyyURlWjyEFhDi+nl0UyuQ55lI7P7p3nLKV'
    'FnI/VSIm4ctT94RWhyGXiEjQZMtrXt3N+ln5INP4fnUDYs4GFpWB55cSGxGOWCysPAfOdrclclQuTjNf'
    'MugoxIRXJwVNfHyE3fh0Pbd3dhjJenwlPtakXT07TlxrcQWcJO00lX6u5973vN+HgCzaoJF0GidNO0dr'
    'QRnY311uv4670uWBoRrcMFwwjJiDUdFAZr6H/LSfrGjPzkc2PIhm76zO8W3UKFeUbBVT5qziqup5aPfV'
    'PosTqL5I2vPIvlKPZy2CtRvFGyrXNnAxYkMdDDjAPH/8DwS1f702c4SogcMJt+f6Mdwu4pbUoa7ivmiw'
    'dIb9Sd/ZsCWB//8FirwAjuAW6ZepOVd29AnArs6J/4z54sBF3uxnjXTSAxBclBPHMrWazIxLsb5V5pIX'
    'mYVKVXBTP7QcJhzSUlWaC872qKqvYj41MUtBTAhRT+ZElvs7jImslVitRlf8ortDf5dgFqcfsRW+Zdur'
    'TDOdIs1OvwGODmpF'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
