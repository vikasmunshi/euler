#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 244: Sliders.

Problem Statement:
    You probably know the game Fifteen Puzzle. Here, instead of numbered tiles,
    we have seven red tiles and eight blue tiles.

    A move is denoted by the uppercase initial of the direction (Left, Right,
    Up, Down) in which the tile is slid, e.g. starting from configuration (S),
    by the sequence LULUR we reach the configuration (E).

    For each path, its checksum is calculated by the pseudocode:
    checksum = 0
    checksum = (checksum * 243 + m1) mod 100000007
    checksum = (checksum * 243 + m2) mod 100000007
    ...
    checksum = (checksum * 243 + mn) mod 100000007
    where mk is the ASCII value of the k-th letter in the move sequence.
    The ASCII values for the moves are: L = 76, R = 82, U = 85, D = 68.

    For the sequence LULUR given above, the checksum would be 19761398.

    Now, starting from configuration (S), find all shortest ways to reach the
    target configuration (T). What is the sum of all checksums for the paths
    having the minimal length?

URL: https://projecteuler.net/problem=244
"""
from typing import Any

euler_problem: int = 244
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    'rxAUW7V3ug3qLeSQigCDAH/tLog7qkSfMImbsU58CVIlvlys8G/3YZpMRssJVg3pluX4B8NRpg2Ej74a'
    'ari51gPcC6VnUpl3/Yi0R9whe/DU/TaqNjab+Xny2Dj96kQ763q12fsGS5KlQDeap8nMgzA8SZ6Ibtnj'
    '9K82DQSDRNNDHWV25KyRZLNtoh+zgHXjHXkf1RZHsuiPSkFTW4ceKhWzn33eetinj5dfGrb3S+wDlzE5'
    '2m8q8emis7vXFJOsxrxyscRTj8H+rVSTmZO+A2QG6lemiO84ET8t8gwwomQl9+pAgGiwIwBefGsG4uwM'
    'tZSQuqEOX+6ii0Hd4P5ziYkZl9aA6hvB3mVlQsuI1mc4QZQZieAZV9rLG5UEnvQAYYnjBmAubtZgPrSv'
    'CATXhzU0KCI1J56UUwr8SnbBfn8+WRRBg3pQisxnrYp/3ZD6CWrnH5OQhe88/Uf07/w3PJmiCIJqidjd'
    'oT177Q6gWgW6epPKP3zBm1Ug05qCQPfwRrpjGXzUXQfYDYCZ6BJ8GJ/G4J+CQKme3TavbyeyfCoTaey1'
    'l97poX0mFqq15ePD6W1GWSYddO7ZJfIF0L3B9FaTKci2AWALsQGvc2CS5PNcicoCJLjlAZ9oMfgc0Fe6'
    'r9jEq1PezUFQSU4nHN61Fg2JE1xc19RlScQ+l7K7jXWBPDSWZbw6a9KTcYksbrLBXT9BcLn0VWvOrIOo'
    '7avYyrpalO6KdtXeWCYDd95C8zwy/FbHvaMELoqsAbJWIvZXLSmMy2oyegU4381sha5LUIitvH2ZUDcF'
    'DQbFG2/wb6m8gBdFXQKPM3dohqPnaLeZIGnwyy8xMTuNUgU9AVYRXBDlr0Lmmc7f4EbBXFlmBdXqoJrz'
    '+xHiZyT+1xg5Pn1iVWm57Bb/Y3wbAkkWIGdPP6PBRT/A85mS/mInWFkTxlonqB8tugsr66AZx8mH8uj4'
    '+DuOQEJtM8Scf4rZ7X7Zl0j48iHDFsYXpqVThYmsUvbvl4EEjIGGV3QD3NmXMo8WN9KLxhiAxjESUj1O'
    '++zcKs7JPo4U1if5RmfRwcTHzNwRFPLNjCkk89/Fh5+1/FEGP1T+q2CIHCpEc67zwj948xToJHYRo3CE'
    'ek6ghOZR9O5AqePdw/NYuUxA7QSlcOnSVYTPGtYEbSkPGY0Pv+8UOSfFfI5ORmUzRVQ5VhKfONJUVLQt'
    'Hk5+T+CHytcS4DjZ9zk5FIgikyps+BuFjAu4qr8gMoU0Zen/JrtiMvblBG0+9EyYKm5xzLOWIZ/AfVID'
    'WnqPpLMxRlcgRLqh0aZ+seNbuOtD1TwCVI6oYyTLuE1mCcGWWGU0rs55j3ogv9ssjyNovYd1gSIpkIBs'
    '8COJGLcyQbNyC8ngxQCEsfP5PL8bq24aSGRISLDHftJmlcyLKvh6ZlfbiRtDkXC4EevARNSe5/GwKwoQ'
    'og4ncg/44Dt1wgLqraNzZ19JyZgwVHQVjK8Q3Zxe5zSIghNCjvxwX30wmI7sUFrShOiIjQhwwBt4iBHY'
    'G1LyirlRXGdWInNA5AmjjBqsOHzB7ZG3xnbSOcIf+LXxDvWvNvbb4TTZgamiXdAgWyInkGHiepAQ0+DG'
    '9orFtQAu+AUmk3oUDkhQ2JGG0GrHrT03/jzyhKRQaLVHDMy1mTt7UFGdKwGWrYDKVbYiu+lwa/PxtTEB'
    'S8gKCm+G41tRNAjhjNALGndhXxS3dPgJ/66rJ/szg2BQmaNxKqg9mPwK3r+1A246iUqq7mPBYjT9Pknv'
    'jGvPFwV7VaXlojZt+8U+9NQM5F9wOuRS4myvJnDKMjNwAZi5w9CXrIGB61v/b7bGAKEZsqYIf7iS9B0m'
    'B3/lt79OC8ofQfuMHNFuQi5cgIWg3KvOyVd5+5J89tvVMTEr1DvxcGlOpDJrt1zS7wycvgwN5N+dChC5'
    'eePQwDJRXNSxsjv4lW0By0QX4xdnYma8gCJY3R3RheXCgQCApqUJu5CrO6hFU6AvaFzVA2wY9akyYNuB'
    'LERo35QOiveR62ylhhYt9jNlCZ+9PCrxk3AsXEG9P3Qf462lOQfdPO4uuEZc6VpePYRsIy7F6OUlguSH'
    'tLDZOfwoRJJaPpPt/Q07JoQm3CagcWq+b2dJ/Ov0RR7PNbtSdJ9YICxsH1sX79r8AqQHklpjKZpTEUJX'
    'EgzENsfctjt6V09lqsr6xa4E96JqqXeOpVCUP82sDmbCDQ76ZyDZiE8qLbxHGQvXuL0KD0yY1GkEG8Yb'
    '566j2LzWx6dxHEQhjxg3gekB+dviLWKFIgxS3VJWHoRUIrXF9CGTZKRjBzIOAzp9hZ0hqqriHoO0TZss'
    'cRDZtgCfdq1kdTQWjvlPX+qvefP3zUyGX8b/hwFfYVNo06YrxK8Anva9cfSmcq0iCBaKOlciL5h49X1r'
    'LWR7Fq1hB3sniqS7MGmBrqLczduT05XnaWMyXosvel2DU35HDZVYUBK9dyn6Gwlxk2Kt6EP/sL8VAQMY'
    'NbArBtmoGUdPn3/2a9sL0YDmuZTHwAqbzYcd140/srAu/CiIsUehfDtBwQpdPw44p8OwTlyTqOIcaYZ/'
    'wN7tKyy3KEPOR0tkoToCp3didx9OSpr77D72Ng9i1GMVVGgzx7+hqlduY8lJQyeXu/vjQP6UdWvd2KZs'
    '2k4s/vCCEKH5XwtrboYMrkoey7r+DQdWVWz982rmcRzCm+oydON9p3y+F8T9N41ACdA8te9dnanyjF+O'
    'IQg3+1lCzrBbOpGxpWk2Tqwy67GPhOT+hoxNRIb/iwqTm8rhqABWQB2ICORsxfZuXc91kx3U676nyPsY'
    'cz3ki6h7/e/qZAhRReVd54e9xLK9wREOyiiN8jH4u7pNlBhFpcW+CzTfGrESCcaGR6QWHdMAl9XR8RX+'
    '+jUSEvB9GGK4F8G39ta3xzSRh0SpIHfOelb4Wd4yYNexxSF+mmOvMsDeVhQa/iPjcUUYrVGq4LcTyCsd'
    'wZ0gfXl3EmScBfM9z9q+WY3K4zQ2OquqcO/e7l6Uu7Z2RxLHD3oupZnl3O60VQf9EZgFBMqhlu0Qjk6z'
    'Cg6rAwYfdVevQJhdpzCiFXPe1Fe38VZf+vuwdk4LOIMjveVQ04drYHqG0MmZeC67WO1uRTrAqQ1B83W5'
    'owi594+hXtIjBci7R6RZxszLHVtvG2hUiDghM0xDrJJ3X0i1eF1Vul7ucsFX419bXE9ctjQlraYfjEJ7'
    'JbkBFpHpqBwVC9TAjyaYiSyprwNL+RePHzR/6PKO5CLCK2WfBW/jiiygugtoXRR3ZWPtEmnLBYJe1QQe'
    'rQZFLo2GVz68EB6+wb9z7s4nnKdSuOEB7QmrwnP6J1KP/PxuEDilFisE4NU5L/EPU0bAww=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
