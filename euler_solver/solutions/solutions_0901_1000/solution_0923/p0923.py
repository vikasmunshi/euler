#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 923: Young's Game B.

Problem Statement:
    A Young diagram is a finite collection of (equally-sized) squares in a grid-like
    arrangement of rows and columns, such that:
        - the left-most squares of all rows are aligned vertically;
        - the top squares of all columns are aligned horizontally;
        - the rows are non-increasing in size as we move top to bottom;
        - the columns are non-increasing in size as we move left to right.

    Two players Right and Down play a game on several Young diagrams, all disconnected
    from each other. Initially, a token is placed in the top-left square of each diagram.
    Then they take alternating turns, starting with Right. On Right's turn, Right selects
    a token on one diagram and moves it one square to the right. On Down's turn, Down
    selects a token on one diagram and moves it one square downwards. A player unable to
    make a legal move on their turn loses the game.

    For a,b,k ≥ 1 we define an (a,b,k)-staircase to be the Young diagram where the
    bottom-right frontier consists of k steps of vertical height a and horizontal length b.

    Additionally, define the weight of an (a,b,k)-staircase to be a + b + k.

    Let S(m, w) be the number of ways of choosing m staircases, each having weight not
    exceeding w, upon which Right (moving first in the game) will win the game assuming
    optimal play. Different orderings of the same set of staircases are to be counted
    separately.

    For example, S(2, 4) = 7 and S(3, 9) = 315319.

    Find S(8, 64) giving your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=923
