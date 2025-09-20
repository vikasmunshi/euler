#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 414: Kaprekar Constant.

Problem Statement:
    6174 is a remarkable number; if we sort its digits in increasing order
    and subtract that number from the number you get when you sort the
    digits in decreasing order, we get 7641 - 1467 = 6174.

    Even more remarkable is that if we start from any 4 digit number and
    repeat this process of sorting and subtracting, we'll eventually end
    up with 6174 or immediately with 0 if all digits are equal.
    This also works with numbers that have less than 4 digits if we pad
    the number with leading zeroes until we have 4 digits.
    E.g. let's start with the number 0837:
    8730 - 0378 = 8352
    8532 - 2358 = 6174

    6174 is called the Kaprekar constant. The process of sorting and
    subtracting and repeating this until either 0 or the Kaprekar constant
    is reached is called the Kaprekar routine.

    We can consider the Kaprekar routine for other bases and number of digits.
    Unfortunately, it is not guaranteed a Kaprekar constant exists in all cases;
    either the routine can end up in a cycle for some input numbers or the
    constant the routine arrives at can be different for different input numbers.
    However, it can be shown that for 5 digits and a base b = 6t + 3 != 9, a
    Kaprekar constant exists.
    E.g. base 15: (10,4,14,9,5)_15
    base 21: (14,6,20,13,7)_21

    Define C_b to be the Kaprekar constant in base b for 5 digits.
    Define the function sb(i) to be
        0 if i = C_b or if i written in base b consists of 5 identical digits
        the number of iterations it takes the Kaprekar routine in base b to
          arrive at C_b, otherwise
    Note that we can define sb(i) for all integers i < b^5. If i written in
    base b takes less than 5 digits, the number is padded with leading zero
    digits until we have 5 digits before applying the Kaprekar routine.

    Define S(b) as the sum of sb(i) for 0 < i < b^5.
    E.g. S(15) = 5274369
    S(111) = 400668930299

    Find the sum of S(6k + 3) for 2 <= k <= 300.
    Give the last 18 digits as your answer.

