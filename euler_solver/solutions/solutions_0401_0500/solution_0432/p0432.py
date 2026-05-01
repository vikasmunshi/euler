#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 432: Totient Sum.

Problem Statement:
    Let S(n,m) = sum of phi(n * i) for 1 <= i <= m, where phi is Euler's totient
    function.
    You are given that S(510510, 10^6) = 45480596821125120.

    Find S(510510, 10^11).
    Give the last 9 digits of your answer.

URL: https://projecteuler.net/problem=432
"""
from typing import Any

euler_problem: int = 432
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 510510, 'm': 100000000000}, 'answer': None},
    {'category': 'dev', 'input': {'n': 510510, 'm': 1000000}, 'answer': None},
]
encrypted: str = (
    'HK8uxkrXeu97AXJ7ejsK2J45yxRFuUevApOQe2/Qr00zkNw291nbMaxbuLsoAT3JilWLRZyigMHH6bzB'
    'S9W3UHZnyVKelOvqNoM42STloaKyishTv63iO3GFCUTuZCrw0Zo4tEswSbD1mBD/g5H5NlT6Qjc5cZkV'
    '0Ev+uVy4dbO6FNMDXIC1kqxmkLlTZwiD7fWPhs+mB/SUyNvtT0VhF+bpo4rn5NXZAlZlAMQN7NmTShuW'
    'A1FBFpFLDtkuqdQeUwWbQbPIRphTXgKzdIBXS1stHp3SZl4EV2UTIzXAcUZl6qr+hDVXz0IXv4wei1at'
    'rMPRC4GH4Hffshimc5T48rGozz/oTuFPlCQSurLkVHmfb9lCb9WMJXHLP/ng81ahuat5Fg7F62ZB8XTV'
    '0NShhk2BRQCsNEczxgyCJRHSGgKlBtCJDLxoGsRmUDuhirR7nCDZFYxBE/8byaE4GP89II7mV5R3cijw'
    'MZgpE0Qk4N1OVxVbbOH0/L5gLPkG7lxMt2lx7ebQMYAWA3XeswZv778vGm6iCUsXtcxYSMIfhEJTTLRM'
    'LBPTGsrY4GOcaewXxya1FhbtDfPUR8tX1i/0MgtGja861oJZjVmYK3uE1tEb4cGtQjed2Sor9JAiYJnH'
    'lj4nhCw4y2GZ8DF0QYNniJN3k5l74wHUfN9Lo6PDPwsAELOq8TGw22TBIaZcip58JkSVR3tSaeu65QuX'
    'obIoui0TOhNkWbzoe3bg2nIOuK8X7aI+ZM8o9NNVLHzqRrEWkly1yfhlS9o9gqnThmQrpLGs4tMtLwXq'
    'I5pKt8uQF3RF6liNHB6HD+EtQ6/MQmlDhf5GZnGU2zYFaWG63edMiDW9xwh24nxtwbRRrbhWfME4KVM4'
    'gZQlHyzkJvQ12wEilSJiYQmRwX6cidF7yOvavUW1YBnQ/euwgiUR0e1zKz8V2kwJhxqOAJ0fsyB4PHqN'
    'n1e8mMvVWkS3jtPQ2T4o6Ly5owAqfVYuunhMKiaKhOb6dC+kRcMWkPg0386AFT3+yog2HTghIyhuMLeK'
    'q/Bm3aHms7NpcD6ktGjMtEA6JhoCrmdYwuEv8cvh9xYCj6iyu7HWx5kjA2y4ZZ8f+o/T8TLbmTStM1IS'
    'eIy+vhl45JJQujhbg646z2/UkE5xX4GrRWLKJfszPabDi4LyuhIG35RDbwVmiRDovI54r2UmjmMpHP0G'
    '+6cQIOyVdqVC1pOwBvO1+ZVSx3geIMxNoef+fx8u9yk5gwWGzksvNMTXv9FyygIFllpQoJiMgzkZSEZW'
    '3xFAEX/rB/h14KLvTRfY0T8D8JhkMwEGEOHMCLs6mcCol8dc0xT/IbuoX0ByFi0fWgeTZF9B68zLMpfY'
    'qBJFvoQkmxuY0HJq+uwKuqFvpoVa9JX2ab9Ei1FWSrQEu3c/tphvZkM3MCv0EopaB4YI1a0ewQKSP6I+'
    'lm5De6bEONpUSJvCLgMRpJTAbcL11tdn49RQveEmT9PNLD1Pwa8mL5ErNNHdro+mzBqZtUntZeWDTQJG'
    'lZe15UjDUsiRDcsMiIzr91dpwwhZpfsO2ZDq/EVc3884paVjwKbvMmgKlPuMuankEDQxEkViGUJ4xTXA'
    '01Wnt96tb6ms7F7aUYtO4D1CH1azjHjjjNVqSPSW4kxvrtFg4v0v0kGBuBsMBmZ0RUWtnN2t7kWkETd2'
    '0gK1AF+PFxnHVsAntYgssZLeTjWOpwae1tze3/AQSqz28YLOG31tIesibCZax1P/G+3ExSANgQ00/dlp'
    'vqO2I8+GVScEF3YWvJu/rQXi3Ah12uyNMUk9w8tc7bwYVwmBRNJscRMHwLakBD+09ni7aHZXtOgZqSd/'
    'gZpatuoPd8L5M7aiHS93SZNBjrkuzMorN9FyN0MihjYBYVcn5FiRkb3kz3LgFk8TJX2aMpJOeMF1UVGZ'
    'BYTtigccsqDzhgmjntJj05fAohbw42PWE54eQNCFskK3oW1/XytM0stX2by/+YchGPAAAIJ+QTQi0Xm6'
    '2DDjvm5AIf6+H1Gh8MLHniLDgwoI+tfwohvQEj2Bs3m4wtxA9qg32EwJo7RHINHsKDZuPjebXFHXFlN+'
    'pISHhtT2rg+O+UsTVNtmPqGNZKan1WIO7mHe4fgCoayZsdOzvgT4zQNi5EIznE+xno2j8tX9djkjnP+m'
    'tqdVg1VzUvMdKdyb'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
