#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 764: Asymmetric Diophantine Equation.

Problem Statement:
    Consider the following Diophantine equation:
    16x^2 + y^4 = z^2
    where x, y and z are positive integers.

    Let S(N) = sum(x + y + z) where the sum is over all solutions (x, y, z)
    such that 1 <= x, y, z <= N and gcd(x, y, z) = 1.

    For N = 100, there are only two such solutions: (3, 4, 20) and (10, 3, 41).
    So S(10^2) = 81.

    You are also given that S(10^4) = 112851 (with 26 solutions), and
    S(10^7) ≡ 248876211 (mod 10^9).

    Find S(10^16). Give your answer modulo 10^9.

URL: https://projecteuler.net/problem=764
"""
from typing import Any

euler_problem: int = 764
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 10000000}, 'answer': None},
]
encrypted: str = (
    'nVbWfCMtkB/zXOd5HdbZ+/oDJ7eH0ocWPCma/+nMQO1oNmyj+HZjnoQS+XWTEXmcW+Ni4saVjQb8dqJG'
    'pSFuXLgu2LQ0IcgOwqZ2nKQmDjyXBdiGu4x/cdYQ0ROa+dWfmJ9f2MlM4BBNKcjGVtsS8tr6HhZxs68w'
    '8ivNaDLXhGvni2DeLeX6UFYEN2uQSxUBR2RgzhyC5kWUAf92YKyUFX/j5MfiNgU4ShGuLm2FZw9F7Oxw'
    'MvDCp+QGghX5TNOwsKPJFA8eRXqGefUW71hq2ezcFo9FIowSANMuxOX7ITqH3iSynBQLOtx9H8suQk2V'
    'nSPyB7DKK9SwEI22gX9sIATnuvjbin95OKJ5L0BYDRiz3bAauOVO1+huiFq1Miig+q92QR9hIf6o5kVD'
    '1cerQjMoWB02gCEYuPFzfW+t+rTuQ1kDUCN0tyFEaqQOT5iOKKaRD4RVjfeafyk/e69P1rWzmY2FwnIg'
    'yuF+7OFDSFxJw2s4hRE/tNZ5grg3YB3yFUgiyL+VpFeK71qvUMpNUjj4kD9YpmT5b1BF6RjvcvMNOvU/'
    'FFpji3TLPBK1AX2xKTi+i9c1asr0B4TrgcX7cCPWjRIG9cfUWMfKtwe3WwZoXDYYepTf6Uup9qTYPv1p'
    'Th5yivUbty6g+jQrwHVtkQSZBgWZXqXff+wbxTn/uREEwjDhB5K8JNb40NtqT5greFTbzWlpFwRLGtqV'
    'SEBifR5ykogRSoTUo2nJdKzuI4nGpiSmbeAf0oFBGXPsxbuzZLdSLvWXsOCFW1Pz4szsb25EDbVGZCft'
    'QaJjaqgJDDZOAPSvLBwPZhliQzJ5/CCa2jnf4o+3RCH8HZ6XllLgNDXY0ZUkkfl23Ckv57uZ87ht45gx'
    'tP62IDYuwv1CS6c+1Q3cYMocsJmZesMBjzx+z74fI5Vko7r20A4Esu2qBIfgUrQ+DgAfN5UFtWLKylgr'
    '5SIgG1t5RMmHGns2p7eZsmzTRsCEMUT/A451hxmpLfuIuUOToLx6wmwNLmYQRJ/N2rcGK92kC5a7/QfW'
    'egVE1BUYO0MUFr5JrRd7wgUnhlt0AFq2r4DTLu1jqDd9j9Sd1drAw5XdolFJpfc5yItzcjw+OqJB3AP/'
    'GjC/CSAc5iR9WTXc6MAFYpePdTgbSSOvaYrejuV8AOKkoRIr6N83v9uDcmwCEUAS4he2VARkannd/IcJ'
    '7brKZ66Rs6WUUawOvNCXreUydBp/BgBBkkEMMQ0gAzH0mu2rxRag1oriBQG7utV11JVQLmo+0NjOhghX'
    'z8P9hQGBf6pGa20Ll/HwpK9LL54b53ocy/yU9XMmjPfggfK9xLngaqMst67ld1djZXZqpoZXvcqv1/Gq'
    'ScCpcIL/2PgS0BCxZ6k5SFsRIPhLvSE0rO0cC6J9Z26ew4BlHIH1LBvNvbGOlCISzOWhVX6zhyDU9lW7'
    'Wm5J9Go56yO7A3puuBM9uJGYBMBOt/yuru0lG2ecVhh0k0YNZtIAlAA/6LmuiqmliX4J7G4hnSusOo+C'
    'lOUFlvtHc43rMBamGuKr1Ho2qR2UAY5bqZyV0i4MuqyFO1vHZgSJZcNsFvFlDfIZ63Trli5xKvHVO1bs'
    'psrQcBGFdoovQidzqMMmoWSmB3LomENn3cq28RoAxE/X8Y/9ZRWF1c8qofmTa6RhtLLKqOL7XmP++noT'
    '7CTL6g7RVd0U9dPKuV7hbdEBJsNcNSuEG28Vhbzs7lagWxwPAFMPXwt9haXnP/yoNX0zNM4QHvNOGQEO'
    'NOwYbk1Onfq1FvMk1UdgVWJQTcZNZbtLEj36EFkOF6fRfCLV+g1BAc0Skmv7G7RFJOauA4YUdaTnRDex'
    'GXwCOJnuIvjSm1YZ079pZP+r9g4LncHfGd/+5cisSMF9cWwYe18YW8VbOoKCfNNG/rhivw4pbYLQh2r3'
    'Hgo15ORkMof6Dh4UBpFN/XFhVdjDkcC5WmyFT1ObY3fe1OJ3SCu7swtP/y+VEY1en9YaeUban+DtzH2G'
    'hfXWRm55/V/lY20lX5VjYLcN+zjqaC+gUFcSYvkfeqjil/cfbrXBpM7b4X5AOD2VwU0m022apMJuoazr'
    'F+ad7b9O9mwNUkW+CLtV9PESJb0pZBamZgIFtVW+NvOQvTeb+dhi5b2g1l2bsJTTLJx/H/Z9AGpqXlZV'
    'degZDo6F+gYIAs/jL//K5oxZKZoCGGR8ywT3qgFuJy3RFxaKqSLjc+W+HgYAWfgCfCzKCSS56dHIYz0B'
    '1BbVUPQXJTmUzDyq8NFX/qevuCQ6T1nVssHM+7grAlgYx6wHwSOwZnWQ6NK/WVYNc+unFXRBBPT7DCB/'
    'UsRy+LWMBzfUkqXkpRyoMPSs1ymSZQKYXBiNiTQj5g+GdL9VN/Yq9K664PgJ73hNp4yOlOap1uxT+VkM'
    'ugvyiEp1wsEBrkemHj6RvkMpdxJ4txeYfy4TMh6F8nqUhxnu5GAOFGUyvigpCyOxm8pGRjcjjvyHKgTy'
    'U2OJ5chX4uFsPWFugCKV+XeNTSmncQLzwvq5R1CHkCpy4bTzIndRd5sujsyvCl3FXO6SH32B8QQIM/IB'
    'fMzLctyuWbzs2NsUtRPAZLBAI6lK9/CxxIFxSb/qKztiRs6na3vK008lrS+26QMe/fxIAa4Gbahr8rJb'
    'jq4D+A=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
