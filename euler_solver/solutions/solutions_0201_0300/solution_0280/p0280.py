#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 280: Ant and Seeds.

Problem Statement:
    A laborious ant walks randomly on a 5 x 5 grid. The walk starts from the
    central square. At each step, the ant moves to an adjacent square at
    random, without leaving the grid; thus there are 2, 3 or 4 possible moves
    at each step depending on the ant's position.

    At the start of the walk, a seed is placed on each square of the lower
    row. When the ant isn't carrying a seed and reaches a square of the lower
    row containing a seed, it will start to carry the seed. The ant will drop
    the seed on the first empty square of the upper row it eventually reaches.

    What is the expected number of steps until all seeds have been dropped in
    the top row? Give the answer rounded to 6 decimal places.

URL: https://projecteuler.net/problem=280
"""
from typing import Any

euler_problem: int = 280
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    'KofkNhoiddfHIWSTP8hk/glvmqHF2YrczjHmXp8ssHoXXuOiQ228KTs19cyPQfHE7gTLXZSrol2Wp209'
    'Va1RQvS92PpmEa46lEJm0E6RXsuVypXtCnkAzy5AG/Gkh+FPQs6OWWzsmLGPFM8vVMXshtUmxUkDOL94'
    'NHrX/v6VLv+DxKsDARghl1T7+g5TtmeWFjFz52zHb41k1ZY0/s95eEbU/i7VWlq2gxDSqvPnTSxOwpKk'
    'g6v6mzS/QPzeHFWvx0V24igwM5yw4df31HYhJh04Q2Lur8zK2ZGq3hPCCsvPTdYuL2uxtITHIPfFYq90'
    'vVmwwHIJp9MsB1ItetzG96+rbpceMwhMexUgc2uHbxDyb4z164km/WOJ2Q93aoTr5VoH4RMH7AlRLKel'
    'ac5g1efP5xSxXjNUJQDXbO2UhfHMD2CYvevCp6I4A9WX3ON3bCjTTTmWUm5YDasoD15DUVOv4Jm6md63'
    'G+AhXQF0hHD1b/F3Mpgl+E5J0G2d1h2mPKipl1qR1ZqnL08AlhNlSKriOcp0kjYvFSw81MW0hFUhu4iG'
    'W+AR0JAt/TnKJ6OB7RUdq2AUxrw0TFoLPOuDR9NkRdryoMQwl5ZuJsmFuMd2wXU8JbQ7oiLdDbwhRWa1'
    'GGVLRvyJv/5ISmK1eN7LO87XThV6FU33j01NHx4eZ+PRRasyh41dRXLAcFBIpLM1K2MY0I9ZasjXwzlJ'
    'UsTzU0prDbPrPciqZ0NcYKnI4az+4a1+3w5s64PoZ+DLtg6YTpGf/F7DCLqVr53bTa92pDZjvW3FkoHl'
    'IRf76DjFIy+Io/5hFKeyMLrnplzJX2ZigetvJH0/pn7awu8RARYZ4kox61R5XHTlXBFBMWMoU6eYXuXQ'
    'NBlc61dAR5n/cgKexxU8W0DOoHsAmvPMrRh86RoaNo9+eLpSlBhbZ0XclPQetwUkUI/CY5Jpp5zvCNLN'
    'naXAX6LFxuFVP073Jnwx2SbCaBHFKHbXOrIqdyIaf5uaSVkDd83zW7VfpUJmdvKXKCafq6v2DSWue5zj'
    'q3hUG/LgTgf1l5Mf0SMHAzO9DzzDPJRLoAzisbS/owHqGEkHhUexNvzdB1gzOWdc2u+WX3oetxKsNqW8'
    'tpik8dbKkLzshvorwY3r4UNvHTW4NMhq7jQv9q/j5FFRDdrIVYCyN2VtSi4iXzIaOzJBUShNH9Pu7Elx'
    'DhkZ7c9xYaDRV7De3UN/H6XNYQzt63Xtb9lpIt/6GVF8f5+oMPsoRq6wbgU/oaN4w477x6FwCrZ44ph7'
    'aTVJeZme2XzPhEQYxEVCRjCZFEW6SESM6SKtFjbLWWcY/E9woZqXjAjVs+SZa8RK/dSI3dvMyQlDRNyN'
    'Naos44ZxHR5rhPYccPru6P4CR6+2yyniVXhA4OQlPSDgvYao9nF9hwwSR83RIo2dgMmgdmrBlqn7NY1B'
    'E7Gpih71qlNQE+KYTl9vJ4J8e0UEpdK1VpzX8tTiYE7yJCb1A/CLOo42fyzCbSqSMwGxd3vBW7YnGyfw'
    'YxMBTLPaN2QgPsazNoWsUqGKSfvAKlgXnCEcGBwqcf5m5m5I10DPNsHneRSP3chFA/C+5jMvTGqEalhj'
    'eNiSQXafX4iI8slN25abllAsCFpR487uZfx49dx8HHTE+5XPzUoZGpLn8RYIk+ukxDfuF4y5kUyoyhdU'
    'Mut6SCXY8fUT+OMsKE4zOU+F8xP1yH/ybD4TUU8CcEMezlR+nzbHjPW0qTZj2aiX5I+Hto1O8IGr4voY'
    'xBSEp5aJCj+UodgkGP8d0S0AaxeLl5+dP2a6plCUCQA7aOV0VqDpLRtq5iXtWgJFH8BFa6skSROu+psz'
    'BjDc21joXyMp2hJGjmROHHr3PWshDRIiChxz3la4aboJgzp4v5YqYTAOb2JsUlXUVGJnVPuQFZuypCxU'
    'zniTLw2Xeh1mNUGDseXmAbK/F9agElfkgyyTBR4zs39pkRXyjJdakwyWI08kjWYiB31QoUEJ7W4ks6Wz'
    'PPJZqNcPqEG+IR+sanEmZ6yumosoJ3fmmmvYB541jKZj+KXerYblgWXqZk8R5Gy0po63eQHhQDC44oWi'
    'aj4z6GtIFIX9k6kRHnzd65pPOHEAvUAJfTo0QMIFw9PP7xr8HxQJv1eF5aBZgEdj1W7k1Qc4rhh8RONI'
    't1GPZIn4k8ilZi3MDOBoUIErTnBKZBXpRGhmg7FtyEaoQqEJt37GzxrCj+UahzXED08saTG15hCQe5Sp'
    'eIZ6JBkcaKQ6joh0KmVV20B4Q83QR60tnrmIzbqKlM2iGLGkhXbuoAiKL6ixQv4yaJCKw59f/61awlQd'
    'Xr3F3uZ8Cg//qdnb7JYr5lWmOMffUCSHHvCGq8y1l6xzPxWyr+bc55uNJIjEg/96ghy1U3Og5KnyqK9O'
    'JsqohJKfW4JVXGeGaUFX/mCMjj4ccHj/Y+2Pqg08wZRH1EGuhz6Kz0voVXfptOxtrQDu9pQpYYN9yj7u'
    'XDeUqG8dYurR3dYYWInfkY6nItpDK8oo+JMS5YP5vj9cINq6Mtk5lbkCntIIRzoavEc5VLz2UbXW0S+q'
    'DkKp/LlpeHZG9y6riwbT0US70/DcpxzT/+8dy/hEItRegra6ld9nMnupYJM57/O0pHZ4r7TIsvM5ITzL'
    'RmyMnbRySxtBQ/iDEO9Lvu5ExLkRzROi9Q4XCWjQFdwjmRSGHamSGGd/mOhSK2TREtL1vde5O8lUgACh'
    'WY4qggP4pTv/x46giDw2nqWjFqqgnzghGO0EYnnZqOPq3YIQAi/ojvW/KS01IfgIg9YhNKQeJmSiYlVN'
    'fMurXOkNm1p48sSeP1NeNBBTdEWGH61SD3PHju6CDI0pIUcHto/BdeGcuT8+qcnLQ914YRXS5QT6UtSx'
    'c8fQHW1Ivm/ZskWOD3SzvNO2Kohs4MEQmzHuhypJsAg='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
