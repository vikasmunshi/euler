#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 283: Integer Sided Triangles with Integral Area/perimeter Ratio.

Problem Statement:
    Consider the triangle with sides 6, 8, and 10. It can be seen that the
    perimeter and the area are both equal to 24. So the area/perimeter ratio is
    equal to 1.

    Consider also the triangle with sides 13, 14 and 15. The perimeter equals 42
    while the area is equal to 84. So for this triangle the area/perimeter ratio
    is equal to 2.

    Find the sum of the perimeters of all integer sided triangles for which the
    area/perimeter ratios are equal to positive integers not exceeding 1000.

URL: https://projecteuler.net/problem=283
"""
from typing import Any

euler_problem: int = 283
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_ratio': 2}, 'answer': None},
    {'category': 'main', 'input': {'max_ratio': 1000}, 'answer': None},
    {'category': 'extra', 'input': {'max_ratio': 2000}, 'answer': None},
]
encrypted: str = (
    '3g+vj7SlF9HI5bfHkYEAK8MuCz1A5aTM9/4hD3SqM3HUzjIaOtMy3ZIVbBT309YQV9Gm8hrK8P8jKixl'
    'oxEZsXEbgjXVt1KCIp2dg1DT5nWxK6egfJfbwwREtD9DpRh6ohtooq4LZZ/NkqrM5lDt9DRK/DgQtFYF'
    'BTnqiqtrCEU44+GeNg6szf6objrhW7dP7IXmar67HrnTjOg7ID7B3Ae1jRXaQfw6w5Kd2+NZg+BdFRke'
    'xEcWrR6XiyCAcW1mRnSWDxuUVJPwKwXo1TbUU/VIP4i/8pWR4pOINPIx9goQtcyl2NKWIGQ7mgTGUt48'
    'Bg5C9sMOP2DoLJVZvJbqodOZvPfzpBQvgZu6o/4MZ8opLmvClDdgGFCybPihtHiPl68EQ7m0f51wke8+'
    '/vMJR/jvLVlc+vAPsPPYEUqpna4kXp21/rqLG/swnbd9q/Y9+iWvnTqe1oejommKKEmp+bIcIEA7Tgiu'
    '0bmCc+E8V3OJtT3YLRn/TWYKMp8dBwSpnDQvHjfBNQ3j/ffsa/ZDxmh3l9dUcmO8j+Pn/yde3ZuLl3xS'
    '9uDA9PxrWSH9ljyHzIZFBnoMn5g0J5UOIBUrtTAQ8mhDEkEzCF81IaaW5o101gAWPzRYZO9AWGoHq208'
    '6ertx1vZOET2m/VmF/e++QFHRpRUkcQQPkaxQrYPKPuO+H8Lf0tAEsEbJWEdPr6NrzqKyMalvEgL5kZZ'
    'jcJsxqhKxWPPOvyIP6ZWniV+CXTJZL9VhHcWjGAFDr0F1DQnqbffCd8FRTSB0d/O4a7S+qODh+CnKbOE'
    '1gsj/SzuBwi8pMk4X0Nv7iJIhb/hMMHqj8x5Ts23LIBI/RHcydZ+jgbIQ+EUDGYzG5I8SXIVPSflVxzS'
    'JV/yej238KGilE7LxYds3UjMGkWltIzAtIMwGKBd9fgj4L61Uq//9gRt6gA+OT+e7Kz+jPEIdS8NgZiu'
    'E/4PXeiQOzkaPpjVRRnSe7J+h64nmQc1xwNRPgRJy7etU+JhhJ9tdKSJKjSW1SeYPsx+0FgukBhTloQy'
    'tQzOzEqgUDX0fbWnMbByNyi6PBINj6pW8RZ63hkYOX0MCthiNj64exRcK5zAieOIdCYMcMyxI+BMzjBE'
    'Yrb+l/D4AOTf7OtUzNY9iSbhqverdEj6tiIFk49U63Y/uXaqusY74FJ03hzZyfLz+cfq5ivRNlKp4qLP'
    'sdFhwJxRWxhKFQRXqGf2+BgmbE4KqXab2DBSi2RFOq8DVrAu+GPv/PBKEp+ybweeKd7+cUoad+jvc7dM'
    'RDYxd4scGL7Lq4Tlm9jhy3hKoAiy1PngVCGllbogShjqiR5uuWxRn5tQhNrQqUvIM+tbAJKyBPjmGjiV'
    'yDIXWoRgJ19uKUGGghNcGHRjwLjFySTuxVNGxLL9XuN2Jj+KCMiWdl1t91EvZyuWiXuvsUQG/RlCoFnE'
    'EK6ZIl2doskzZDNeVRaAShBKlmSkK1m12HTJ2GqZh7evF2xrpaJe9hK7aduGjzeu5VjzGxL7lbugeOYI'
    'WPZg/Oajb+86y67lywwDTBIgX04CENO0vKzPHg08CzWJ7x56E6Fom26yGtVd8eYOaz4lhUHnE4JbcRTM'
    'Z+l5dqjK1HrA5Xj9wuf7Orlq87rOmPIOyFCsoeJiWpE/hCvhzpbWXDJ/r1y3D4b4mi7L00zgfOMYVowY'
    'BqBMNeLNYZkhidp9CAtUH80xQ9nS4G5Q38yDHPn8TnRCCY11EZYL8LGj14Y0+E43xodR/dHVLr7QCSIU'
    'gBvuuf0ZIw7ZIZhC5S7ygaITP5s4o1em7dMOesCDsNTc9cRCy2kz3SPowDNX8RK6qQljjMR93oLaV0Lb'
    'uF4bN2injLDWwYvNgB6y7+CEzI16ZwhqCt7O7gplX9PO9+15wg23inuJIiae2TbBwvml5ZzoiqGt3XHr'
    'AG2Wa61HE6Z+oU0rNiGq8WBr6AY42g2F7tYcOf618Mpm3MvDP6hVEpki2/QeQKA2wA09k6Ur4/DdAYnJ'
    '/FObPVM5VwSit8vCyNoiKIPFGY+MA9NJTFE9Vw6Z9uP/kQ/Xj8ueZLYFIWededBvKJd5P0nR7uzAYU7k'
    '5LG9veI2ODIMIY3Jl9gT13PpIAvylRcIDDkCetzxxUEBb53Q8YgNZLkLKM/UQ4MIC28N7veLlR36Lu7i'
    'Ipegw5BA6y0hh3XEi95vjzLvaASrLNGlNcbquFzWW75dNGsdddmZXsx9AXicnaE2rHpwslmv0nAVanAx'
    '9z3C3vcXxPehZkzSqUz0eB+Lo5QbGE3ndqAyUqhVsBT53LBoqvmiLXfJJF+VZBHzOma1axRsf6vsP6Yt'
    'DTRa0eSVlQ1Ys2KOb974/VJwXm79RFzn4HIxUUFCdqaARK8t+h9aD3gXBO28/exMfAOvG44aTS7TUXSH'
    'PlgfXpcdrZIu74e2MaD2+pdlOobn2UC5jF/ztxJy3bDzsFImpmBokoFw02YGXZ0Fq0E2fMjYobZpL0Wj'
    'mJnXY3Mt5DU2mpYupBO7gBZyQDrg+7qmyJQm4aVt0W4XFqnu8R7sDnP9emsbtrmPIYQIiAjLw7hgJutu'
    '4WI0lPSCCMsTWrg0+p/2YFouZzMvPiUppiQE8RZi6ge1BX6Z8I6mKTAJQC0y2LR+MVEZdOk0Y7r0kOXc'
    'Hdc8o78BLloNGVs9NwAvnPCjmYcwDW7k3QrThEvxXlV43pf0EmxoskTsCkMe+VjDKM/MLKLVAB5MlL3o'
    '8H1gWmAUSTiiHhVjnhOHjUwJJojz0d02vqOLJb7/ntBRiCJOiRj1hNDcicAhhCjvwgbyut7to8oLa8T4'
    'dgzM55p7ZducxoR03LeD4oJbQQWMpurMt1KrJ4nxyft0owEphixFD1E/nHMPTUxEnFpQEqU915bEjP8C'
    '6O9rAUgz567FUfv8A2wSPG1mRlnTWO7pVZmFV7eN+FNRuSIrm8WvXNpxpoPhb8umKTX9TTNW0BTHI2oK'
    'kCCzWw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
