#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 170: Pandigital Concatenating Products.

Problem Statement:
    Take the number 6 and multiply it by each of 1273 and 9854:
    6 x 1273 = 7638
    6 x 9854 = 59124

    By concatenating these products we get the 1 to 9 pandigital 763859124.
    We will call 763859124 the "concatenated product of 6 and (1273,9854)".
    Notice too, that the concatenation of the input numbers, 612739854, is also
    1 to 9 pandigital.

    The same can be done for 0 to 9 pandigital numbers.

    What is the largest 0 to 9 pandigital 10-digit concatenated product of an
    integer with two or more other integers, such that the concatenation of the
    input numbers is also a 0 to 9 pandigital 10-digit number?

URL: https://projecteuler.net/problem=170
"""
from typing import Any

euler_problem: int = 170
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    'ab5KNprWL8GPmon3Yf6JRSNHqYpBs2gEH749lTWzKsAB9eXVsOJXy+fyMSIl0zjRu1q8VEfqTD2zS3t8'
    '/dv7lH7MzscTdy92l5/MYY88GeBZ9I/sFEogNvEvGibvE5B2pybTKeuoQ/ORh//Frn74v39BT2UGfKBA'
    'XGQxpMN+K2Zd7xr00rVYLS7VgZ88532Hd9SPjE0YO5oQspeiyOxaOl3/33E2X1nh8HdwYC3twZSAS9mr'
    'ZF1JjkBQk/ajXo0bRA47kXJd+UDh2eY/jROyH6QY/WMYoD5qSQVJb2fwBFhoo+EGPFAFDUE+RVKHWQLl'
    '2gp5drWJAMsE66havTxmOo1mSi+R/9iARiOQflXKZsQjHEY2mC8rVKegA41MDHESnGItOVRDe5BE0vz4'
    '3cpNLRE9J6TMk3NKub+/UuwBLQ+lZe7zm/egxmBvB/m9nJJWdV7iDHIdtsRVJWjJHjpa46YuMbcxMNVO'
    '+llABKFDZymUTDaUuCz5Ga0JgPLcPti94tGqzRCdb0T6Oczs8/eMmAZFK6uTH+fEA6xt0OXpa5BATryO'
    'gGMCAAr7/IS5y/t9IGOW//gHkM6hF2X8RTFOjaxBVBY2y8FTW38Nl2ErusOtIPJRVpB7T2WqJRuxazC4'
    'HIyDc3y1YTFrCmEZCIgyTCMnMEQ1Fy/CQyP4sgYx1ksd+21de6AdZmLV5S333MXtgef/ETKYy+MbbKgA'
    'rt4Odcvwcw9zvVUK7aRfxcC0dRupN3hdf/kqKZUVVbTesMbBcb72NfjIZZQ1jSUK3XjVdW2hwew7mIGz'
    'oaicO/IZi5ANaz3yukL2csZkSBpPXw1nfvcGYu+JSdMXV6Jir8oI8OjsR0v6QDxKcZz2+ZQBPm1E+gyl'
    'q9X2JJkvIeRVGtDF+jHptzXipdSMicDAfaGo/HPnYdplzmlO7Ki6AlJYBByb0HQmz/tahYomv0I1FMr+'
    'UDKwFcDM5zwa3PxA9Mcu02c6YGv6mjHP5CzO7FI0CM4P3HiZD2X+zqTKPFiy7p+Kn7ySEiMFJufRC6Uf'
    'SW0Xa1/b5Ci/B7RcS6LmJk24/kxGBzabe8HmYxZ261qPHMuAHANMDx46e8VTdcCFwe7N791SnH+ZRQal'
    'QhIEjuO85QsD9kH53a8FjhyMesbrtlBtF+32bDvc1wmjwj/4/HmCGwWUNErOpJPt4nM7GfgxDj9RhjrN'
    '9zTDUAm+mGTR+1E8nNMiG43YEyB0rMvoZQBkm80FEBqPFmQ0fhBMYyFID6XgMSH/peHqaHdRUlLVkA7L'
    'dt/KAiLISV353do3BxJsUiGIe1zmyAFx6oM6wJlmPcYPiN3C3nCy1HP0w+SEl1VNN24QtLfpW0rIF87t'
    '4coFSfcGkv0iBgzIR+klzNbv6x6ee7EunuBSznav8Qpj1TSHFLcQ9xEx+1hukouPQAM3u2mrEOjesUSh'
    'HI8JfWAREF0cO3RLcXnjbkBFEejWn11JDjCtgV4aBn9V7k7O5Ko58iwJbpRubdOaLtEyqFIKRysWtpKT'
    'agFOcsiQdWYZTUfLWiEdWNV8GE/telxpV6rVqaT8p5UkdwXPftGEH/X1lq/Uib8eVBmL8LssaWJCGOTo'
    'WFZWZWsokNSxK9xKX8ojPe85yAmxgGAUh0ZQt7NLAlnsu/Gm7QDvaC/o5J49YXpKx3YPjUGifd1S2+0e'
    'Opk5vLj2ucrKcRvUh3iOoERtRBRcEzq9dcZTHtHdwiCWRpEKMrhaVgmp1QlLZbAUNdV3gk6ZGCI5Ha9n'
    'QGvyI+5pnYNYD++soa2w/qhvso4UHBIX+A1zzZx90+8md0Qt2VCckB7TIcBNje1tH/eZzuCHRX5rncnv'
    '7gxAcaxmILFEHHSQFry2wgsOm+wTjTpv8N7erzuWijAMPIHOG9eY8LCoQpllQlrFtp+tvstBdO0N0I1v'
    'c4pWNeqYyzMgAFcYNKv0DP1xCKu5PiSy3JvcI3slmFjkLqCD3h7HsMOj3fkcgbDHYQaB8PsfbYeq8KzM'
    'KaSSZpDA07cWrI6RDqbehXQVWkJoR67HNIa3qEydeyCOZWk8/L8kNKUGCSc41g+A/W1Z150Yh4lqpCnm'
    'YCq8ydHzab0ZhKB9t8S+sDuLrROrfAVAu+R7wy+P+TX54XEbU3li483kGfMD0LzTW2LcaLAOJRnomAqY'
    'bZ0WCnjgtS228Nipa8uNND2DQxArmsPQj0iX3xBw0UhejGoR7RjEan8FHHxwcKHdoQ6tgf0tD4BXR0hK'
    'rpn+rAVOheQsXeYIfmLajfAyrGb0fWecBaiRVwGsx0oKGArUy+7uNo0TC884p0PYvvoz1UV3nTY3bQUG'
    'PtW1grNc0ipqeH9IfT733C0OJeNEZJnWJLqX/yA1Wr5K9eDCdHRSV51diakFP1CwVHGbMLJxla+S1n4/'
    'BGzapmUcbnfmoSWBKs/GrpnSmixX0YWs3AbG5qrlU4O5uv2LFy6O0Xt0H7feImjk0UnVtsut6A9oLdoE'
    '86gJes+oNheh6A7O2PmW8foGSF4H0jRFMpLKUXEjeq3CWmjjz/u/BRMlhQbD7K2EYKXyvByuYMZ6Se/Z'
    'GUW/huunmolpAlC/g4qaMGC+g0JnLVjP1nfVzKm0JXMUYYBt9RzqIV4qh+UWiBhTBsHk/6Vk7pFEFDNM'
    'w8vS5fPfP5vcaUCBj40itGRp6LFdT+wc+2GDZ5T3GCPCUyYsYLAiRXm/DMjaqHjMaIDObNZvr/R8jxny'
    'WkI3eCZi00gOW9mznZQtq4QkiMrAE+6mYylsZqp4qX43/Mq6P6m/tOCqbl63lJAEAa68cvrtv37j6gXU'
    'bn3mD/oGHIYRv50iAdekJEKu5lf1ACKgOwBeuTvQhfj64+Vo44Bxci2f5vngivdlyinXufXGThTI4wai'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
