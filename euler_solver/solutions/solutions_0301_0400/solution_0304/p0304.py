#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 304: Primonacci.

Problem Statement:
    For any positive integer n the function next_prime(n) returns the smallest
    prime p such that p > n.

    The sequence a(n) is defined by:
    a(1) = next_prime(10^14) and a(n) = next_prime(a(n-1)) for n > 1.

    The Fibonacci sequence f(n) is defined by:
    f(0) = 0, f(1) = 1 and f(n) = f(n-1) + f(n-2) for n > 1.

    The sequence b(n) is defined as f(a(n)).

    Find sum_{n=1..100000} b(n). Give your answer mod 1234567891011.

URL: https://projecteuler.net/problem=304
"""
from typing import Any

euler_problem: int = 304
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000}, 'answer': None},
]
encrypted: str = (
    'MTjVIC+vj2zGbic9m1sXTgCSuBJJRNCHY9jY+AewUnpFTZ2klcqZzju2ayBgMOCd7XFWjqA2AFD4vEM9'
    'sLvb/CwzWwaIDjk6lcn6zFk4vA1jtuwFc8ICH1RJhMNVQLloKuVxzKiZQ9HLds7LEU2EBjPCco+gAwbZ'
    'abdWuIriK67CR5gBXnGMMBmrjYs3qGvFfnzMGnGq99JkqxhWDMCabCNBR64no0w1wKhSW1l67k+8GeJq'
    'fE/mE+jjZNnYYAd+DxAr3lJUG54UPd2cE8Wq4t8se6r+KDwWYMus1vF1l5nuYAyMJ3CmVcb5uAIjhVks'
    'hjXdrEop/On85StJ2mJZEWPAyLA1ZhXLNLmE9HRk9yD63f2ws3oMb73CLeELoAmFF+cIpjhFrOYGFlHi'
    'U8LzqTlPAh2DI3H147LSGXF9s49di5PuQ5rBow2gui+utCALq7QFLCLvOiyZHE1QJtpAdrx20MqQfjZs'
    'Hb74cTgPObHSQgb+u31WH8kK8vFPm8rSdpdxBMtNpHJTRXpNaRFNTlzECBmjwK7Y2Y/kVJ/X1xIN0cxQ'
    '55C8WBuGkn4NT4uCy/pClyEEZMCJYF+fVqLnKqIxonPZc1svDUukkIvHJ1NCu/IZZmLS8ktBbYw5435S'
    'PBC3DB+VKi/Nvjpy8Bp17/EtNED+m8ZaNuuCxNBP6YY0W+0fbOoDJbg3duvmIT+9kF9pXvbbQdckVDLs'
    '7ONg7xpD4AzGNZvmVcenhed0GA2FQfQ/6YsCHGJ76bH5xtVDOCyUXA4JJ4/a++DAx8a5ZAv2XPYQrswu'
    'I66wE4f+kmRdyBkOJ0l79I/Mqu8d5QFlbcFTZ6loO40+xq01Kv2io/l0kcK3vo+aFVDzUmbbRHNLBq1I'
    'P7Y5arYsBYNCcfetf44X1//ZqEfBiDX2QbLJDmDBysqC+hz/YqUEmWwmdSZYZpTRxImzUgCiSH7rVXQt'
    'JEXT2M8YNMoaFuOkGTzWG7ikKdXwBqPWBctkZHRH4FYr3C5vxPJYf+zrzySMr+X8mAbXhDi9ia2PMIOp'
    '6vMH5Yd62vEL/IS2kNceAH2oCu9Q0rJ3YAeT3XGhWOrW8Hpau6sjAtzyKmPJKq4OlVbox79B00kX1Uq4'
    'ZDfeoUMvR+eT9SoNkbXUTRLT6m9yt+rlmXZrOdFGn4IOsegt4q+7K5y/4h21IC6cfwXEqSoM/bHM75mU'
    'TDnREy59ktpHwUsP4JKOf0mhcImG9G3GySH73Z7fDP+xgpelOYeSuDyFRnCnK8G9IiqVAaMXZGeV+bmH'
    'SNwU6E4XsUZyEdLSjfHNYv3fJBmB82wQQXL4zczKCBMBd6C/+y6gus+EzZJADKYy4UpzU+aavqq1neAF'
    'k4r0Zz+Mi1TVrN6uxPabxSjX4jksHJjNhUtECogBS00r9H8ODLtyJzVvKM8llS/3TEudXfmw5Uoa/AVR'
    '/qTkJz52lybLAquP6IaY+DHMssSrLd6q6RDQz5j7c5qJLToQrJxyQRVDqT8A1VrW/TaSI5npk29awbYE'
    'wcwzW5T+J0WzTXn81slHbqtLLGG0yxOyDjmVPSRh5PfIYP8Y5xaZTKW0eamN7Yj8gplBzuZBUTg3UZR+'
    'frnYBLofr5hSvtFvQvD7AFd/ei+tEmv6JFdFL/VUthZM09s2tunbaXO7aWqIvPhyAv2rSHa886cjDkwM'
    'wuY6J8WJxXm/9qKyu9QkVLb9cvkhPY29SIBGxOHfmn6mKW+vMHk7/UMRKRExP0t0xMyZlgjlSUFj1vqU'
    '5UNsCd66DErfrfj82O46GgIIcxSpm+SgjESv+u0y41RwWVMbD4CUQiHgaah8fquRtNtxWkG96d8hFQAz'
    'X//5RSA8B4BmnjoMya6QNcpUZjIDvoZurHg6jRi3CDP0bqK4A0Vy0pnqOciPyOTq4upqgcuBAuKgBLhT'
    'R/BcI+YtuDObQbN5L839zFQBKgg4c/19zh71FCmGZ5FWVgui2wD2OeFrY7j1E5K+Jl+78LDJBQ6ZilCz'
    'PjtC0pZMu58HVYa9OBLSaopE/tFMStQ4DSAM1o1nOqSwkNN75QOx07svluv8mXbUhtrC+Ms+CLCmxy6f'
    '4RE9a/RiFWUQ9DrrlICy+Qn6Xi7aI/V0CEiOC9VuoswFm45z/cjLa9axFfnREDVKwOVnz+7oG2GvbRrS'
    'hQin/N0TuYYNU+afSlBXiWn55uLOR8imLAZYv00ycwUAcdgTiIec06JLKnvfONNRoEKS3Xk5r3nzfknY'
    'MQOSgpN0LYa9DKL2YAq9ruFgZ37G1GHdWYXv5GQphcbXpkXMMuzufhMNNe4JR3DXjUA25uJYcS4v5WTc'
    'Xqia9u7HYb8meqXJXkR4zVSBMYg+M86ZafnQQhm+yhRIauflcRN/TRFPkRThTwUBXk/06GwMYdP13QlL'
    'pr+bkb/7kfUrX1tvkDpKKbErTlkRQVLMo9pR/VA66H1BVpmJePh67mXFuM8EBRumDQ5gKGBhBKlGjQwT'
    'r09Eu/VHLL+U6qcEpQYCduOecKDTexi8g+bC6OtNEg+zAGcUYnlVCxq5EMyp7JPJito33CXr51DFtNlc'
    'l9d+Nez4gOOwXlp1TsMy4FlGxMRY1dQpGeAHF8tQdKtSCJuS4tCwFiUTaSULwUiyf+hLmbNSlEyITdyZ'
    'zpzwcsHbrt+AYN+1Z1TytW5KWLAfcdBSGvHmQANYfVa4H9V8RjSp/pXZ696FPRAxZvdkAg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
