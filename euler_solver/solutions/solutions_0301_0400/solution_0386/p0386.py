#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 386: Maximum Length of an Antichain.

Problem Statement:
    Let n be an integer and S(n) be the set of factors of n.

    A subset A of S(n) is called an antichain of S(n) if A contains only one
    element or if none of the elements of A divides any of the other elements
    of A.

    For example: S(30) = {1, 2, 3, 5, 6, 10, 15, 30}.
    {2, 5, 6} is not an antichain of S(30).
    {2, 3, 5} is an antichain of S(30).

    Let N(n) be the maximum length of an antichain of S(n).

    Find sum N(n) for 1 ≤ n ≤ 10^8.

URL: https://projecteuler.net/problem=386
"""
from typing import Any

euler_problem: int = 386
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    'h3i0FtB7FylfClUo5hP8Ee8JXL/euhqlVHGIE48P5iUeZO6Mz8NAHUZ0yuQbc81ZGuzQPxT/OB0CV/yd'
    'rLY6mJnc13S3eHxDB87l9+o9FsQz3dvUB5W6Zgyx0uMAuXEfDqdGGn48Y6tGpLUu2E7m1LFRNS3GgPWs'
    'wgtLSxFhoSL4WenxldCUVsm50cvuORpKOt56UQO/vlXkw73FvkiFbNj01v3hODU01FEde/5+r2UTrwuD'
    'O0XgFzjQYeBRRhxWJlkaggRWXDP8YcNRPnEEmavbgrLK0xynrD6rFOKXee2CO3EUgCmD1uG5YL+7XIhW'
    'FfIO136xmWZ2EPnUK4SPR6k1HgajoQCXA8SY8+yybGuXszhAIQoJsA+YnBaHQ3FG1DgcM58UVwmRci2f'
    'Uc9cLyy2qplppUMiQ9S1SmONBZYzBTdx3WIYAVEOKbOCiKRUzF228e9WghTMPSyVQHe/6hw79yl2/Zjt'
    'H7jcvilNMsFBK/aO00cm8hKQlsSvKHBliBV8Bo9ifUD8xSjLP76xNa0WL5hlrQNUls1FKtZZZHALco5V'
    'NxN8zv9ogRF6G35jS3ndBCh4Toh8Xg8crZWTOXUCC6kD36TOJ/FktsDaGpqinbH8R3aFj8Px3ZRFR7Oo'
    '+h7DrPjJEVxfdDcukBhZ5F+s+hbIiioAP96jtQFePH74BNajYawgXw3qCFmaFf4miF4ly8MTqEMkXqAb'
    'aqA6aNGL9LNBj5IWEy53FBqtBDzWLdx+WoVfVFIrwz3HDCWSld7uBt5Pc1AW6w1HaueB6fhxzwjAWep/'
    'zN1jHrpjC64OB0qeuBRrIy5FgLySN5FEpvPz1QxNqetP7sKtGV+Rm8PbK0agXcr0cfRNXHKbaeXuX2l8'
    '3FX4EsEH3ktUMVs6znDwyMHOHKIImAEDK6tOS1odQGrBxR8NXdaEPDpJJsKjVAeihZxT7yNfLxQ7qVJk'
    'oKOZLyEEmayOa1IDGJ7C8agAF0JK0MbNm41j7n6NePcu6MT/ht8bzMYITFIh7FdPkE2LQrRsXh3Iu77F'
    'IKJ0NYXcp7NTynzmtruh36ep4fVyjTN5nh91XPpw6jh9lXeC1xs3SY/Z0CoOXOu+gm3KhSQgfm2m8rKg'
    'z/YWfkQNAkgNSormDCBlzbbs9LE80jhVqSNb7bk/yB8LD9iEf3aONdAcb46cY4yapgDx2KIprZSiz5Hd'
    'bf8DnlJjjwOr8p2io44VU0YLXepB6PYXPcEG1dVqXerMq8IsmbzMVn69K0De2uat0d0fB4TmhzTwgUAO'
    '0qs6+CzMxrFgv1ywtuaRM2SSfHK3PgQWDnXSuiCaS+pbT3efOhFtqNlYCBJIfD+n/6MNnrmQd75ZNNmm'
    'fkXrI0OPX31rfbYLZQN1TlIKqf3q4zzUR7jOYHimTOMrx2kOgh0A9LQIR3HphVttimIrLDdVbsWK4p/9'
    'BayVH3GFUFDLNKswg/n4Bku6RscgfqPOlJ5B0dmlI3eECWVhOtTPiMFlikqkfS+LU7Ke2C3IlZXf6TJ1'
    'uzWn51tfIT5r9aSIN2Hl/jfz2CBD4QP50NYRegPZxs9+vgOIe2O4WpFHaLjKDeNYa4xyroMtlzvMiY/V'
    'QEgikYqqWDnKAOqrC92frMJPx/NLnXee8nCzAbOnxVyaaJw4NfWGuGhHMJuq40g5H71ckn0tlgYQOr7C'
    '9LqCG7GtvSccgZynMnBrBvGCUCafuJaPbwqmyWsUhxgBGJR5SEk1D3jDmD4w3e2qyx8XUEnOkF0h1Q7u'
    'y6c6cF3ZISV/tw+9ozkEe52w1v+9giWDva7VIKDIV5L3FrLAIfQYAon+VlICoLav04k/D/8fYVcVhLYa'
    'ERpOrwn9Ax78uIrHT8ejlBRx8+pXUiaRhub4dFEEHPn7eeOGqdmh8Bp3NHj+Au2WXGd1kz2cEU3Caj2s'
    '0uECoWsnjlsY3q5R0U5efqhTw4q12MY607qgvMQnUz6zbwkvfi+/WvlxLlQpc/eXh+5mVFyq61b9+i0U'
    'J05jWc8NVA2Us8SwlHQIhKTyOIGwfIK77kj4I2pG5jx1RORooRse9dTrClfMO9+kBoTPGknxfMKwy6Sa'
    'vXaa7rKbrPmxV9/AQrJBG1GtlUjQXrPnt95gQ6UGmDqdHQ7w84V9ftFuDVOJmo2Awc05sAOJgHYjxymA'
    '0HtxknQ0KDt9kSNBHHvwrVH7AO0yLL+TprFLztm7U4BXchlbBFLm9cTiLHBe79tuW7MszzfFMM3p8eR8'
    'YUFIMAZHqbdc7HgKLuh0Ytc6TQQv78siVDUvF2fl5Fj/a7q9XNO7oYHOrPb6c3fQ3BkE5cdx9A4l64UJ'
    '6ej8B7L4WvTXI/eisZnkbfcKx3NWmLwm50skaddibL2xnUAAoatjW34zOAtWgaz0cGbpnKd+yP7mkk34'
    'NtJik8Dp1JQWMfAPxmXKfghX7dm+8/reaYfbRxQBezy6/zrtmCclC1PlZu4pTgVHdkvagGlE4BNMqhtQ'
    'UkeU6YDaoPlHrD4yXk+/PcNY1LsUKFo3nTE1cCB0ynsefHheCO2J66C/TH8Ck+pWiRgsEZGX/OhGm2uJ'
    'hhtg4eM8RSm7mVPoBnPV4bl2TCPmKxwkQ7KqcpY+zewW+g33DePU6oiHuEcVOXXpHnFCCpJbNqTR9akU'
    'FnN3orm6Wh5PxX4aZNJTtKJyLWTqVe9N7n9IPVltkjNnEEtzfnEwCkSLNxQlpeP5Pgw/xjsB0ZyTUTVd'
    'PtzoVb8PN+qB2v3UCGxSOWH1foZ0oTMDtUA4WCNXm83AvsT8k5bwtR+Jr4Tyix1nnboixBtrJEC+oAge'
    'm6MwElOBBzlNbTquHMd4Ee28XOeHv2hNbT8Aytk6D5QLit6l0KL91Wi78rXfDOkxPGMSsExF8IubWhqR'
    'WbJvmhoWJLK+VsyU1G/9MIvQE+3BYgDHGi/GmVnF2nhb3g5S32SGCXRi6q5nAWdS1a3VnYbdeaxWZXQw'
    'lkeE3aAncsIv4TKcM5wdHFRZUBzvOw07WV+BR/5scMAnp4uBbyysD6ITv2zknaMrz/RdTHSzywr2W3Jt'
    '9SbZ+p3AWOe9SqIMI2vUPN+QesbIhfKh/8lvSaoLtKTuQt1X67yTQN4NxgwoOwMyzZPSzPaOEqTYX7Y3'
    'E4Co/8mMh19mY3QrvYbOfOUJpOm0XKT3VP4v2eZxoRC6X14w92Y5hwZdETirwn7IyJUB8wRx1YzkWn0T'
    'VfM23F6+4RI2fxcM0aZoXEuNd8OGfBPpvpUJrONt8gbf/9kj8LRHvQOMCLsPOJIpMwMy7qNMpN/abZ6e'
    'oZaquFnTQouRjJQeNp+diwMids1W/HOKWwknkFVb458zFsoyvJ8t8KkGzwkl8nlI6UiN2Q=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
