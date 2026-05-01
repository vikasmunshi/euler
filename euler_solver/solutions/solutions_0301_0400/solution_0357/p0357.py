#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 357: Prime Generating Integers.

Problem Statement:
    Consider the divisors of 30: 1, 2, 3, 5, 6, 10, 15, 30.
    It can be seen that for every divisor d of 30, d + 30 / d is prime.

    Find the sum of all positive integers n not exceeding 100,000,000
    such that for every divisor d of n, d + n / d is prime.

URL: https://projecteuler.net/problem=357
"""
from typing import Any

euler_problem: int = 357
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 30}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 200000000}, 'answer': None},
]
encrypted: str = (
    '8VJzQK1nj/sQcX0IOyn9K94jjIGsTGgdWYYDdWI9MfEN4MdbRHvOTzqNnk6Wn1hNCSiatD1L1SRzgyto'
    'DBqPYSXinuwX66iVx70l2le6RfyJbkYqR3fv1hxLa9mBP5KpJrYvuDbHkYCo8s11Uu2CNWK60XLg+XhJ'
    'e53FNesG8EXuUueTImLGXttPpGq/I71IxXTmsNu39WZnF5fF1rFnUx3YZ3kHJhAo85v+eSFgKocFRufj'
    '/jCHMJBJ2GMi7nsFJKzuE5T8IHYej24OHrHuPPjhRngo8io/U8FlWaKXCCSWIw23QAKm5/JRMWOfz9X/'
    'XreEAfZ1LVm0jQ30MZ7gdItxMBY0E+B8fC20GbZlMohES4HTaEvajaRycNan8dGyHfMSdsOzxbMBOvmE'
    'WmjvYC/qcwyjQ3r5/XgIR+nS523FOdGsv7luIiurlTmEqOG3C/gbBxpupQ4JS+VG+QveMjdoG2CaK5ZC'
    'xgORl3OKTPFOZtjOovwKHWr3QSHhswb6vhnAaLHvsk0dJOxQ6PO1sPZl93DZQAkeNtDLf7u8eZCRQ0fL'
    'cM3aOi8tf2TLxw5imyFtzz1BFgLNJ+U0n2OqfljWiI7fHk/bC/JwC8k5yukRt0qMfM3mwIU8OKdSuc8/'
    'DkFG00ZNduSKEmRuQA26OlETIxfqyFXyoh9bD4pCQ2/r5I6iZ4r+AtS7yc0togCRaYmNflNIIdzS+870'
    'Ti24/3nCKhaan410fqAV4rz742uQxoDDHAV91YWPUwXTaj0yVkn8SPd5DTvmFhHHixvZOl+d1fX+/8pm'
    '0/Shg0aAbYp8eG7UXccSbVCk+aVexCuO5YqH0G0tmM3rkM7Oj0pkN0qAjj2GijZMWZNgN5wZB5atf21F'
    'hGUUx8NWPRcXIHwYss7wTZrY2ZTh4X2KYpPb7nHhOm36kHvr2zMhu8UaV1CKE56JrR0662DDCODnOPBG'
    'bgm9GSEsKmwy2dn2GNzMdqv06VrZoC83+dVJjVKZhWDkjtRtQjCRVOeGCPWMYUrB+IYYYpJoQVRIfonx'
    'QpHF5XuTyBZy0bmiPYCP01iJ1NgATnb5gID5KeaVXAaxxX6RunHuIEhO3P2WlKwlSDeR4H9nQTTakknH'
    'M7F+tXPthl3tRonIAkZsZMf2DKUDY8evC4vNf/27BI0Vd/Ve5WooV5kzdaQbr8Rjn/j4IH+q8nJXhDQo'
    'voCakO+rY3Ioj1q/Lzb7tMOv+efFSS2n6NcROi4TJqJXcexaVp/FFrmi7v2tT5FQ23VQ0C77qJGnBmrs'
    'wmBgZccAtntrEFqVKXNEOPjcEgVZRMYi0lUw+CZZMnBXyI6W4oukZuVSgtNwAmtD0u+G/OiHXtf+Kom0'
    'V5UYFvLc/pqw+5VNQ1rkxXJohW5rnsW03QuA3TOXa1/pCFqJdTv+QXPQi9ZyxkobrfZSNI7BtiFLIXw/'
    'UgZ6q8nTYC94GYB3y65RSDrlwmSjV3lu9mNoVNRnnMI69BzFtfHjWNAHmhdml47pEyJ3ou6eKPtCoakX'
    '2/IfgQK1MNRmQNgpaqdqgVb3YOk2L5na5vn/zB6Z8w3hnLk7TL+r164EUGYkz3AaiGxWFZZZcdrepd1z'
    'BtkqsbFXxGrZwjie+K7q+gt0Xyt1uu+BQvBtaeirv+EZWEpbspvWxJlWBGhTypwoyGfUeDfGF03pCcbw'
    'ops52HZ8ozvnNooQfLXElzGY90ecA0FLyJWyfTqEaOIRYgfN5kzpz5guoiTW/SLK5P1bMGsbZmRuaf64'
    '8VC5vME0GD64e164Rn9WSOCdwDeDgQ3UQcrYVp3qCSxBkQSCIQ47QoT5/OR5154R/L+5q7eEEow5GiaD'
    'u+LEHmbNrRVhSj6ucx+03gdsdUN8LzZR9oMFgiSEObl2NA8HyfC5pVw5IYW1U10mgtxjz2CKHRJlrxwz'
    'C8Ygcqokw9fkfkukg0exyv0Yvr2Ucm3fDSOg1x6xK1V/D1cY+cc96A372Rp1isDbAJLwDQFr8+Ag9+2T'
    'J7f/f+Ui3kFQZg8OmKLZmn5KEnw1qbOMFWw/vBCp5fcVjLgg7hou8FCQnaHpCKMNzyEyt8fNF5U0rzQx'
    '9r0XlTUa+eYjFegmBX3pi8K/fGxmeKgTvI0TsJ5D6hs6/I+uk5+074/VVtys4mA9V02/M2izIJM9/v3j'
    'oogpDsbrrA3WGM4tYeh925Ls7vZJ2NRI5kJzA7MZhUEUwqiAjtd0UQhvSa5ujtNwG/Krnsa92i61VLcI'
    'Ap9UsIWqb+xIBaPMlpHKZSg69KYPTW01MtfVPCXKgss+9Wk6tWXe5glo6nOSTlua9wjI6awHE9RFaSCH'
    'laLZsZ9miJbKmcTueat2gQSL3uvkVG7BaAOkXGE+MfuQlGrIWMWjxsQoJvRz95UfSl5XyWTqpw1HQoFF'
    '2CELAQpYH+GeavKZlhDgD3BVoMtTkgxza5I1xa1MEYeFe/c3VXYen0bjcDBTYULP3bWgmTaEifX9QVwE'
    'B3st/CXUmD0+37vl36kLuJXb2H3AWg1Xg9rHw8f4Lrs/caGJmKsqABY/mdWobRQLoJ7bNlrfpPKzDVM/'
    'CcWbZA1e5zrEcdf8xKAserFtyIiO0AuCw30D03xegBXLS5uSpb9LnS3DF+C2r80U'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
