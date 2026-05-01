#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 494: Collatz Prefix Families.

Problem Statement:
    The Collatz sequence is defined as:
    a_{i+1} = a_i/2 if a_i is even, else a_{i+1} = 3a_i + 1.

    The Collatz conjecture states that starting from any positive integer,
    the sequence eventually reaches the cycle 1,4,2,1,...

    Define the sequence prefix p(n) for the Collatz sequence starting with a_1 = n
    as the subsequence of all numbers not a power of 2 (2^0=1 is considered a power
    of 2 for this problem). For example:
    p(13) = {13, 40, 20, 10, 5}
    p(8) = {}
    Any number invalidating the conjecture would have an infinite length sequence prefix.

    Let S_m be the set of all sequence prefixes of length m.
    Two sequences {a_1, a_2, ..., a_m} and {b_1, b_2, ..., b_m} in S_m belong to
    the same prefix family if a_i < a_j if and only if b_i < b_j for all 1 <= i,j <= m.

    For example, in S_4, {6, 3, 10, 5} is in the same family as {454, 227, 682, 341},
    but not {113, 340, 170, 85}.
    Let f(m) be the number of distinct prefix families in S_m.
    You are given f(5) = 5, f(10) = 55, f(20) = 6771.

    Find f(90).

URL: https://projecteuler.net/problem=494
"""
from typing import Any

euler_problem: int = 494
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'m': 90}, 'answer': None},
]
encrypted: str = (
    'e3fYiv7vWBHo5S0ey7FLiel2Wdo9aeP1PKIfOo4RUqi7UKL84JK82DuwgKJlhxrNlAiAXcqWD/oWinnG'
    'QoBeSzMz5Vc20bmLF93DGq+A83iZ2tHRBfJdmXdh8LBrPteKeGHY2aCwRoHD8KUSSeHOYiwUX3in4eTb'
    'YQzm6nYTqCzMapG5tFKoupR7xh6T1iqQbSoFy3uuZRoCFdp9J8dalLY7kQOHVXQAvwcllOlFjWwZLhew'
    'hu5PZALy0Ui3alBGdkZK4RM2UWN0PzSGo5geWk1Tzq1K7syPW849DWCy1J4AHRtOvdX1LJ7qFhnhyN+S'
    'rtDhK04GEgG56pMipvWc1oBWQ+rzm3LInXaPIsDZIZxJ0YP7rHnwjQzjSEEWOh7BrJntRg9Tm3YBelzN'
    'BxYvtkRAKp1Kg0+x98tr0KbGintXNReUXhKGnPyZZlNMz+yLxbjHJx+14p4Px0tT4RJ7Q2YPiq/upp8T'
    'cnX5lkhXakWfHfuHqLoWipNECl2Ck2ATTxRpWV07s58Hx3q/JX7X6wCNH3qg4fRa38sAe+ndjzWKmljc'
    'nECaLHNdIV2h9kenBoxGBN5j28L+oZcRD6282KnknOjSF/E6hnvLab7QzgvCDZfTI1LOAmub0BUB6blo'
    'qisMMaO4V6pv5kkwL5u1p9uI2KJEW/7GoTAiz2cN3u/bMrwtKT19gtziUMQ0cQYXtrsD/1nV1HIqRiz0'
    'ddRgQ5Yh5ohygmFIqAN9Tpy1W36zct8e3+hDFLcpMqvJXYUcyU/yMp8nAAKlfYRnqseInuzxwUEn827D'
    'V1MHQ01SdAiCE+X3IBuBAMXjW3UwrqfKFhcRxIURAtFV6mRyU2oHNSY/6rCG6IzByNSjBk0lqdTFxb7T'
    'U8nyTKM/GD5aOOFTptg5YcKxXL/PrhoSRnW3Gj5BAQRSqbqquiXGEvB76l8d/nOw/9ei5sFbms77dMyK'
    'V3syboa7E0IeAPc/h9fzBrFXNRoiHu9m/4ku+f5YYyPRf52NtvNQ50243Os5a2LaDbyTODAUiW0M7SR4'
    'ogp5IjZCQvwbCxwgVdrZvT6sRDtUiR4IPTrlPV6sgdEwx5rSa+1iiXj4WJsUBF6DicUxh0O3Ys9kSRv7'
    'PPndLhwYCV88ExVI0YA3pI/Axqc1wGiBueHzI+7yYPhpk3b+xtQJlD9zb5lLuXrMRRcphLQHbTpaIUTH'
    'nLEet1k5IFnh2gcD5xGm8+ecM1J9O3cJGmV+LDP0T5Px0EUsNfFX6Q3tR7U1Cqq7gjWWExICTNV6mjMD'
    'tPMY/9P5/5epFfg/iNH+CGbhKj8JDwNK0DO9wCp7GrNruNM7CklqGJVWRgiHEUf8tGP00SVeL61We4lk'
    'PPq0DHhxO5humO7xgvuvXzdC7kPMO9h8SFFu4Ld7oqJVY5OQ2k1p5mpoHlSwzd5dukZBvJ93AjplGMUv'
    '/xHWziOiB0gmZkdcbtXSMamoKPhcrQVKq4tBPczFGhcnE9fp7MHgzwKPiQrXAN6c6dgDfhx1v0jAwdvq'
    '5+ZpyCK+SYiCsucT7uZA7s+BKkSiBLXU9VsxCGbzXzS9hznw+5KX4uacw1S2femM81abFd/JF/hkwtpC'
    'Ri2lGrFUU+bMjtbkLMTi96ipZ6aHu8aeMQ7Y9YkPiyJjyoff5SKB9jTjCyn7hRo593rlAmnwqdbaXYms'
    'nw05RYhP1o5H2T91dJ1EOcppiW461ao0dJtgpgejYpvR58OaR66msAgxU2tNjNpbxlk+939z3l8p2x9q'
    'TNuw/Rut4PHtAbLmXQvOwCWQ6g3UYGZaXKKcUfwatWmm/n9VuIJ31g4QFloz/OQaKLHfpUQOX4L8UzUj'
    'VBbVITR4rQ8H6IeTq88FNP2AW+7UT53WNVE8iqhFgPDLn4H7IYHLyQKvxSB9qGI0MO3WSl8ZQSU9vxZ7'
    'IM3/PyoC/ovJYaz4cAL6Y1eKRCFRie8lzR9yCn1ACZXDT9fXyQgMtYpptRV7dp+kah9Wtdu8BuzVhmdo'
    'LWGqw2763oPWAWxuKjbcDb3mtYikab8vJMwykhR6WE2K4gn98r4cvGe7XRBQh/Q/vNGD03k8ZwR9HiVg'
    'Ux/dDW/P6cjV/jw6m+69AwbvGSgOeLunE26c+bmSyXo34NuGFYuMtJ/dKsX6jLZuhTPngtXdVi3fXEBS'
    '/CJVx523TxTXVSMNld+RNLDWUMYhdnfUJskqV5s4L93HWOBHDFOSBYvgcVQ406XjQ48l4dTLud1+nB3H'
    'RXevLyE8l/EpcZYCLelvC3As+Y7LoZ7HvS6XApC9HYxmrEuyvJfCU9Nsn3gasJ+9cduE1hmV2GZVh2S7'
    'INRngVIYCRTLe9TXCYFjsqD7OCc5NNWhkjPJA5rHtpqM85HJN1zMrKQzBO8K8UOM8CRTbazuVeaplJHV'
    '4e/pef8qiw85WAXOq1zKzNIVAAQ6BzsL1SpPOsHFfEfLqqKRYsxJpR2Qt2LJzz256fmDCNeMejyECzWV'
    'vvI3rvJ95auDsyE0DXL9OJyEV0fDOVcJQDic8UgTsZMB2WsBX/Y4XPh8SSYc+jphAqX9cW1P9FCIQcCB'
    '+ID82jjh6nQOn4c4sWSjBSHDNEv8fYA+iG8ZX4zqirZzYhV2TEg1MLawhx3OmkEyKpHRgBB70sCSMH1z'
    'cXcF/ueDE3R/GcAQD3WiLQ8v2J2XrWUdtpJm8t4drx3IQimgF9TV83ZSF1QxzDVClYST5zum25Gzhoee'
    'KbmhGoMpUUWMjdrlfqo55mTlHkFro3dIeaVInCw0oPrC7dzwjPg1JpPTU5hgSLDGxWl/pbjtncxhXTg0'
    'nSIIKMEg12v7aFNG3mFFAQ1m/OsonZsWDxsHt7TdGCUm+M6pE613ICkrTPwWXgZbQl8GF52V3NSwS2MQ'
    'RJEJQWD5WwPZWbHNkcRa95XPa1yFMDu0/dUSJ+gKAdjaEBQpSEegxvQYpCpQFaqyRNL0GdnyOhtnkgvD'
    '4C+VYyo6nrWkjl26uTth5jBCLHRAF40tQ8WEXbgLJKgkoGqZr81Oy9Qgv+UGCz155Hi2kIkbaiQfMBgu'
    'YmB1757vTZ+SQW9yajBYyl/f9rPyAZd/Mpc71z4y12LixQp3resMH7/DA5+/TIkVj9hPRQgnent9cHw8'
    'n+wcaUWR0uUVx4zwlJ/QLdUTXrHXBIgLN+z6Am2uhWcsU8W7fm/MLjstHouMcKwdNlga5lzMbVWjkOwk'
    'zv8q1mmZkE/0Z4tySX+uYl2N2hjhtI/4+lgG7jD/ptdhJM9kerPXXCMNaB+H0ykPsxJZbdc55q+ZCMMX'
    'gWM4x7xykEs7BYaUP5ACK4SdNS+zhIRiDGnF7ZoGkqdhNliDcVkWD2MR5DecEE+66Y+KZ1n8vtC88eC+'
    'sBkTIfv0/js='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
