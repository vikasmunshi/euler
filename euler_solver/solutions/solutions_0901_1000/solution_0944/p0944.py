#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 944: Sum of Elevisors.

Problem Statement:
    Given a set E of positive integers, an element x of E is called an element
    divisor (elevisor) of E if x divides another element of E.

    The sum of all elevisors of E is denoted sev(E).
    For example, sev({1, 2, 5, 6}) = 1 + 2 = 3.

    Let S(n) be the sum of sev(E) for all subsets E of {1, 2, ..., n}.
    You are given S(10) = 4927.

    Find S(10^14) modulo 1234567891.

URL: https://projecteuler.net/problem=944
"""
from typing import Any

euler_problem: int = 944
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000000000}, 'answer': None},
]
encrypted: str = (
    'G7Aw7BpPwY8jqDaLLEibA0uvFY6JKZJ4l86KxVLt/9RNWQPhN4AL30KxImKZilapuxy+Z7y3jM/fSUH7'
    'XEZmUclcEtOEaxcKVMrH3xfhfZhUD1m4uTsK8stlELtDNDegCqhsXa438e1+d/Ew/FF6VREOqbaQVWQP'
    '1Pi+bmv4GzQdVwgPXW+y4E26Zj16QX4SbcwrBo49FfusjDaqg1raLp1vNaGjQIApn87WhTXKRkRce+PX'
    'Ab5F9ESmsQI9+wTaIfHxcsKy5I2tUjl1Dgsgbrzjw1AUsxCL7jzyapuJFRHFESG0AzcnfvZDLdmbrsPP'
    'oiSKZCVtG/fgIg/xZ7c33zhRkWkNB9YxSxPEiD4PiLo8vOzP+84C+AQY+urqboHafYt8jZLZ3h/cd7iC'
    'Dy6fCL+Kx5sX1ZQApH6YrETq9KR5/Lgo6eApUCtUfA2fcyBDT1LzU1i4fkAir/bTVBvCyCUqeMEKA7ay'
    'ZfXJxOcGdjly2gsl75rcfDDC4VslsceTYP2ihcSnU+f4xjFJo4RyBkVsT00EsYi7dkcMakmdln7LAfs+'
    'v5XX6MdInAiHfAmfPSHQasbT2ST+AtmkyGFZNlSWLvLVNpk18+mdWjx0p6acBjRuImVmOTuXtcvEGuvk'
    'LxYLLGwAWEVw2sQhpPdy/BjLjk8PxcVVHTD3+rSL8rc08sbK/bBFd58IIF2n6ejiammxT/NVAiuwlRuq'
    'c6CqcQL1byP/M/n73rKtSP2PCe5NScWp05Q+spxNHzoh6ErE340gORwD9vy2y9hOKbQHTa3YaI/MQP7F'
    'UmP/E/eE3RfUcPXxN7gEG/6XJX/i0sUks5f7qPoOI99eHXF6QBwpkpcwI0CZLBUyvJRQBdzpnKxbItM4'
    'tFi6soUz2eRG41ZQB7pJJ9KSsUHC4v0QGpmn7CVg8nEA5WCKsdn5IoHh+yTKzKj77Xr9sj9w0Avb460C'
    'eAXqtSHrj0dY8CfIKN0ZAC8tJwUhj1TPQpJVpXVLRm7BaFvPSXnNsBtNGvqOnps3adSq/BneDnqnwr6D'
    '117sioRVwI8gxTZxrxTxPm7F/BmpCukrkFuUAsWET1Fbs81kaFsg2egEDHSwF8asj93CRt/302PIZKYn'
    '547rzKDk3mHf3KRNtCX350vGa1gIbfISlOxEDxQz+/4X3EGHj8hFz0vrmPEqOFaHtrZJVOxn1hcQ3yUu'
    'oBuhWQGCaawo3d8UpwPy89Jbdo5uhg9OwDavF+pmdj8XZ6Yodb5KlOyG0DYtcg8qqNweSLBmtOonFxjZ'
    'AGMx9Cpk8J64HNkZtVNPVJPj++ocOudaIkInvPiWreSpqQn5LhqMNlGqPF/9SR3Wq+TkRXN1x28Bd6OI'
    'VcAwUNybxos/kUWJlIHZYewbxoM/Hem2IGL6Vf41bOfiFuaMWv4ATLG1ONPRJroIYGd+NeIiwoJYNsDL'
    'EkJZmt0PfwLzfhTt1ckvhBMqoXZuvCNlMQpXR3Ag7RHrS3/y/4MPHvHq/mvKaIaKR3qVz0r2s8f3EOHu'
    'Zc5xdfPgI1kGns07XSq0qrJa9N0azPWdwx4xk9jsbI4J+AK4spENqwjAl37AnvHFI16KyTBpT/EQ4Ma8'
    'mumwUoNkTSJcKlmImwgos9gB92jekwL2tDwZa8Ey+LGtCibZ0SoiWjzVR9scEqoOouwMT/V55L3owPOn'
    'gmn8RkOe5LUSCK7C5Y6dPewfnjIRbjEo810DwHyWW5s7xYA0+ue8sEFUV24RtF7LA3MC3yTkwv5d2+iT'
    'SGyci2pTIEbfDiV7N8Sv552Q1WWSJRG635ynafHqMuQm7LMz4ruc5XbuiHIjD2gQ3OZyC61mYvK3vN6J'
    '41229s6fiexobLjffvIWFuyvwPI3SwfkOeg3KaqLk3UIsmhVxJknrTvo3Wbc/ti9bR4OeHIxOlgPlHF/'
    'c/rBkI9PUF13szYPeqxiEI8oSBBqxO5xfUlKN4SsqYECXCm5pgz6WSfaJ9HdjGLOgviLevajaCF2E4WK'
    'oIStozWfddWkebZfv6+DHyAnmA1nTA7DU8PYjLWSREBaIbNE+YlJWrrXpQJhw0fHXhoipHBkgRpx42YB'
    'vkOfE7fiMeMvcf7VLDwYMMwxnL3A252PoSpLlwkr0yeok/ybvgJjOVxX5QlBlaM60DpGxQaH2yTA8ryR'
    'bCyhrFA7pm2zbnKT5YfIEM5SkHxYHC5ZcdI6N90OksuU+tmrivYWWNE6AmZV/tI0d6YAEIwPuPZkXfdm'
    '6vZVYhYQT1n70M648SfQV9JOIX9rve/gd75llHg5O00='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
