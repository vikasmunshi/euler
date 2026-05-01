#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 953: Factorisation Nim.

Problem Statement:
    In the classical game of Nim two players take turns removing stones
    from piles. A player may remove any positive number of stones from a
    single pile. If there are no remaining stones, the next player to move
    loses.

    In Factorisation Nim the initial position of the game is chosen according
    to the prime factorisation of a given natural number n by setting a pile
    for each prime factor, including multiplicity. For example, if n=12=2 x 2 x 3
    the game starts with three piles: two piles with two stones and one pile
    with three stones.

    It can be verified that the first player to move loses for n=1 and for
    n=70, assuming both players play optimally.

    Let S(N) be the sum of n for 1 <= n <= N such that the first player to
    move loses, assuming both players play optimally. You are given
    S(10) = 14 and S(100) = 455.

    Find S(10^14). Give your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=953
"""
from typing import Any

euler_problem: int = 953
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000000}, 'answer': None},
]
encrypted: str = (
    'zM3Kd0J4VSGVAZnC6AyJb0srGiUVp6V3rdGNrwqgqzBunUPPGdq4jR7znRwZaGp0yzo3+JFnqgWvtYqY'
    'oRuTpRQEWbP8Jcg2K6EQSSgxgIhA8aLfuqbErqsBxW62qHAMrqwIVIEShNEDJGYqkXn07xNKeKTxdnk/'
    'U9z3b3IMkz+q96zERCpKfCbEhaPcHpJ3EyIc+7e+BrJnZIS1UesLyT8Y4cAqtLCX/BB7cerj8dB9TPEZ'
    '9gAEvrcPQP1iU5quJumgJD0PnUXI3vRPDjlVcVtXYUPlSljpbT94o2iIHJPqCe8IIK4Zx3lATYzQpjhj'
    'UM2ff6f2DlUcsZd+3rMLmxb/gvHhvZuJ5a6XXk0Fyk2ghy6bc7MZf92p7ekcT8RU0a91BfujV2d0LwU6'
    'n+TIeB6Mg3GDknH1DAX8n/xIbOyeR98Eh4uNEMp6ypcJfN7OC8BlT3O/MP+E/pZ2tas29x4kxgR3M4Sa'
    'JA8jepbjORp4nsxMxsqNoxR1Pengla8reg4Svs5b+nKbnn77zuthAmbt/YOMfRLFrucfEmPE/b1/9sPA'
    'R+yq7ZxpJey1Ei3dOgoY/pDuB9dQH+6c8ike35DQI+cy5OIka/yLP0I3rhMLrGmgQvRBV9JySbEYzwAb'
    'jx5BzmFHjHHLH1vWjdYAKOm26pc66geNBTyzQxlWDowsi/DLh8JVH7p+sQS/LhoyZ3vtv5P119Sr8z0+'
    'lGxSVK2S33HE7rtMrUsGWIHbAsbpxYj+rXR9/J+A8sP18WXHWWueR5N4D6av0LdR5Wsbf3kZbeAiH8kF'
    '5+XfEJ2tGUgUMiVRO4ONqZeR2u3hLLQU962T9pP+pd6yvLqCZzlZE4RlPgrldSmkF75Ue/3gFbYe+dL+'
    'txjwwZs9Bd1z9mBgFGRUkyO1jntGRBjm/u2vLN7qV5u4Ck46IbXXTP4NIEWF9xO0FryeLWNbC02h9bTO'
    '2q9MXMP1NW9t6WX3pmnzBznYfLUrELBjVxhLtmr/iiaOsSR6B5yv39JYWtPvffdER/IDSTneltTyk6Og'
    'do/Hi0RbT0XFU8cIj3uffIcgeWxKJ7dKNBteFMK7+q+VBfgcRkQqgF1qzE0wTmonKHqd/Vjq4D0hyzCQ'
    'yVnEg+RJJaRMQoK/Zg+iuZ0Ri/xLcb+GnAz3Z9O4SgeCQ6FsCyzo2S3b+URAXDPwAolml3NJ1ZywwhXl'
    'CxDi8vI4ULcnxgzF3qhFZ1W3a0qLcEf61HRhDxc/pTJBOyShPr/0GD1X5AqRGGU+oMF9XGO6BZoKPyxb'
    'BBeP3v0hdKRtMYJFXeWoPYYLTkB7xts2F8AiEweWx73MardKvt0/VK/aL6kkO94Ks1ATH+oBqPDq0ux+'
    'ujuRWKJ1XU47eY/c5x7/ZigDWw1+N3ONoe1xUN/ZIFVQ59Og+r4VPC2al/JEHSLIcP80YXnfO57WxfFm'
    '7V3Pk85blNBA5Ok4PMrncAIGyOaCnTyWu10IA1/1EXg6UoL5pLXeUv9JlaW/yVBqUUWUHrCq+SfOMxrP'
    'ST56h5/1hCjqQDoGjqRMOg/onHyUKrTTfn85ttsjomL0qQhnFXV+/eg6Tn6jC6SbCltiEOTN8mRRKFAu'
    'hvsFyGGBAjCqijHloEwsbOMCZhpYft+SjYxbP9GjeYfITGgKR2dEFuwKdlVHbL2F2GWCVM8QbWiVrQsm'
    'hj7KmyXtDzSHcGdc8/FWDI+k3vjvCZOdIMUV/HxVzYpsarPLcQVlOnQmQ9pgXfrcKeRUMSfp2MSy4i65'
    'ju98NmtzHmlI39KGbO1RUXAdJMfegyI0DXBGos7KmsMaLveCWeq41PyEdeiqJcCnpRGlGIONOInNigN5'
    'EhdPubgxrONfpU65up27h3uQ2nfgWa6aDqO1d6ttuB7/aoVRcjUHm/pOC12Lj63SjpSPDI6McWFg1qz8'
    'lnyxJbNILsXarg/s1ZsFEXm/n+S54adJxcp7o4OPtDw2eayvzNa6SiIgheufmOQvppY+6TTmhNygrEza'
    'DHRoWgVYxps9zh+2HL5yY/btOYvpbvLvXEEqfX1OtFxo22Tc2ouYby+wNFf3ZfoM0bzIzQW9eXC0Z6hc'
    'HF84f9vnCNnvoS8Qxgc1tPnxj3leoWNJ3QbbuSiLr29l5YbHVmVUP4J9P+n7Uinh8d6gqI7vKeRXgpjV'
    'IEfQ8sCSjslFJI28AjNrW+tmYPG4MLYTRSShB/8lHhpq4vvcyptiWbVRTJ+1O/iwdDF/lWHbKBQBEmFE'
    'Iij3apxJu8S7YMv+yJVZTKUBJ5fBySpHRy7MAjNiynqbYIEv4vu8gAfkFQHpfiNvNM6EuwgGcMix2/uZ'
    'M4AmdJH46Oux6exL+Vjb/M/wGW7cXEBZv60lKqjVRemJqdiS+CIFtT8KzBCRSE97Zwwl9htiRiEsUI4h'
    'PfLb8X3nEkRmHhPvZjAfCwwxfUNu10wX0h/syVBB8yTzD8mXTwjSn766bCOfrvxnvs14aNc2RS75k8qB'
    '5VAzFTV2m3Z7UlloSQ9dzeVI+3ORwxylkSuzJJG2AFoLrYZzef+kZ+egik04huvJTjxlpdGH40KR6aDf'
    'ozFTxyMm9z7g5XJYYzsEbd22KbdhFdDDfn4Ng6msGRLNUVcIbz4ubtizk0RAdi+o8nYLtll8b31Kktk3'
    'TFJcL/ie5nGm8U1CsPNwql6wjUYCKp1YnkNorzBTXjrQQXY/aTTmApZSg2Sp7dyM3g/9mfrOkav4TLgO'
    'DvljA+mw/rkizbxe+wCq6PN8dAHb/NJHHbcZjnGMbdn2fVrJ+eaEPnLSc7UN12cynVtboglRLQUCLTjh'
    'aD+9b+/ypUQMHW8upwvGkt8fgYbu2pwsCj39MHz+CwlZMCBUGGMz2ZKknMlfL9Yt4na1C3y9Q7uWRyt9'
    'ArLhTc+as/CJKpFgyYl7dnr8zUpqH/+brwwC5NOrKjgCPxNFF/UGFHm1FJcGkcEywVfou0VpivnIWM/7'
    'e1W56iYpKGnHDOFzUPkrWxMQz/Xy8dkakHvkuZ4Ywr/NlC3CmJ6kiF1NJ7rfdip9hmF4BHiE4r1+jX7f'
    'FQdrm6AbW8rdg0CpTywb4hIhv9dFAQjTu9uCXwMT5qa0RDjsvB+EmO49amqqJAZbUdAjTr8JGkxVOVZS'
    'iD0Pvmu7MvsFN8V8LJqVFVHdZ3dqd55bO2TZx06jZS6N+ndaKa6Mo91RWT1w2Cfz1mPZChJ52EBH3xIg'
    'Iy9dX/4j08TECveXnHbVyzuqtNOwDnLTIeYoDbxwsYxQsmjuEvQXrrDuDgrFBugeru5aUdnjFdFxS1k4'
    '8CNOIlVuSxP1ZJe15aTBdNJC9fKpBXa/C4n/avxz/Hl/4UtRQNfBrEQTGCCU9JN9MGEdrywnd3YRYf7c'
    'XvmJsK6+oifPz22N4qbeR4yQn3IJhoYWL0YonvWnWNfk+8ip/0zDWgKMOlhBMFA88e5YI3U2SV/3YMJd'
    'SsAk6xgkfxv9H/PqgfOWGEBKGePq2sskTsw+Kk5w/MTZo2zfojVC0yxPE5434Jha4ZXAy/hfOIot1fi9'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
