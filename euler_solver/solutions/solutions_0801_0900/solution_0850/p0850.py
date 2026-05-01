#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 850: Fractions of Powers.

Problem Statement:
    Any positive real number x can be decomposed into integer and fractional parts
    floor(x) + {x}, where floor(x) (the floor function) is an integer, and 0 <= {x} < 1.

    For positive integers k and n, define the function
        f_k(n) = sum_{i=1}^n { (i^k)/n }
    For example, f_5(10) = 4.5 and f_7(1234) = 616.5.

    Let
        S(N) = sum_{k=1, k odd}^N sum_{n=1}^N f_k(n)
    You are given that S(10) = 100.5 and S(10^3) = 123687804.

    Find floor(S(33557799775533)). Give your answer modulo 977676779.

URL: https://projecteuler.net/problem=850
"""
from typing import Any

euler_problem: int = 850
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'N': 10}, 'answer': None},
    {'category': 'main', 'input': {'N': 33557799775533}, 'answer': None},
]
encrypted: str = (
    '8rG4rBtEmgJiNEhZuSt1dYVQCsqzPNIuehuHqFyOsGn3fP1pqzDBXu4BWOp7GPR3d2t0vrLMp9tdMBRz'
    'TpocdKHwg9pO7uDhG/gWe9YytpVoZicFrFm3PK1eiuVbyU3tnAS0MOM2oFl71DEkCWOi2Zcs4gfkGvdJ'
    'G0UWGBX99yKZuYoKQ9mt2T5sCFNAAvLIBJpYO/sNQJ6yQ8fnGgLlYDuC8p8VhUzjlA1r6ZRSTAWaDpEr'
    'Pui1axj4oCIjnSY6WECl92io3mgpxR3MZ+rt2WT0TCrhXXUo0fVIKE5wT/XgVpFo7M1R8B9RWGYGS9cn'
    'HOlkFK7H2hjS374UyORJmyx6EhSbDwYKxXpztMXnHsnY7IvOL9QXYLBWWXoXiRFyhexjywoaJTZtuFB1'
    't/MZUTM5T/vkYlqHW2JYmWb8+JgyqV/B4R3eZXY7UqPMblmCD0V77Hei6cRFnOTIKES7XTVre/YT1TSP'
    'CRDUF39DPRj2JHKigAiBlS4dFi0zNusrHcAyWKPuvDYSbaItZI4d9OoqEphQtub6bd8HPj7rA5L4Exgo'
    '6+nYNpJ4GDaXmxzzt5+RH0fti25QyMnpx9OG34pwgavd4EmYsVX3fjob/XOSMyyhXtfaNFem0okTRHew'
    'laO6OfuVsdCF0qq4TijiJAKK/j659t2PtrsnN6Ipbyt4cg8xtyRtWKDrIPwypr4wDgWNjYa/q1og2CKd'
    'mSJs1V3mHoPvbsYCebAX5EJVK5OFM7ivwY2K+8QUVEagVj/Nt6NzjC58tCjuKVX9BUy5Bc89nsBXgwpB'
    'yQ4EDOmyxMZ1pp8hq2c/T1Hwz6DR9pUvb39F76zGPX771QGRvxvj2ykch3tjcIYQB6I5laW7T2KgeYC5'
    'lmvNWaYGhNFs8nQyiuLc824Caytnj/hpkYMI/zCGHvwCIB7hrBYrvJpIxd+COCOZEjBf2FyKrLxmyqNN'
    'dhcf5HzbIxRMbFpMPxIJyQ+tNcCoQbLCU2os/8hks6jMk8phLF8Hp5G6Ln7pC2TzPGFaL/MYkSousxuK'
    '6Dlr+pixIzfyCyTXb9vGMP/kQrzSXNj7IYqNkgAzD9yP1E0rZrZx03A28S1eRYrwQKMRM6wv2N0G04DT'
    'w3vYIKcn4b3yeWwlbMDZVxwjZKCj/aHm1cuaRQJXJreZMRWbJIgJrtSWsygWztZ7CCCBkNu3ivUdFED5'
    'xdV6EzbBJAse4aKazCMPXcVCCVu6aM3q0se6TRmE/U/J+p2CxarzKsUBaSbR5d25oqanXOnAHbcgc6LC'
    '068yNfoQAiRspOqhvPvpHz1wozcvFrRnlALckDzpaLFy+1jf8wJvo4cevF2kJPe0B2fRw/FUgVtCyazP'
    'Y9sSQWWwWP+vBwxaAwsfStqZY5EUf0QuUid3w4aSX/Jb4pZtqJKms3/YCcKAUWoi65kVMc7D2RyCFp6n'
    'HP+vABm7giJUSMRFCyDyjoEDogIUe3yAqwsLlVZgd8+C5kZVGRz7FCyJolnMfwz/zyPLWNOGRb4fzTRL'
    'ty20LCORpi3PQ2v43mHRrTqh+nx79XzEgITNeggGUrTVH9lHfNAc6OHhLhZSKGUgWYepXaXB7vLMMzqs'
    'N3KNLRM7F+J+sEibIXIPmKCqFzMDZVZR8mAiC8LfmZC+S04xv8mTs8/5kEv4Wupjgu1X7hsL6mcAlX+G'
    'AKQ4PvAW5peXcZEJu37YQ8U4wN8X0tDHosE4K5tyQeY3oV+H9S3n76zIgvM95N9vxqgYd0EMxVWyhoeq'
    'cJC/IG1HF/QBUmq+nEHKhZ/OWxz2ODtoSXaW3ezmBlbHVRfT5x29as8a0aZ4/OLW/cTxq9Ah57S7E2ZY'
    'BO4YMZFdtzUcL6pzxlR5xPrTzbFyikshCTKRrqYtxstanqlJcp43rGWNGThU2NavZ1L+d3FfHXYy1vk9'
    'goPJXAQt+I4jUpWUuieD54RdGbwZG3lOROPUykQARITL27GJdDMjJTwuwGd/9HJ7iLzvMJXOVJqb5Rr0'
    'z51QxKu4cWL+WbH0FN9VrLPjOdcrU8MPwIQ5/l/ZHRqSNJaLRhJEt/uT0T2GwnjDl0MblPVcL8u9FcJC'
    'eNTbSQrOChQPXQwwPYwusHdoG+FcXYZfv/bUp7Lfb0a42aBkV/tnVQcLRHsbD6vq/eVyqPync+CUfdRc'
    'TRTYWgzYXME5YaVpZhJTDhNsd50iucPMnkO8j+kKETo8upWCzbdsEh8dSZlaqNB6MS62MlagFTCCzQi/'
    'HEsjFn1qwPCXyKNklE7eiq4R/Re9PBZPG0/vXMQzHmR919wJaVbC2g417SGFrH8iwAkY6tKweTi3s8aB'
    'FhLgd6AOrWn+2kXezKd0H1TbziR43KqC1nFea/e2R7TSvBFOz9gc4/fikfSe/Oe4tEVoO0PUtbroY5gx'
    'kKWwrNKEG0XwMXaRo+wyMwhSalzJJpZ/3w2MaCUsTubXbcLkdDKsRA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