"""
from typing import Any

euler_problem: int = 923
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 2, 'w': 4}, 'answer': None},
    {'category': 'main', 'input': {'m': 8, 'w': 64}, 'answer': None},
    {'category': 'extra', 'input': {'m': 10, 'w': 100}, 'answer': None},
]
encrypted: str = (
    'aSeJmFgL9icupI/9BYwGNAYXcArjSJt+pDJu11Fb64OYXtQSq12c4ie3fpheCyed9OQpTDVQJDeJUpDB'
    'ykRh6rhPXm1lSEx0EgNnmoH4+i9v2kLibcXH302y8PophzD+gKhAiN5eeasf1tAs6jDKa+WNMe7AfHsR'
    'YWLKU03a4/PomJ0UITKVrbvI6KkM4Ycq/lHZRsIGz3TU1H+5yhCeCjQXZyOIF/IAAo4Ok+zbiGdKXF6/'
    'kiaJHwH8AoHzGbDjGBCauW8Z2A1kbjxHRnc3RfxGmSN8MNbfofiXwd7ADVagImZJo7xCN+ggL9v4Eshl'
    'wW3sYV96cLDp+jrkpHYVy/3PshmEHUncKCvp13tCvGoVe9L0oa2/dy56bGp/q4toSxaYrWYEucpJHJ50'
    'huzY8TyPgeTI8DKImprjsx7wat80RzNg/pbJDZNHqWUupkWQK0TWsYFOv794EoTbMGTiA2059avU8TqT'
    'lf/Dp2RQCgnhHjiNiI21b2r9jw2O2J6JzSUdfXH797Loejq3VQlMxMtR02P2f31LdGZiYMkJAWpOhLOn'
    'JXPBJrAEriBchrSruBbGMpswpk7ztCbMy8VOd4k4KXuAypNVu7LiKGSG76wNX+mArT6AyBmbSZrTsztK'
    'J4cnzIQeaWe1uzKn1MpnwAsnp1PXv3QkzhvpZmEjxn3wjD7jPCtPiJxMT+4cBYtBdr3H3gddaKfo2UMf'
    'J8SJ0FqrGobRQ69zOIN7u6nU37KNaqzIWOEE2z0gF+UYsUQSYzLs6zKMd4fynxqdh5Jdmkf+24m0+pn0'
    'nce6LrxTh12RjHsmzZtrlvu3J2CtiuNw0Kt05/eF1SQfyCR1NlHyWZ7gnNvKdqlHPYkOtnD341+xSDkE'
    'hfK9lGSvWAJb9tOc0L87kJ3tCImbf1QR/kUyurza2JO878T5qEC2mj/Kx7/Q1Gx2/JiS9i8bdLURopTn'
    'IPtNs0RQ1AW5VF8HpMDqHW8So61Ob+Fhj3k4u4JufvSWuuqdCqseiRmvEtqmvLgLCMdEnWMV+OVefFjz'
    'EVlJMJUFOI0r74lArDXETH5EA94/LhKW6jTcnbird/3gzOJy6KtsOESZ63tkU08usPSKA0WuHd/i53wx'
    'Xfm4AcGHCV5NpT99SnBtb79OW6VLjQvP+RV8fo6UVu+Dl9U+zfkNju26VOq91nKvbhjNm1vV0YGjb6ff'
    'J2AjK9U5vdTQo4mC7zM8Xt4iS1aFN0iXUecCFbtUo6GwvTHF3m8svqqVL5It4zMhmBmojR9QRzwTBeS2'
    'O74RyLp1Qqe6HmCB8WLq+YMCy1XFHjhL00LpOX2bAvK+0puLANiHbJ1uV1Fdc5a6Ii2t71s2jrmg2uPR'
    'Sh1CLD1gMG6LW16cXxqPkqJRxecglO9ixjYPiFu8dmEsgJE8knekySVF6wyfu4ta3v1MlrHThkPwJCi5'
    'NX5E0Q6gsLBTdfHXhY67hFSNqCv/32F8T3bqw9cTKLKIfeON0E+Q18UX+2+L9EsBh1mTQdSeD+vaWXza'
    'uhmaNEZl2zNF1VryduASWDBQIwbkQMsCPB7fDXQ8vm5ozc5jafdrFTPUzaizNuP212pMixRIZU2p34WZ'
    'if6KjPxbEXPFVxA0ke+jsEcYn9oOvYIEgsWKNSCtx64Lv94RIZ2+YSn/4Y43RpOEIYaweZRGnn2ZVyfl'
    'BRXKjEnpEQuMEnn+rgZJDbMjEEjCn/ZolG6K5hxI77akM6RJjhlWaRw85oth2eA82ecvc4Us2l9OpZus'
    'OZadGbhGQxnmH+1NxWsJbf3D+jKteuhYNDYZYkq4yrQQoYwWzwftvnxnZ2S5GjZHFKl7knyIttmUWS3I'
    'HACPP9v5HHhLA+banOsGv47rsdS1hHURzMkm8P8A8SWmWDaZUEpMzGBKWhuVwFvox2XuQWN6qQxFM53K'
    'WffPim5DGlB8nWg00AMn2RAWIDDwZtx5sHXJOKgmTp3YEp2893TsUynRsN2JQ/oD4kjGz+TcnFKcxdVr'
    'tqI9LalY19P/Kx+uLXFr8JFEyigfsYBiFaM2ehJd2fxS6vjZBFtAKBjvijDKXv67V/djTuwjdVSEG/x9'
    'TyrlUJLSmwhEZd4RCRBgntYOdRLQaFAhc05Ug3H47YKgO6YcgkdsdxZX5iNTppgxZJKo+RrOakOc5yYb'
    'bsSZP70yYT4aEiiEp8ajpeltK9QiDVGwuQKj3E7BINoD0qdHqxLGQVTemRvjTkrPlUFTBCB0nusv3/2/'
    'JNq0wWbT4pghivy9UqIJOyJsjFopVMZhw9LUfZOn4dci9NOkWLgVDYQYTt2qiqnMqYLNk7narh+dJDhj'
    'JixJmT4G3vNQzyA/rwV6NXCkQrGlOlwPEbCoB9kE2c7PU+NyF33n3h2F996Q4SxMx8PQFioAGnqsC4R5'
    'hSM2qTvYhLWLbeGGYncK2FF+mcuFK+gAvPy537zYTuiqzY2CgsQTDl4P1XqGFP+qhGIH1WMTr/bkVI7S'
    'hbqz7UtIUUvZ3VzZjBU35r/qTx4BpwkEZUBmjsl7ewka6J67vd5F4LSEPyyRbpD3NOGaFo4IDG9hZeGT'
    'kowOeZBh7eXnAO3mmnfscvtNBo68qRCZJFeGxOGiNVMPXpZbw9zfnpHL0naPfl091YI6IZN4hUxZNKSn'
    'EKF/nMMsr6OBba0f7fRLB92VU0DCjMe2fIlBlhr+9oYJZ+b+B4ekphLkk7Xu9JpNnLBAaIa2TyRWZ8wE'
    '58hoTVWX2zEyMEzen5lMPC9GVyVWt9kDveZqlqsDQot9prYekFn7BRkaVDs93JaZnEIqlfFRKAS+ILRT'
    '+J2UWzjpTSHVQwKmRSUxq7eR8NOq92el63OS+woi/BQ5cLe7uu3N4BTcDGTS/WofScoTszsYEqUFx8Vg'
    'kduxUHj/asFYWNb5JkDsnd1UmAvLp1Vjt1idfK6/7ZkUVANR1DHS4rQ+RS9/L/GfwysDRySOK4peBoJW'
    'tnOsVqxXpv+tn6k4PKeBOHhYTgM0NHKWTMRdhP5aI65j8SQm1j3OR7n+zCMJ7Ba1dA3bq/8pRY48/8DV'
    'VC5o3d7ukEBp/B+AK2380GqJc3/mQrSeie3Wf2PRr2sdly4AuDm92ciL2Wq3rjTAQO8S3Cwaew0HcRxo'
    'TPUsS35c6pRd7QeEJGJAwIrpscXlIuAqhP71y0xm8YvZt7t/Dj1y8T9KRGw2h02SQKvseJ/53v949DP2'
    '/8WHX1Mj+6FGyl4UhI8VyKEUXymCX7ZuOeRgwXm3bSkR1CB0B4FHcJmfcTw1abA6uJ3Saqocas6SOwzP'
    'YmAU6GwR2QtmlK8FuD8A5VgVp543RlH6ParWaW2Lal9e8IFm1qgVFYdRwkEpUJO52OBCEePQrGg2nbJB'
    'sBI7ROP+WSan32yQ1crR+YLr1HRV//+tBHizARrPYjPjUZw/wrIWb+uLXfVroDpB7xDKYpAF9q5buklM'
    'IhlmwFmdHRq72iJlJISsKLyjIDE7JShy4E4h182zHaFLgLMj/ZCvPdlw6JWC5SPNA8yXcvnkt1GrnMnJ'
    'MULc58Uu2f60n4tXwU81gNRB6howb75jyHUvVJu6VCSS+5Bo8Buz6BrSWwNzSllfpzgIi3nwUsS9LjVC'
    '7rFd3ehnT3DMUHq9HZvM7O2rPn3xiFh81CqY+23XAIJ3GiRBOGEDlBq10ToCvbnzSBiUDPYkK93vjswv'
    'Jmdo0JCGmxsC6GcBeWTZlYfhBTC5Q9cm7AV2iQYH9wK22fOIt8igkzCEFoM93SOH51BhGrspRKSD+sqF'
    '/RgwVXncOfGchWWfg17AttqkJzr4+2QGgF6sXggI64gt5EdBwD9EoVPbD/FNkTvghKNe4N6z5a7Vvi5j'
    '2zMY93fovSM0AStsNcX6nFnIFtAqKG+5/8dhyl60iRmnm5d43Mbqk9UcUsiLgKnIm25nfci6jVYkjerD'
    'FH9S6ejiLJkx46SOeB1PhSghAuWoeIYRhuWJpnmHNYxFH+pE0U59TAoMPW672HCOstSFlz9Y2+OutbDo'
    '93n/nYVIZI7ShjXiCgcrlNYdDKzaXjJALtU3tsspak/b7XJJvTjd8k0XB0ELB9P833+iNWr3x2Q6fVUE'
    'V76thfW81WESvTzPe9BNrSbQcS4sJJAxUtR0t2WPbKX9T8KlFB9kpGytn2+PC39/afOVKt2pEvVEK0Kx'
    'SsVxJq3LZF/kMI34m8wqnA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
