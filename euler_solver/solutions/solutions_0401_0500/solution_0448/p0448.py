#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 448: Average Least Common Multiple.

Problem Statement:
    The function lcm(a,b) denotes the least common multiple of a and b.
    Let A(n) be the average of the values of lcm(n,i) for 1 <= i <= n.
    E.g: A(2) = (2+2)/2 = 2 and A(10) = (10+10+30+20+10+30+70+40+90+10)/10 = 32.

    Let S(n) = sum of A(k) for 1 <= k <= n.
    S(100) = 122726.

    Find S(99999999019) mod 999999017.

URL: https://projecteuler.net/problem=448
"""
from typing import Any

euler_problem: int = 448
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 99999999019}, 'answer': None},
]
encrypted: str = (
    'DXe5L0UeyQ5upPSqVUebkQ7z3VlySMzEP9lS16IiPdt1dXlIjjhFpquVSTCWask5c+pd/VIuY8HgnX9W'
    'YGGtkMz7sCVHvpJ0f3YVUvrYYGKJt3Yh8O12BaXXdAnl7jMxM2rqc1pRbyQ0dFm6y7fBFBFJgme7NqBu'
    '0+RTnyZbvU2uoh1IYkkPr2AyE1+fCS/cCQ57cTG09sNjz8uz1OwmwbBaxkf3+w/Hm2NncXmPO/NOQ6xj'
    'XZ6U8cxUxOp4rwUsBG58/Q+qdGtSvBWdD3qQPCfJjqtrec6kXBMOgw2lC1D5Aby/9wn9pfl+Z/2F9uSi'
    'EPaJx3NKL2PPaYbyl70mzHGiTW9LGLh2fEeUtqMQnLNLJfo3LV2fAW4gu8o4Xh8Khn6w8qOgmobHMdoM'
    'toNn30m45dNPut4iDIL9lavIVToodaLRbtWBrMxjEq0dQf+IH7vmnqKTjI2JFSpIYo0TgQQFdSE7PGT5'
    'ZKXJA/ppm/8t7oDrZ3WNhCqA4jwGEDyIVvzqCcqAKtFCsBljPvVIyz7OZMiyXUOd5Vefpbz4ewrznqz/'
    'NSvHg92mUiioNqxsAyrEKRIZtkKU5FR3md+PnfrOvQBdFJqfFVSA4J4DMtZOZtrCxmlM/27BqAYKJ6UZ'
    'pxxEDsn8OdKkxprTxp5OmzhBc95jqsMGisPwK7XRlvMnvo51Eu7fH30YVsfEE7Ph+7/UNMF9YRShSF4t'
    'l5x5zdNtiZ/BRT4XrECd5YjjSHGD1Kzu3MpriRnPUjN9XMuHztbjyCj33giElrCe9RHs/rOo23eXaubd'
    'w6ZhbvBZuwJOvKqWKEPMhpclgWH/c38/vOtdXw2ybfWconmtZ/2mAAL11tS5//WrB6j6qdXE8C4c4pXr'
    'l8oF+4arrh5tYU20njfGV/JOokWds2ecP8WA3j9g2vlsXO9g+hXqg2UPo6HfaTu3yuxgmZdN30J0fkYz'
    'W2xk+hZRbh5609SIS9Q2c+YgiKu0vci+GVtmXhHLfjNCXJMTmJ60rAeGUvtjco/Ghzj3vQaseXXuoDs6'
    '3hxB/p9xvveZlnvNnlGSbJ6718DhAFBpvH1Ug2k+wn31gh7uwZIKwLn8qHvUPj2PfRZ2ieRWDGeiy+gE'
    'ivofdARP4VIQfvAwMPhc8zjyvpqt53fjxPun5+5ce1P1zvgC9TFee0cCqpTsQuWJmILNKcTlTnTV0OV5'
    'KfRsKEONDH6d8BonhmkqeTlm/jiBbxs61JLBlyT1h7W05B7VyZ5/3QyArpgNRfKdMcQbZfrzcy131GoK'
    'dfmhEqDjbaPYzGaEN2yZZlD4jKm9nOTCObyXloil3kr2RpGRPzldeRdAoo262m87jyrc7JAIB0uQhtIL'
    'jCYxriYPYEqgLg0Hraip7hHl+WzfNmGGGBVkyI1vWHYjHJcBr0tSLu0fYwhUppR2wML/orKmmoMHH91S'
    'DvTH+mw32pz7MrTVRxxn/Fh1bQhyhGLYM54rVsD97AxSwGfR6tOjxEfnMZeh9km8Bzk5tN8u+stNwnQG'
    'IR6CGOkVGRTciLif65BdFS/KuDGbYSsFN41+/u41D8xZfb4nxLze6EywxN4jNYSho5czYwNL06r7uFbW'
    'z+VWrA/dqXTh4rnFDBl7lm/Y4J/jIxCffAfg7bTqrsec0ZZXkiXk1qyou2bfZJyt6LMV7o+8IltACfw4'
    'nV+i/U6aeiKkMVw9oThlp7QG2yqrbm7f3UjH+o32r/MQQZxaNP5O42zA3d2jVA7fqOmMYf5bFq81qd3N'
    'MDSV16EEHBwCBG2yoqFH5/szp7bVLscfG4ozGwfusbP0vz5LonhXN9onz3mt2wO+Fa3g4XBfPrauEb7x'
    'oS8pYrpOKBroS1qwhyiFziHhQndMUyL6EJ1NwaUJVzzSqTsuYiMpl/okoa84Ktif6hQ3XLVnY3M9dZwc'
    'mXTJjSGb+VjG4X+7HuH1Qds0rcVQmxnqG8EYeKPDRraZOE76cqh43uStakNFZKHHxegWLpzGJPDJ8X87'
    'fbKJrE4d+WYqR/S18Nq3Q8BHX9PuAJ9MQDQUhwyc2PI/IFCLKHl/1umuaN9TA7MHyqsNxhfc8Lu6pn7o'
    'KPTmkpJcI+ATBzy8VOI3qE8WG9s4O8sAr20UjlWzQ+HJykmVfs6kpQfsOckgFgeuaPwnwBWIUKeufINR'
    'dsPyu6A6S/abgFZN/3o+iy46jmlFQTM2Mw6/GOklDsvWGXCNppWBuJn64eLEod2FVaKpja2MRJvEWU9/'
    'GMDWA07Y7WScl7l06SFy8DOC7DYTmym6KEF15otSHJZLDYkIOwCe+iY6CZRpbouHpkSBPKVc4Hi6p9ZU'
    'aBJH5A=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