URL: https://projecteuler.net/problem=414
"""
from typing import Any

euler_problem: int = 414
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    'VXVibyBOocAvaCaOJTMnkSoD/16GOfXaqSe93vCil5Ff57hsn6uQLfq8ZKRsWHZc/zUf8jQPGe5nf4DV'
    'M4ko6E+WcqIhF86FwgV8g8RwaC04wMZgbn8mUAC/Y+r33/02trprQbpc65yhRFP01K/7TJlvbh1CykUA'
    'Bs6qfu6/zs9cTAOq8vXRiUTIFZrpI0m5hv9sVDIYkAZ2Sl47M6cLhZwyhpv4EQT5WZGPbySBtsyUPS/x'
    '/bPjXYSSSWEiXe7Jmp6zquzE6Bqqyny57MrxzoxJpKw2awT2hJTRfQ4W6BuRTbDVGPZPqCgMQAgICFmr'
    'W0Yd93eXxpUw3l794ar+zBsvgLOxAFjnsFVVZ63z0opZPWJILQmgzX4UpJ+yycUnDhpGldFnCdgOZKI3'
    'MbzbKc6XHmX/y30V97VeQDiXkI1Pyt+0gu6QmycnK5jZG5YvDrCDvVdaz5axov46RxSglWSI7GtmGVkL'
    '/Dgt/akcMTRmH15yebnOt1hNj9ztYgXj3vi9hvINfhPHlxV0wTpLNBRLTPDye2eRv5lIsry8PMgnS84V'
    'IRlyl5gAy/WzDv6zdgehgZVsoWmTHEYOShCp/5c8t4qfr2EfHHckyAFdZJjV+GcAFHmegfxCh3spDkv5'
    'gSUzfTuEYVP94GSTSQaQiIYUJm4I/NZUNssPP2TkT8uvGKeiVuiapZJ0kltK6RUjzPu0gUrW+FBHQCRK'
    'YBeHhVS5nQ2s64JpNh9ixhvXAETvy4KgkD0su8J6kpXYmfZh9PSrNziltNc/0ZE1p4iRYY/Pxv7cqPYZ'
    'vVBTAgaFkZ7hC+AomGEJraLipJWMuAEJsyW7pTSkg5E7PcWeGaWpV2dIo65wt7Epm0UPDE5gVV6HVEuS'
    'MPSSJLSExlwS1PzXdKDpWyW/zpVPj8PdWL+YNC9CKsTvVFUftEQwwU/D7kuzcF63IRH5QBt1bVWMtcr7'
    'MEH0Cjz0f5v95cJh+vhrLHerKrih0Ml8ovJrQ7f17/kpdnfDMaHDJ0GfCRBwASZpurQIUnWq78aH5HyP'
    'zJD3K4yVlO7soYSbldaAOtNu7tALhvQ+vDHJuScaNEoqduTGvav9KLCieOShe2tSrLXEn7k0cChJath4'
    'uHrFyP6v2x9lS5zgbfBJRjKgKKHHr0wgjlTWSisscC7br1r+ChYedx6UlkExuWVw3WKTvxiIQexZVieV'
    'BkOdJDoweVYYLBG7UEJmOrg5IcTBIFroDEMZ7lsFg8eE8pa0G/tYdFV1OSRkjsG1fA8Anxa+gvd60s0A'
    'XJD+w8vSFhAlRlpNYfixEYMOjNi9GXoOr75lUSzqtSn9X5ivpx03XY4k2yvNuEPIfadbZ9tF8V+N5l4W'
    '3vXlSE9MfIYNTVCQBmLEneVfY+55nOaGqGlJ4GNeHK6QTcUtQv9nhjsJ4/DqtZjtJifFh/kpU5jkkQec'
    'nPjVNKXR6/ULmDLxFO11d53MOOKmDYSKD0s/kPGb60SRC9FgLTrQw8OdHFkJxtDOQdL2CUPtWhQesiVk'
    '6Ra4Mo3dcOTELp//AXTTMj81nZGnZd/Cc3/m5qH2obWRxqCkKMp6ys9kDZX18sr0HP40bj5E1cGrhG/k'
    '/PvvztVAkfPa4AEDjslxHT2oImYGZX6csl7JvLTJsNkHbSwWdpBc2lbuUWGtYHpi+/xLZmhx+uai+S6U'
    'hkb6RGDYi6ZN+pN1Tk0nW2pg1pXMzKo6vFbhhC9VkFPDBqWK6M6dwhLH0rkkbJWMZj7NHJFdyfda9EYa'
    'xCSPN+ZSYlv/ge5Aa2Xmv5RFZVYnBlqMfVl+IrRkHujNt8hkzGRYorW0pBkXLebJGe6tQCv4YQNQeMly'
    'Ns3U8dRa+31G9NUxeTgNiY3vPbajM/ZxcUg2r1zPLooV+GHUsZkf6KjWx3jzXVFNzXGryd2hTJJ2cNRS'
    '3avXaZSgmIszME0mPiZ6gL75Wkln9kjAr48QsurkbK4Cx4KhfAkx72+8vMUYh9ye0I58zGxKO8QLUewl'
    'L1fKSakX97xL7bSEWfdXqu5ysztNJHLlYwIoTc/rSfxQya9mFRRG1TmbZ0a4ZRTebCWPkDC7AagXvujB'
    'q7vBNWLXEM3JcF1SifSjnGiLtbW2ERq9f46UKumu/73J6aZ083H2lc6wrAPFMq4CLKlb7ovQO/16bWfv'
    'kiACK+v5Xig1uGtVu4vazeZ8rewudY7iDbKzjmstk0APZ5MpOSNCnehC5ktuQbTIBZ2CO7F5tWBRNwkf'
    'BvfnB6GjRCsIDsanlyX6MzIMkDPPmxTAUDk7EYcviQUhv3bGZYarBdnubLZr5WXgGk3lTKFZIuEFmkLQ'
    'hAtXfP+yTr1RWPZVA2M6f/BhY7Aqwog70RX2xmYn9YBCo/G4Ju7Pe/zMFrJId/hI6s1M1w50WIYsaNxq'
    '0tH3H4u/N1lSbwxniDuUN8XKBN9GNktEqw+MSH6XUX6xu+lkPzaFldlpE5WOi03me004qmT0LpKY0/+x'
    'bLhYa2y+F3kDt9u5Qi0JLUEgVbwWMLk8Jy2HAMPbdbWGef8qWsUrSv+9hrMLzbyq1Mhr9doOv2Ad2ZCv'
    'S1ADE2t3iLGRDSayjnVWLHvWOpL1OWvWjkNQC9pj/7FEJ9Iycb3Iq5IeRkrmW9hJ1cMgeRoeAArNf4gt'
    'SAl6t8f+CcogfYtn2gImkKapK9Y9Ed6r2gaxcFNzUT4jXdf4E6A4nz6hGapIFm9pFoODMYohPkihToo6'
    'EbU4w8FDgY8y+LIKDFMcAv0ikJWvZxHW9USj1w3WY3ozEyXT4EPOKj5BY5gNk7/Mdoec1oIMNDQZvb2X'
    'cryIu2a3ZQZbOwZFO0RUtnOOwVFrdRwQvF9ePTI8ycmYOgNAvudqPdHfa8RLXySTLdOHT40Q5O/k5LK4'
    '7FLG852LjoI3GR4kZcOnVU2xJBsDYG+emKIcc1qmGJXzK4zLTPdUGdlgDg8VPqG1/0Aw2TfmOioLoFCv'
    'v3XOrnJIdiV4FQV6/uXs1aJc0/JXWtRvFFYGSjAW+KcgN+YTljj9z3hTqnClzasRfL+Qvx0jSE16v7op'
    'e31OolTaI+zQxz/IfXWKPvY/eIM42NonE1QJN7julWp2SabIvAjlE0KoSU9QW9k6eT4/AwAiX5T3dR9c'
    'jbwgLCNBDig5EjZrATqovn04SQZr9linnz62gchz4VYXEYPo9A3Wr9gSZ5bR2MoQk5a0+9nssT0DycE0'
    'XndBR9U90wXkEY1pX8ckBYbVcQhcXaWAXZuCz/A5HzPg+xWecehee2gHPyuUFiDPnhPy0io+oAqkETX4'
    'al2/xBy3Wm9EWSLK1DaqBDiOtzhqv4Lwhg/dSr5NQEVo1dvYelt+ERK6g6vlrJfpttjtKB7HVDlNJvAZ'
    '2+1MOfmDE7TaviNL2pb1ZB31VQ26JyajAPRy6wsSeOjAGG3PbmjKZ7elRoaVcwiUFr7IOLiWTvL7AgIr'
    'wbxYcZ+B0wkVM4VMuu23RvA/vpKkTFdNwyM62nvPh3x7LLtsXUFCPjglkLWmkTwxPtSKUcJXjiH5RjRm'
    '0kVantzYG1IUGN3nyuM2VA/sm60C/vqnbAx1dgTsp8vDwCU5tRrLUq/xTUVE1kC9bJK/jnwq4fYXiq4z'
    'cRd3JVE7RF2GiJp7ZLFC542tFJO0lCsDOCIPnUuGdEf5cOsDIOEJ3V1+EOypvEkOW1HZs5pDXJRe/K4M'
    'uW/T6AJ9UiVYUp71k3hsUkcheVSYInWTGJhhdLsG3MCyyVGFKqX+FRjGqwJ128jDFLClaozNW5ZR42l1'
    'PDr4eWSew2TaraDi2hg8O3rOM7JV2eOoecnE7F0eLGJD+HuySK93evSwslIwRpIpdF4x9K/rSr4rWLqt'
    '+rgt+vbIgsGmiNXrliMN+N/m2jjia58EOOA0nhi6LrnmxNIwKd5JuZeOeuDIbZRxJxUmgUpWkQgZMGAT'
    'YFJauwH2as4G8m+ngA90MsEPRoDblCADtZz48BvSpaOuQAnqgFzLKO4yymZPMcsF5kGz11MPn+UhjVwe'
    'yFr8o8ri7/uR4FDjqcrvjdqLh3tka+NA7mevtebdH2FnOtYT2a4GDgNNMrmePlI0gl9Qm6MS99rfulxz'
    'hk56k2G5U7da4KbE0SAakRrvb5gErw8IG8cGuTul9JlUppb+hL9aYea27/ncVSkcLX1EKrVOLbgq1sYN'
    'qhExMhua7UXj0BDQAnyOq2YOgWOesICGiB/BZeWJbt18k4uR0AU1NPoNzCI2khAAfAgq61y72pPfCAzJ'
    '0T7aBfKqCbRwNGaEklLkoczOpSGm6Zrpxbd9XfL/u6I/nLjapbdcBFu4tvNs4kXlPx6cQfjqEFT8pH6Z'
    'eLI2DQetk6V3m71wOQv3efN5QnyqCJ3Rrb564lHBAOvQB6OrmdX5xG9R2mEDR3TI6cBIxqf2AflLZ4EZ'
    'epSZ7HWGwyZ5MTF5SFI4IsKRj5ZCJiTX7M51OM3LXVQX6xi8o0hCJdk6hj5qbgGk4VzNYlF1ndghJob3'
    'RUQm4lDMM4AL1m8GkbI8rylYdsJ30wX4WMkkciYDdwj5RvJq28gUMH1gGVMXS4EI'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
