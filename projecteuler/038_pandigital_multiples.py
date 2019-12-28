#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=38
Take the number 192 and multiply it by each of 1, 2, and 3:

192 × 1 = 192
192 × 2 = 384
192 × 3 = 576
By concatenating each product we get the 1 to 9 pandigital, 192384576.
We will call 192384576 the concatenated product of 192 and (1,2,3)

The same can be achieved by starting with 9 and multiplying by 1, 2, 3, 4, and 5, giving the pandigital, 918273645,
which is the concatenated product of 9 and (1,2,3,4,5).

What is the largest 1 to 9 pandigital 9-digit number that can be formed as the concatenated product of an integer with
(1,2, ... , n) where n > 1?
Answer: 932718654
"""


def largest_pan_digital_multiple() -> int:
    result = 0
    for n, x in ((2, 9876), (3, 987), (4, 98), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)):
        while x > 0:
            number = ''.join([str(i * x) for i in range(1, n + 1)])
            if len(number) == 9 and not any(d not in number for d in '123456789'):
                result = max(result, int(number))
                break
            x -= 1
    return result


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate(largest_pan_digital_multiple)(answer=932718654)
