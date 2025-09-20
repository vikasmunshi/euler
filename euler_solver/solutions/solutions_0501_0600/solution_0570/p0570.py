#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 570: Snowflakes.

Problem Statement:
    A snowflake of order n is formed by overlaying an equilateral triangle
    (rotated by 180 degrees) onto each equilateral triangle of the same size
    in a snowflake of order n-1. A snowflake of order 1 is a single equilateral triangle.

    Some areas of the snowflake are overlaid repeatedly. In the above picture,
    blue represents the areas that are one layer thick, red two layers thick,
    yellow three layers thick, and so on.

    For an order n snowflake, let A(n) be the number of triangles that are one
    layer thick, and let B(n) be the number of triangles that are three layers
    thick. Define G(n) = gcd(A(n), B(n)).

    E.g. A(3) = 30, B(3) = 6, G(3) = 6.
    A(11) = 3027630, B(11) = 19862070, G(11) = 30.

    Further, G(500) = 186 and sum from n=3 to 500 of G(n) = 5124.

    Find the sum from n=3 to 10^7 of G(n).

URL: https://projecteuler.net/problem=570
"""
from typing import Any

euler_problem: int = 570
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_order': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_order': 10000000}, 'answer': None},
]
encrypted: str = (
    'qcre/V3FVf0tu9zhKaFitayJ/oupSZjA6ZhTJ/Q+GN9aCC6HYuZIiYDmY9brfNdKGkErFYKtrecyP4vw'
    'OnhM6sfVE52E0eJ5qjHcL+4qVUvyLwqTKMpyZ0I+z1S3hvFqzBfA2cA13nzphVoSVWDuXxYuEtWG5FwE'
    'AOIJZr8+oINABqLZ5W/t5TS88xhVV2qtLUQsQH/5J69r6LiTKIBkyEiH4TXa9o987WpllGEyiIg8iAGg'
    'lgylqBDG1990mG1ruefdGbZxfVu8ffrzxKCFK0Ftr57LSmhhdqDEKhkososgb1Mtt4tICjCa3mzYLhyE'
    'WU7LxoFWxpTmebNqIFWFUPcflDr3FcRxGrpSjesDJ4AY7WqVldP5F44VkVwnTcFelhL2M2ZIpG3Jz/Nr'
    '0bzn9xmkPz2r/KneWyzVN0PpdHJP9gnCP2uSB4ixqUj7Tfgczpn6oAWNMOaFbDNb/N+nVwxwd7cPfyHg'
    'XpxvmoyGgxJmEgXsQPHVA8XurCLnmhK6Z430F384GScjsjPXIKjr453N38sBOxFeXxI9REVuG2rThpeh'
    'lfJ6YW5KeFYl/K02g4juVvqX98mlvyjNcUBU1a9wpqQYLz0iAuVJnrXyzDZs5UZo2UKnN82TFE3xRz0x'
    'kLqTtJGRb9QpYa1FBjIDqwwL1FKS5RIx2cQYyvFvGja9ytMZBYSN1bG61UlX2DNkp416CcdH90Qm6BPw'
    'fr3sFL82hLfi1HDWdAQ5HCgYWW8zA0X1M8MrSIVlC1nU7a434EVSiv2HTeXYeb5NPmwWmfWp/9Q+N5a6'
    'Q2qKrGMvDzQWGQGM5tGEBe41sIiJsDEXycKV1QqBDPTjwQ/urdADs8qrzS49CjN1DKl6GDmTGIFE6FUs'
    'SBHzB55wN2c/CoxhMbz9xBlwrY6qnTUYWXSnipyEglklnpTCiSblyjWRdJVMQ6nOuAkPZDg+alcZ7p8b'
    '+6BCIXRamKc8Tp3b0RpyT3Gcn1p/wU6r+YQQvMzcIj+Aw39PLviBvU9aMQqu3qWDS62v/jAD/WMjJ5l3'
    'riAjEN7qDTEl5EuvFMT678YwXBV8UxUBX+bJprHIfZDXHfaymeln8gbfiOUuR7lc/SfQck5XUWV6x956'
    'eY97jAhRpAEse0NT2Z1gMiT0sjwEJPLrStsvFNrIDnq9UHlIPoX9k0er0nKvGO9+QVB65EqQejo96gxj'
    'W06/ffXAZu/IjLg+tesr+ypwW7FRKv331JGI12hskd6G7F2GZXmbMPH1L+uHFevtJ4dYd+8P+5jsl7s8'
    '3Gzh7SU+6tuQ3yL/StX9NcFY4ZU3YxnaXlasw87u2r8XJ0RXBR/K7UUt/NZkkb8F6Oo++m4Xnhu4O7J4'
    'TQ1oARjkTcHM6+y//aOO/HFwBI8KxPXsx3JddSGAuwOUh+epqKnphGw7nmoHNgw9/RhPyf4/iUbjZVAT'
    'SuAX2PxUJ0juTreib/txf32ukq64oK627MvXuT1PluzeauHigjec7txzsSum8+SNkKzu7ylL2wOKdntF'
    '4DVIOKLxq0V0/IUUICC7JCXJYmh7z0KmL4fA1mbA3g9LrxNDnFcAAEZDUIWhlZ7RM6N943D7W967zanr'
    'NuxIOb65NRa9RAXUrwq/3OqI3mkWUQkCSsXjbg0glZssjYHvZstyKYPNyI92nq3Wrrq8/Dpg2D9xyAe6'
    'dfgCwg6CQM9kamcK/OxqxGfq/pmMuX6AU9UFjE1jaS/G4OUVbmiWmrG3h0S3fGZjyLX8GEIo92/FkHgS'
    '6TPw1Mv0v71l6amwMrOaDXsRGm1M72XXoJ5DH+/bZNGFhjhJNJ5e47TAIrrmk3TfzZd1cKQFpE+xt0ZU'
    'ggwfK5V4uuU0ag8FiSqd/hgMmyRjrIHNVHHK0vgawGYgRlclhobzTAyo4OWzjkwPqFbTAF8fTsaXF32p'
    '3b1vQ/7VuR+KFu9jIklUJ5NQ3bR4Q6SsR2c9VO97KMxyimb1GvUuOkyA5lHvKDXHONM61Ci3hw7LnuZP'
    'd8aPDlxA1W+2UvFpNFswdJn18At1arFsiQwwJ6GIgGcz2kBGz9JDRGfPYohFOeE71nGfklih0GcEfDR8'
    'OdKRpUBxamx3DnIkUwYx/mLKq3o3f1Nh8xFvuZnLp85pDsc3NIfym4qJMIIeLQRcdizfEuvp/v9sEdvR'
    '9bKQH1X22k1zvS0mavGetVT/8bF0L8hEkNeNO9h+UN0woE0aVvDBXwVPXq6QgglFdiD8WzhoMYKMr4Ga'
    '2U/UdxeTvuZ+K9jD4kll7eaPc/wJb4h7U9QdNFi3ij2hWXaTv+likzGxfoY/I2T09OPN0bIyqne9J35q'
    'C45/l/ELPgsx5n8ALfHcnglTepjhkFclSNnmjaUiIZCunV4qSzdc+Z5tdPlqDrLLyvkOnxS8GjDDRbKD'
    'Th9NuI0AZjc92lNG66tvKMjojo6v3Qj1fcd3wIU3j3Gv8FFORvjwswyfLj+q/gpBPvx6quT7tcX+5/Eo'
    'h5J2G2cDBXH9KWPl9EVaOfCwqvseEMQVN1HdBK40v1RtXIW7YXIt+3VfBaaXBpZRcV5ZUsgKF/FodrVb'
    '+uonsU5+jj6GQ4pWOdtQfyq72FvanCc9/2o/ds0dY0H4ZYZk7x0+9efEqsV+IXXLW2fFfNF2/RL/qfjy'
    'MZwnTJvnOIieJOKA27oOuRJZI7Mf1B4XH18kyxAP8u0V71Ruoo6XKBpvt8lqdEQgolcN5wCTzLduaCx5'
    '5b+lta5fFADNqGLXRjSQolZ2cpiS5qeULs/4w0yt3vaIZ8TAVwqfp4TumyPmgNeUDFjmF28MMsz8R37z'
    'lH/AVKQLqnVZzW9M83JcfaLWSpP19mv+f+mMuSIQkiMWBTPJ8EFhfCsuPrs0L8YE5lRPl30mjCQHdTxy'
    'aBMuncCeB1lBu7e2mSJFoRPqlCLdmQomZD/6OJfqsNBQ4+gtm5MT/sQfa/HIvrh9'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
