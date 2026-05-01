#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 739: Summation of Summations.

Problem Statement:
    Take a sequence of length n. Discard the first term then make a sequence of the
    partial summations. Continue to do this over and over until we are left with a
    single term. We define this to be f(n).

    Consider the example where we start with a sequence of length 8:

        1  1  1  1  1  1  1  1
           1  2  3  4  5  6  7
              2  5  9 14 20 27
                 5 14 28 48 75
                   14 42 90 165
                      42 132 297
                         132 429
                            429

    Then the final number is 429, so f(8) = 429.

    For this problem we start with the sequence 1,3,4,7,11,18,29,47,...
    This is the Lucas sequence where two terms are added to get the next term.
    Applying the same process as above we get f(8) = 2663.
    You are also given f(20) = 742296999 modulo 1000000007.

    Find f(10^8). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=739
"""
from typing import Any

euler_problem: int = 739
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 8}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 200000000}, 'answer': None},
]
encrypted: str = (
    'F6hWwvFttViQqD0yCgKvci/UCaiiqXthNm7VxNkz1OLTm0Mjo0wK0KFk6wxhzS1Pi9H9uUTcD2p7PwLJ'
    'eyOsLdSD6RPF7ppticOE/qQMCAUz2D++VCqbqqrC43fSkULgzar90FYL9cSNyiSrZKUFo94IJcTlOd7G'
    'NsnNagRAgAPzXOqDFeT56TDcLIh+vvPi3X1h/OIJiwN2b6s+zpzAXjz7LQ3lAjfTDLKy0JbkW+4puJ1x'
    '3Rb1V6wajJyS9XUVO8HTcS1Ir8hcmfvdIKW0RWvlSrFXVC17vycjEPW8VylPwgEyhZLN+KzxLqNyV1qN'
    'LlbhbiAQ43UeK2vzQ2n2Ff71G0Mx+Z+SoGCGXG5NSofKLxAGWTgzYM0dFYLvs/qkF8M6mP7WSDt2BCti'
    'A9F+76M8PVwc7a2zopiYZvTzb/UPFeH4aZJIfKkrBbMGpdXKzRrXqIV4i8px4b0a5ImxCeBE6yUR+pgW'
    'PH4MBwXFFuUHFmLeM3tMIb+niBh9FcQzxDfb0HaqccXhGz1X4DuxPwByxbkzNZcd/A0Fvg5A+jqzyyrZ'
    'VBXKbu4FvLW1t9TbVa0UFOrdCoRxy+1QlNFsfGHRVf98cc5et7d9hTYtkG3Kpb7iUZcoSdrEhY73AVh5'
    'NrkBscPmDo4l8jX/cH/YmRYdynLUsdbTEIQF8VTjJwV67TI4xC4kyk9LKaSAZArrNHxgPfBiDw3GCvEn'
    'l3uIW5yF77FkMSRWFyw6KEJmK90jZHhHV/JEOFBHjxAn+0qMYxgod2VK1shp2iAGyPqebeEjhfkr3Ips'
    'LHlqkwD4Eg36UqbxGD2QgD1oE9+eWXjjBRKK7ayodniyJIUgkfWDpOydh7yt8E7qWRXAz5ZI43pk0Lvj'
    'cFimR7uxb2uWgc7xK6DuqfrQWQkZ09gaC0+bljlwZ3PkmBJAk8AlmoqOAzK2EQ+PKBB3NKM9prsbiXQK'
    'M6Gsbzu0/5FftrtoFYVE6VfqsweSk6T9PGy5NDluyvtM4+wmNArSlJQKviVDFSwp6xAPG631y9AeVJyA'
    '8Clatvupnf0qortnvMFWcvLS+XI4IH2gxKgQ6GS+NyknC16F+/0Sy00MQ0XGG4JjodL1gq+kpvELIi4o'
    'UKG3k9x+TNtU0VhVSbuG1ygLPZBnSZZxvTjIoxkgbYpuNliCcbWVJXNQQSwtlmoY38yZ3Ki2AvYw3Cm9'
    'h03B6yHOM9BCsV/CMBsiE40ombMGhiKHa7v0+ImQg31AdOUEj8CtkJ6MIw8PUTjup75HitpRoLBV9E91'
    '67QurAvAEUIF5W0nWKZVp8GuLyS6wQYEu1KFLibS/iE9QRqJXZl7hg40pfxjVQGgPzolDrsfxONyOyDu'
    'XyQnSz7T0me6Ux84NBCHXBibZWlEvjGzl1mgVhuyfjuoTvnqybpeNr0M0BgJBMJU5TczvGTqAmEPcwTa'
    'ldQC3VQ7dGt3/Eu+IkCGdTKAYtPiZi8Ry/T8xzQ/pyXuiEajimHRasCr94tfn3yQNBvdb8iDnaMIqA5s'
    '6WOuYdK81uXTViiMPHbpUhUN6png5VLP6jWf29UxjzWHqrJWMY/FWIQUCAX0Z/mzAnuVRPvqEwZT29Tw'
    'UM94+0dsI/kefWpM7owZstGMhhrZE5DiKQY4UaigP6KhBfuCP0T9FSbW9VsCV2UNjqOnK3dlwTUm4Rve'
    'W/irCX1YaiFNd/kCQYnXlwRfcks2QZzAZeDO1O4AY2d4Bz2a7aG85p7GSIyzT2Zg/FUtjHETumYsQmqf'
    'Nvu8bHEs6EyE/TsDGc8S98dsP1J8W66AYkFx4kRribh0laBUzcIU4IOToPqNgU0ELpMt8ZO6Rt7DqWsv'
    'h4SgqqobHBI75oHQrgbJSMM0b3TfTeH1nOKBN/nLNw5sejzcC6ciMuGSuGBO7P6eo0LpE69uaQI6bccG'
    'ibrHqvoRhQtF4d1Z1YPgCKQo08/PcPw2YcViFexma1w1m+J6CQtplfHaNXSrheVC2cQihoTa8F0VjeVN'
    '6vnGwtfRqK3tHB4s72tYkpQW4VbzT0ISsPQzSSCoUA/yPo14LBXefqN0C/TSqSCRCO9cGAvHekRXhHQN'
    'eX1OwEyGN7/Xfm5uZcA+ahnowhw3CVJrty2vIUgSyxhtk5vRQnLMCg6+7nDsqiqM617tjQhcQMl5dBd/'
    'Cuog7LbDLmgJHhnJSkx2FvDC+2FZCOvcQ/uZMl8Qj+ITLZHVkCulTDZYNtkg4E9VAuFK3XgIQeg2cR1w'
    'd0fykaXWC8DMAZQAQ3S7eFxLpCE63meEQGglPUxmY1q0MKaTBCHvPqL1YuO6MDvk1kdU0dgQ5w0Mgq1D'
    '4PURJJr5BoePIDODGFdgT+nwbqLvc2Ar2+dYQ1omgS5h9UeJZhQNHX3qKlpza5KmgIRlfeYsu3XCqkDU'
    'A7Jr4e8NgoUDG9VmHXX8TK5oaHEEDYUdZAb/DVlyNIhZgiorny79WVdV1jEs/Sl07pMyS6qy3M62yQw2'
    'POEYk2lrD9Vfe+nZKv7yz50anYZbi3xCoX817Pv6ZqsBmALYPlNwsWSZ8QGIx/K1wvRSFdQNMPL+2wCf'
    '/EjLfBAJQyRA6g25KirpAip2gfrLY03Icxr83X5xf8t51w8Og9TO8NZEoXp5oTWexU6EMKlNDMWg8Mwz'
    'I0DHmZxPI5EpQkUCZBK0UVmk1GGzotfBPV7KMBgmx7xzuLUj9O+qqxaO3dvpCxZwAeAPzt+Gor6Wt1PK'
    'dGh5LBbYSe8YxBfqG20xRQqzoa6++g6r7Wkzdzy9JXGBD0fNlOlbNFTteuXXXK6gkl2T2rABeL38XzRQ'
    'mPbb/o9+bfJtuIbbowSd4CnvjPjpo1w8JdCYxH5CJVRI5KIGbv2g3/l6om4ccX2iAAB3qtmK8LlJIPc5'
    'AVRA556et0uN3eOL2zCAj00Z4Y3JZoT1g6EpG3OpLTRINw5Xk89KK+KWaNpzqlT+bdv3b902ZzBSLJzp'
    'vZLNEANIRDkFa9ElOkdn0EGD5FWmGfEnuGswLNucXJCyNuw3fV81lKA5vcSV/xyOb9N4liKkjIUKzJ17'
    '/UDVdmICBv4zT6ZcPLX7LAH+ClEUnfG9td8wD385HyswtlGh1JpiSN3k+0BKjZrNIMML2YVKmN72kWAQ'
    '69UdZk3JjZNkq/6CNAxHRd5rZwOGUWKXDIhEmDKQ1JGFbpAr6xI8yWTqCZxUi5aHAdt1YoQRlIizpBId'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
