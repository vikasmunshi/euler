#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 637: Flexible Digit Sum.

Problem Statement:
    Given any positive integer n, we can construct a new integer by inserting plus
    signs between some of the digits of the base B representation of n, and then
    carrying out the additions.

    For example, from n=123 in base 10 we can construct the four base 10 integers
    123, 1+23=24, 12+3=15, and 1+2+3=6.

    Let f(n,B) be the smallest number of steps needed to arrive at a single-digit
    number in base B. For example, f(7,10)=0 and f(123,10)=1.

    Let g(n,B1,B2) be the sum of the positive integers i not exceeding n such that
    f(i,B1) = f(i,B2).

    You are given g(100,10,3)=3302.

    Find g(10^7,10,3).

URL: https://projecteuler.net/problem=637
"""
from typing import Any

euler_problem: int = 637
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    'FywuraRqpJj9WWyYm7sSQifbqu5rOTocvdVjddciMhXMWlRIWiEfaituPkNQhKnf6m0OVwS8fX0teDwp'
    '97VHbPhqcNy83E864Ovy/0XOmnZnmom4PqdwgREtRhmv6F6cg9onAr7y8O66A2GFKVWKciWavd+M2fD8'
    'VGKEbBHJgNnXtFiaGIEDyvwmMe+MDXn/qSSwk5t3FOy4rYrBpKONO3wwPV8oyTQHYmG0CDXMASlz9Sbz'
    'UQ9U0RXoPSCNMByz1WmZiJncblG7V2kKLytaZLSOV/W9pojkSrA4sie4Kbz93ANEHy1Qmop/EK2rTUAC'
    'k1Q6t18r2YCHU4DlHRIFm5/VsND8skR7Elp+YInOPBHt+ZiDeky9rB1uAyjJzdUrVEsI3r42jE32MPYX'
    'rWt/b18ue/Y57jYMOIMmhX3F09O4UQ4lqHO3L1Md4lhATigwP6SG4Pwqa8WdOFasVuuCyg6dm9wB08C+'
    'h7H688d49VIsa9UjOsCv1XwvhK2l2QOyiq8vbZTZCEZpBVBKabqrWxY3q/yNkU0x69H9ImkeO7li7KtP'
    'ZEF8eah37r5Bcec2nitK4CjRcu8J3oMrBCvqw844fwaVorcxowCIIoF53L/ts/LirR2Uf/0RspwrFaup'
    'MNooLk8a+KEtsGAFw/sO0N4zvI/+wqufQqtjbTewu+yPETMJos+ThtinVU+AM7gKu3Ch69MY2aJlnwrU'
    'TwvgXsLU+oXJvOZW/MBUebvPzQgzU7hax2gcu067a2yEnq0zl3YOjAmWedbkPcd+lC8z0zFxeyoMM/Ki'
    'FDg56WRy97hHtEOKICEWFVaMUNL45A46S55MIPZ9L2Uwg3T33OyDuffjo2WD362gpZ71mhIU/PNfdHtT'
    '0Im3WUGMh6vi7ZYTETKPNCACZFetRIlXSYddkcf1gslqDEA1H1Z+pP2NlFGmU806Je8PMs8JgWgI7PWG'
    'ZonmIDz+Ony3yYhEOiH2COq8TSCVeGcC13andGqyjLjtVgV7XnzKOgFTAWqA0qWPCChzt/KOc9kIoZcj'
    'zk+bHBIaTfbtTmlQiHU+WMUnzKqkNmRWiGxdSRCtVO2S/Mee6mQyEGnzh5gccJ2vbEFwHTev/sYRUFtQ'
    'ESQ2iDhDEXwZalCP48gqiz8YE53gyY/vL6sEyV6C+o9dg/rhjyAiMb1xbOmBztV4RaA9RyXGhUV3I3Pg'
    '0f1TKFArtgjb7paeRADp74Q0BgcNbVZHE1LTLfSHAT1HlgIkvs2XuxDd44WdNICRIl3pLqEeiI7AdG5M'
    'qLwAsA6SKvO2hmr1JLkDqbkjGArdB1YNuFXAFq8VbwkdQj5oQJxTr3oNeJ73ApCfusfZtzCgC0CMTZNu'
    'E94G4rrNn1Z9RupxGdHk/ARCUBN+O3lLMcOqjUdMemQuOf45gz2ztWwdKivO0NmAdAihfXhwE5d+uzXS'
    'i7YDQuR+kwePRkkU2wIeKueWfrvYTa0I8o6Jea0AH6ySpGCl9g0DqELvbeXUkY0tpjdyaccs0DRwDIlH'
    'tZWGzXq7XJWfjARcc+4urnK6/vWragqTRuM+NzsiRWLfhec9Wk4+/uBe48H3yYP3MBMAy0fPu9lEKsge'
    'HsBC1dP0j2KLCDCEN74DO7jA7P7HQ7w/9+QQin7xm4TZ00/isUqf2RIBiTF3yDGl9fn/ukjWyo/NvQEh'
    'P0YqRkEpqlUBW/s7fuNvKOPQ4BFmUGR3sHeCqC1ZTjMGh+cA3NuGD90bws0OhLyHGNTYFRwQDfsM4MQQ'
    'eopA4Wc2obHEVk5PcjPwKsM2vTvkBDQ7G+tmnVox+W6zVkpz1HsO/ieTZjE2+qurTkaN6+SwJ3qHv0of'
    '81nLEyvh8hoNrjGp5L5+dhg9DeIm86uX3HSIxr/iqT1PK0Z+VkKup+ZGshfFR6RtKQGoiHgv7j7RXegr'
    'Zmogi7NH2hJhGOqvJv8efLS9O7f4hnHkyrWU2+mV5oUM2QEDvbG3AHDw01U+GgQeIJGuU6EIGVOjemCx'
    'JChl/B8UcrhCePzlv2qQKRmbywUpFucOrdcmcVzKs3eum8biTcT8YZ6dZMWRZYju/MyYUOV2hgWRL/xh'
    'xYrr41pQQZMb2CUApjmQ34ax6XB4NlXjlNcET3F+D2kjov4CMPrBTj3T/1Pq7he5sKac5KsnCsEEj+3/'
    'U2m/PwQDAfpYj1/0vNmLZ0uvsutFcJ219MsvZuPcr5ijWNRWzhB5TgMS2iHd7rVpwUSOzx/qV69xbRhm'
    'e4nMwqM9Rb2hD6y9qvBepR8+3TcQrsHKVAMqDM/VJvTX/6gzXe4qqzJxKwRGX+p6Q7Ji5RbTRIITXw3I'
    '/q2fk5DythwaXLCSFqdI5ObAEZcA61Auty+ZxeUZQisK8mr8gRO4aN6tUlhT95pQWV2cgUH6cmHMFUdR'
    'r3f1QCyteMBULQeCRsddDc2tVs+UgftPFkxEuKEXF9KOk0xmc4bVPDbyFqt6ANKWbkmcrt2fyMg3zCbY'
    'nnlb5wJqFrG2lBV5dTkFBL1uTZw/G0l+OdLa3qhxXJ1N+GTwn2z+0ZqaXuAvVzf8lRRKp0ln2eL60cD7'
    'mPFzVmFmVGm1OKN0ddQVUSp+8AGn3q2pPMhPxXCJ2ohuzD3suMNqtRdH22zCcN4xrGCeXlFF5RLHu+6c'
    'jHHxQaOBKyJUrHvvROol2oG9XxQ='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
