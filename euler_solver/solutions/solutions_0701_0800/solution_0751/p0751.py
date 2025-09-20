#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 751: Concatenation Coincidence.

Problem Statement:
    A non-decreasing sequence of integers a_n can be generated from any positive
    real value θ by the following procedure:
        b_1 = θ
        b_n = floor(b_{n-1}) * (b_{n-1} - floor(b_{n-1}) + 1) for all n ≥ 2
        a_n = floor(b_n)
    where floor(·) is the floor function.

    For example, θ = 2.956938891377988... generates the Fibonacci sequence:
    2, 3, 5, 8, 13, 21, 34, 55, 89, ...

    The concatenation of a sequence of positive integers a_n is a real value τ
    constructed by concatenating the elements of the sequence after the decimal
    point, starting at a_1: a_1.a_2a_3a_4...

    For example, the Fibonacci sequence constructed from θ = 2.956938891377988...
    yields the concatenation τ = 2.3581321345589... Clearly, τ ≠ θ for this value
    of θ.

    Find the only value of θ for which the generated sequence starts at a_1 = 2
    and the concatenation of the generated sequence equals the original value:
    τ = θ. Give your answer rounded to 24 places after the decimal point.

URL: https://projecteuler.net/problem=751
"""
from typing import Any

euler_problem: int = 751
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    'NuVXmbLXz7QdluJllFpe0KiBRj6ZEpXYqC7eBixmLLdI/YjSbF+O9KYIzi1+5C09J7zfBkZctwujBBzI'
    'QIDLIuALML3mnkCuEk1V6zwmbVB72cn9n255bla+/YQsI3lAhTvVPPDhAsz6nnyFGz2nSmQKzevG7C/b'
    'Vj8/m31d21HI7C3/rgmsFdc26yAzgwQihoYKLEkCqCk0UDBfXKkKggbvUEiuMQHKpyy7AuhJizz42R1y'
    'ikvRb934lVyD8jQ/IO46Z6oftUENyXA6QHoTdxDBr7uw4tGSadOVmXqN6H9GI5K0zSwUfV2da8Sx2sgn'
    '2Ejne6/PPDgaMsynmRkntq8slqbTsyXkhcnADlh3fK/Zypqq6dDsSrqsPttc3zkRli5SBEu/ky4HuvcB'
    'Lwn2NnD7T9Xj090XfqHZWlk9sKxYu9yT6YjFiig6unoB1DpZqUm6aDnffFDUvXjxgzCBekVWJe8x5Ktu'
    'a8JFdO6mLg8EhQbz22Ma9Rd6LqrpZhvcWSGZl2+rzIke+4CV0x3kOMUI+cTV/HdvTD8z3hAzKOn4UJ/J'
    '88ZFV8qWIN3VhD/Pa6Rp5GF89safjmtmVxbD5ZCHywVmG40wJR/QiwZFX8U5R0ic+AYNsZBLsFosAfF4'
    'xghb08lzj2UM/QvlQOZ0CxJtXHzJACCQceK85LCSIFS2eQE0/vdtQtCh7RDo2fppBR6octiMM745AQk/'
    '46CE0a8+Oc92mdL7f1MzMz9lC21hxIEi1WcKy7ZQ2TVfs8w32YgEc4MhAGko4GsbGIbdhN8UeJC7izlq'
    'jsl5Jb9rXN5UIueax5bb6Kvv2Kx3B3bQvKzf2Y9hYP88kM4HmlU2MbfHKa4zPIwAgRviD74mP804DSKS'
    'sNHQWLqwEVnJP5vcmYw/1sVgzUobVsGRi+v98P08Igg9Dm4gyMW4AnAj5g7EgCQhDCwvvvu7Xjz3NCcH'
    'fsNrIp2EZz+xG0CnMlhen8F7uejeMY6B/3wiLpB2e2KF6nP6b7Ioaj2N3HdczMk9TcHnJr6E/tui2cD1'
    'fYa+JHq5NyKW0IDMf5wFYKAgpXcrlPqQ/cW/GQx2dWzEXohy5+i3OioSKPuPoUPh6stHsB3XNhuHwSMJ'
    'i64V9Grjyb2xC+sFjfG28b47m/RUx53C1vZCnDEyiIuuuYZ16JKcWXIShWfNUL0kowir8DL2M47Vgx7t'
    'j6berswenzvO9DJ5zViZTjOUjE9qzHb/Nnrckk+gHRgaAT6zY0H49gZb//5ZgpCqVYEWkildgEY7T95I'
    'iOQFqKZZcCqAMlWfc3RvuG23sgwDPnjaZCHP5/PdTwCYbIWmzniQJgVdDwTOLKdL1Y/+K4cXEMyWvywB'
    'UeV1uFQdP5x3Q8wdx+TPWQeC3Xq6hA1ugcoZ97RVikov621suaV7mpyerG7HncCiinOg1qMucl0w4kqr'
    'gT0osYsIDyPVAu+G40NHYBvjW/tiFVfGQo4f2FoMFR7yo9gH7CFedRXisxNk+YXMohzJfybPZ6+eB8bM'
    'CL2m+ZVMBDoRse9QkcsYqfH3Oz/EhP1JVbgAXpTXvWUjsVRB0tcr0764BWVz+R3wX5JG5/rl68Fl898d'
    'mL+NTA/oEvqzAkdhpRbZ7uzHHQp5AI0lQrU30do2R8CO5/hfkFzfaeKqe+0zrjbp9O4JoVUXdl+DXVBk'
    'HCMUreiFKWqIQkWOL2ikHjyf/8hk4pTk+Y8Pc/Zl0NLU7PtCmG1/4WySp6vqIwt7iVoFsC8vttPrUxll'
    '6qkBGsXexOQtF0nYTf6A3LiHDd2dSmc+brUGXg8VCYR3vC2L71M+HtA+IGJZ4JZ8gbGUlYeg2RUIhXAW'
    'J9wJkG3oMg0OZqLJdTE7famEvAEzHZDuNqn0qdMQld/PSReMtXHB/X/SFX4zLgM00FNRrSs0kLrGUQUk'
    'HVbaiTK9tRbOadfaFRtf5vv3swH8Dyx8JIyTGQ3XVcYy20VQsRpywj62Y5hL9/sLAwzn7PqSwX/u69Ig'
    'vWwokMDNOO+RpomPadFpgzIbR31j8uE/rZ+gCEmqziGvvfDpSVmPfJEQSseGlol+Hg6eV7BufC9x7wew'
    '4y0ozlhkErvkiRo2P0PO9au9cKdnaUHSiuRHqlh0WnPzqKrs4HwAJ3ZxWWm3ML/kWjas1sPLFKvMQaVa'
    '+QASe5EdZHmBzQSTpexElN/Zq4GHW7945YA8F7Mgh1M8NI8aFIpto4wofujgn3432VuOBncaPGqInvvF'
    'v2SodKgiOpEYFQHea8ur6UXxK9Rd5gd+c4e4PARxH3L6JsyIabfVIcV1PjQk+64qFbKKzSlu/KP7ceHA'
    'gopvQ3WCTqKhTWgtmnoH/guJTIS/+s230KQ2qnnw/HRyPfwFsvVpdDHtCAblWmu13lo+jdmXAyYKs362'
    'zUpy6J6gAkLHL35vXlOoR46NXZ6Br8t0uKjqqgzkQ4Z4JWmEDjigEPI5H/mCw1y9mALTw8NmHuXGPgrI'
    '9OedJJ5dP8ixbSITF0S3snlM5RfrfNuuU07Btplzz2/b5mARh/iSPH+ny1hph87ZocSAOlJImIwtK4Y6'
    'f6LlFCaRW1GMbxuOK0+c5XahndRuMI8tlRvyblwFrxuFtxbDPfcgmBwSPYmU1nkJr/PHDpS/ykVLMk0h'
    'DLJpZmcWwtsWKBPRLVQYmCjnQ95xJjLsue7zDNslHGMsz39ZtGpfFXF0WB+sBzWbHI7RjJSGFQCsz2Qn'
    'HwhNumJ6k0viwnttcQnmGju38zM8ybRnX5ioJeQkIkT7xWoXG3bDknyDWajBw7G0B6SWQw4os28Pd9Fn'
    'OwI+08x+xOIQ2ZicbUp02oV8Y1FEJD0hDI/7ALGpu9dhKuKgNTTzOp2u9im9lS6EFsEkF4ZEj55nSEQC'
    'fAbuSL2/fVYf5BD1okbw6d6VyaY0uv/xwTr0W/F6Qilka+T37ZphlfJ2apEaq8jTCNyExioUb2jEnR+A'
    'DpUZtr8jPl2TkZXZQqJeIzFRE/fAJjmf4x9qY9Cfx24blzdPQ8bT3aBs6uakw1JrHt+Yi8FGYLTmfEas'
    'NGvstKokRyEjBrj65OQF1C2pSop9A6wJs/49bE2dbqaRCePrtxJOoQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
