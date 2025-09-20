#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 713: Turán's Water Heating System.

Problem Statement:
    Turan has the electrical water heating system outside his house in a shed. The electrical
    system uses two fuses in series, one in the house and one in the shed. (Nowadays old fashioned
    fuses are often replaced with reusable mini circuit breakers, but Turan's system still uses
    old fashioned fuses.)
    For the heating system to work both fuses must work.

    Turan has N fuses. He knows that m of them are working and the rest are blown. However, he
    doesn't know which ones are blown. So he tries different combinations until the heating system
    turns on.
    We denote by T(N, m) the smallest number of tries required to ensure the heating system turns
    on.
    T(3, 2) = 3 and T(8, 4) = 7.

    Let L(N) be the sum of all T(N, m) for 2 ≤ m ≤ N.
    L(10^3) = 3281346.

    Find L(10^7).

URL: https://projecteuler.net/problem=713
"""
from typing import Any

euler_problem: int = 713
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    'dLtxC4T4rfmBfiHIt4FykIV6jP/TFnaCJ+4m+eTGgjsj86K0TO5dnjFAqwL497anNT6HCIVvJtPRvU3G'
    'D/+Hq0FVHf4ajyCTq5kHi+lsoNnXWxyanaBu1XtJVmY1DYSD4uis4hGMFiofJJgUX3YNBP66PZGqJw1U'
    'mc+5lj7oDGYzuXi5CPS79PRDAauipmo+NvnZMS4YBHJj8lSxEGpfd66QE7coxEZeviF7CVVhEprYCICc'
    'z98IF2cM/J0GTtYLs7yTaZ1vaRAOimNhc+jE8g2Rv0l+wa7tnkJEN2a1mE5Xey5dbET+sDpbvE31Bkqw'
    'S47gNeT0T+7mzlzsCNM9RhIxcgPG/ea/s2ZRpHOY88g1ciArdeUfto81fkIZtdPFGksSMM3bfToXpWRi'
    'Us0FBNXm0FeB0gaXBH/4kf8yn8mVWoHBE/7JnjjtPJpqB121WcrwQim95INZMhNxodTsvNxt5jI1WUBE'
    'ape3o2hmo421EXhHEZ+PCmUbkGx5l2nK7RHuoZIu5lekkCwVmgDrAXK939PwPMfvPQGFAZRMHZtVK5SW'
    'Q5PMeR5FUNgIIf1Vr05O90sLKIld6DHxbUJ2YOcTEe43Ac8ZYPgCgq+hHJlTi/OptyEQkJqFXt9/8o2I'
    'RqAbmcM0Ol0Q67D1ice3IHI+GyH/SzMjrXvS/I+tquNSvMJMKA1GZGzt6nOtmmhkVfCMYn+Zy+1iOzXi'
    'DiPnRn2j4jJuD20pw0AgaSGna9VcXRzWsGw5zHTd5Yt1rTd2V6DU96ULJGTY2u9jEZZpgS6fU7GKlM/M'
    'OPoKfJ7gajv3ta/OxybITanTSb2odGroDxtKlIUtuLC3UR7XtXi358Vh+nyNnucs0zq4wZ7fp3frUW5o'
    'dWygnw9F1izng+MeYop4SL4ojThi6+SsBkzox25X7B0P7XaJSBPPJf0+MUc67hIVwc1yWtqL7g0w/NCt'
    '/6WwTw1593vSBAuVTxtmFMgaDyItHcpI7s19UU+EpUBmD+M55orZzMhpfEZhKGGmm0yjy+mVhJcw5N1T'
    'a1R8uC9vm/HkIm8KRQb40fieSYsrz96MCTbSeR2rcyyIo43jG9yU5yCEQTYXqnqXWFKddA+cEPynoNdg'
    '+wIcdsiCBIvMaC8L7JUUtoGxw1ZkGASassV8Rcw0rCbZISkRW4EFHmXW72bO9gXGFDs2iV1y3wHJKKW1'
    '1gsieMgo/r/PBIu7zwD+VlYuv/L+WS6Aqj2ooqDT4CKhc8lP/JXoh1rQn1wJFzPJfR7+4NmTSJLPf/oy'
    'g4oVXcBQwAc2RwNMkb2kDaZfPkMW9Nd8KCQ3IIDLwKut2t9TT7VxD20s7kXS7ed5NBRZi+VpcW22KqN1'
    'DxFgl94vRBCqzP+345Fc6PgGmjs0mkv4Eblwhi9RElgQT6sildvh8TnQ9NiRaUJ/7zoiUk0a9E22RSYS'
    'zB4WZ/htdJJxGCkZdrOV76tI4o4Lr/04m8Z/UojGurRB2VtZO/FLD3l9SWBj+sOjweLXwAfdOMo7mv5b'
    '23O744MECKpqvvCtHqCQpkTW5zSx/lvJKDZZ0nDP2njq1roNWN5EBN+oivZyVWNyZshr9Xacl3VxcdMm'
    'Y/ZdZhGKKWkkKq6pSPCIoHTE3remoTJwSfXNaDOmDuUUlYgdh6E+hOa6/0UgPNqmDo/42n5dqPGhjGmH'
    'SrmRWA+nWCW8bKZ51SGwye8eT0CDgcbQxvyqn3u5cvFc1NYvUZt7t24HYrjEqKdmPgjggmunRygsHCs1'
    'e+HSxcjU8s4DOaAwgtQHAD3hPv3yZr8/I8C/4dS1Q8bsP/ElQuZ3DE8Io3vCrWL1fVXRWpdAigV66l5K'
    'LJHbD+lFxgadPwm7SF00pjQs+xHwZkvjv57X3n8ChqIR4cF4e8lYacPYDeTGw1Wkt/uVkrWQqVo/Qx99'
    '+kJDLYHw+MbpKz2WvTV5oNqjKOxRx0gJmlU7C/BEIHAqSmEK5Mm5AYN4+7xCp+hT0HrHh5kxT+cz9zQr'
    'ZP25Mrluo5ZnvIbs3vYXMDr1IgoLc2N5np0n9E12e4ZcJ9acTKnXqLU2jTy9ONLuYF9sBJdEaV+mIPhc'
    'ciT7nWcLe8ldWKfbAgQnsH8NegDDW8f2xNTwagcZEoIoV2DRI/0LNpdXweSWF3URoF1CzPt7YW1A2ohW'
    'XxuE3ScrUYkkkeyIrEd2ZVc6ZstgV8K1ITUOy+gqHttqMdi1M2if3A/c2MWeqQdZSSIIfNTxOhUE/Edn'
    'CAeP91lUNziOrqAPiG3Sg/XgQdvAMTvSEKZ0NDNrLAC0plUTPaJ7zE+cyYIhYp5bciYkZ66qzeHSp6Bd'
    'P16R0h3Or8OqpfNhKD+D6azTnr2ZUIBbSzSe12Y3FLE+ar4m9prEGSiOLAPMqx5JRL8kKP1Jbojjx516'
    'Y5jLvdXDJmq1oNfVcQKMqN/qOFHvThNXKqmenWaKQQD4NEoGlvHeLvZMuIMnqyHdoG8rJ3d3WLCpV1G5'
    'Ft5LLz9y5Wy+/tWSRlOVijoiGb1p4CPbwbCN8E56DrhTIHR6oIxxc7P3z3MsJau7P1d5QNVk2H7WId78'
    'Du5WvyR+Nq9H0xJqfrcK+x7ZlHcCUgSkh4vztdn/Lg02G7lEEMlAMroTTBTtD7ieurN4Pt38j0RuZrSB'
    'OQYq1h4wTyqom9HZYK0TAQyc+8kEEpEzUiICDSnsJnsXKFl5/hOFZS4mFIFObmzYm0w0Y/gMklYLdlp5'
    'nvMKWAZjscoIe8gkV3P7CZanxdZfjytnTlXrO85QIIMMsCgL0ekGPVfr8LiiGlhxiZbYdpqRWKtXTKNo'
    'wW3Z80pP1GeLmHGjlVLFHzAxd1N6rfttDMZYAF5Ong6pbDNOXzIGK9J5SVL1jNUBWH3dml1SBiiXr6FL'
    'EPNVLpcGwMB6c4mNRmRugKNFrRQnCBexrTMuRwGk/5rRByTrPLhdQAcTgKrxgXmnyP1q73Kcz0LEhuA6'
    '4Tg4EqcGf4oHWesoyVRxGFDAlyw7k7gTZrUHZfpI6TgiPvwf4O07Gs2Ew2NpufYdJK2ibPgHIk9B2tll'
    'yboG3ESU1o9L3YrVGstu5Ivc5+vE9Ik5ejTpOYL2nTSyUX3+JK/k7pjeGzS4rQMD0/+4CwPm7zn74xmT'
    'wdEiPzsu3xMN1hpCdBsFHYE6wy+fhGb/bVrAMMHLmbwR0skCTVyIE48GjngNqOp/rwMrYGlYd6ajo/G5'
    '4pOjPU8FJU9cnIwD0UJ9Sw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
