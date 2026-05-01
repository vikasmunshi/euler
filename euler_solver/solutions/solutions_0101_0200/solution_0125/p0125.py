#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 125: Palindromic Sums.

Problem Statement:
    The palindromic number 595 is interesting because it can be written as the
    sum of consecutive squares: 6^2 + 7^2 + 8^2 + 9^2 + 10^2 + 11^2 + 12^2.

    There are exactly eleven palindromes below one-thousand that can be written
    as consecutive square sums, and the sum of these palindromes is 4164.
    Note that 1 = 0^2 + 1^2 has not been included as this problem is concerned
    with the squares of positive integers.

    Find the sum of all the numbers less than 10^8 that are both palindromic and
    can be written as the sum of consecutive squares.

URL: https://projecteuler.net/problem=125
"""
from typing import Any

euler_problem: int = 125
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1_000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100_000_000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1_000_000_000}, 'answer': None},
]
encrypted: str = (
    'T2oz3b1+4qJzgszRoixAikHbZCgtSFe0iJMBj+cLxRHVbvYam9cQNp932Ux1eTUxAYi6VqwhY89apPNe'
    'CAocAZCTL1lox60HLAOCF1GNwUvoZ9uWDBXGuqG5LxjbH8c/w0WVg1wrAA3EkESTzMgvAjQnavs/i9Ka'
    '+M0QdiqY067yZ4Mk657FUuHc2urv1yeYMxDxOjORGTCD+nGn/Cwr+hg6pxNeEaGfoxdzqPXt4raghM29'
    'j4GqDSYziz2SYXdLOq4gItS6FE568vSwk1OtVUvYG9gR9dCg2Iv0CeI55CYJFcadIRXbyAMfLvJXEQZs'
    'qgwO3Zm0lMPWyV3wQuejeccCwlcEasGv5z/jEjKtXED8TpuFW6zr7QUMDYixpMlEIsn56Bm91iMfKStT'
    '5BJGepN9QBzXhqvvCBd1Nu9efD6t9E2SUWuf3pbet86Nras4s0UQZsXFGnOz1iQNmdoeSDlDVBLhoDrr'
    'iz/Nwi2jzjhrq7kJRpVx93vyUXE7cY1sB9QiHaTtaP0OLCAfat5E4M+KuH9n00CDqoy85nRzg4dT+HMi'
    'hX7qTQASg/dBBa848oiMxF0T0RqrnIOeFkswEZ1NrrPR1CUHzLrbLwyG8v8hL6gG+fZSY1/kCE9QqYfB'
    'WDu/e57Ii4ta7DvbXHNBM9cOsg6ML/sufvVgr+kgXKdNLhjoR1TfSCcfMVlIV8VIcIuafPsC6JSc2CG1'
    'GeB+kotbzTS21Gjt56R8I6v9Zf0H7G3mBrEbFWrdpi2yplPQZHW9sxTdsbhzt8QNyC1JtXMQHV6eoiR7'
    'dsmeFM/7ub8MNKokjm58YqcNBMMLnHK6pAcL3aztDzDdsyHQf2PNXR80vWNntSKfUWuBw9AnPdp1iVfD'
    'XkdYTed80a/zF143y7aXHbbfct4QSP2LmHQhDHyJ1DrR9Q07BkZj1LA8whQIFQGFH2WVUamx17VOVDCQ'
    'OhBwoUOMQgB8PzUOFmxFCeGUxuOro2XQ1+19/vw2U7OyvOmNjuDqMIXKYDDgrhlW+Mi+oIGIjZeBEIIA'
    '30HjJnON2dhNzv681NpfUhLI07Ljw9bWdezAKk3b2qRUKlVt/T5AIwjvQO/JZEjEMUeUok1UgsOM1vTw'
    'wwjaadeYmEEA8Zg8gIUqaeg4gqb16TOmVK4rTFuCLgRcpTDd6sG1Wo/w94i35kMcS0Njr5OmZxWFC3Ci'
    'V0PJjguTaYn36SDKdeJTAYVPsZA2YOu897P8sNxLZqiQgy8GkFZ6k/aT5M3lHCpbJ60kzRM3lWJjTYD+'
    'icZv5jxKo/jJ7cEFTrNj7ijHbuBNHyhbmPvgHt6a/3cGq+BU/kFuTW4kqTn3h+QVDdtnAqNcs2XxMsgh'
    'M8C+U+a05tD+/Yu6vLh1bfcgRY2dEJM1+dSh/khhJesPQ33EAKGrtfvVl+iV/ZelMJA3BYf5R8ke/f/5'
    'ktPG8pA64q6KwsfQt62VG1pBkG3XC83ZJ2Jvjgrm6QpBiPlbbF0x5B7g++2t37a2u8iaSG/hU2PqMqQz'
    'N0soWXpmckLqd9UjnP1HRpk7jFutlbLw1kpev/Ehu20l38vkyfG4WO7HNloDyTgDD2RG/y2nSiVmbiFg'
    'FZigedabzOquYH1yIJuRH+g7W+iOxkcAio4aau2YKGp2UK3EvQ7AgpVzKOcnp0BoD4FU3IhFfJSVpwha'
    'K3CL8cNdiah4DZCpf/hWvzo6e8COKW3lqLTypophGFjVqUdmWoUgkQVjuGahE9BmuWQZ+FVAIsrD+Loh'
    'TYcN1BdEJ6HiMe8QkMDL0QRghjQVbWiSbJvmDfYnxAVnw85g+c1gRqGB+JFeayet10k9g5NJFQ74be8l'
    'Img4oT3okg+fWXWz83eybIkurHCr/4VrPN3tu2Ymp93VQUH5ar7QWKyhczVxmnVKpAQpz6ZRUbXmjRYO'
    'hJo2X/j64Vq01AdEOfG8051rwqXN543z6seKFJ8ENEzRAuavGVWBVeKhzvAsbrptWeapo4WoZfuxsJ6g'
    'Iu0mDSlFPO4lp5t/KfGejaUC0MONbcgKdVqYcRI256VGrI5OTETOelEwuYp+5BQko/CNK9BvA5LRUFue'
    'qttvsgbsd3nBxtF81cu3Y4WqSgLHmLX93hFPk3/G0tBgnz1WtfXhza5HcSDFSu/H2q3QZHMG/7heNfvv'
    'h142csYZYjGXpNbS3kBvDq6/W2fYKripM2rwQNHdtfG3rgHbhhPCIN+oQ2kEnXntFPeZvkJq/8gXZNpt'
    'UMWwocxpq4xlP1tpaQV5U7ob7P6p5kYw3zWmjyEw3KAIPUXaf2jAZdMa7Wqs7MnFrYnhtxH6t/la0sd3'
    'iLgD3h6wkezUfN7tYSCmuGM9mxsLbK286LCHHPqK8fv7Li99iBu2SULVEwT43jVqWAGKk/za1T7zy/Zo'
    'nCM7IOshA802jYbt0j2srdcibkZPjo689fFTOLBa9NX0HJo483MqsKFe/CE5vH22rzdY9yNkdncXjvp+'
    'Cf+FzLyacZ08PH1fqKk6KxKGUSQjcUtEOcudm9685wOr8epl6yTl8u61Q/OBsVpezggxhjq7eFdKkWBH'
    'QKFdZT4ZdINjNW6SOtMTfNg4R0qnJLtRp9J4TPEf3nhEmPtlGUtsdiVph3cc4Q8aRxPX7Sd1mCgHlKot'
    'nMVvtOFI9oFCico9C4XzeNaXZfUFjHuZPG66AvHwfQznWf1BwTlVoE3FoZk9Q99a31mnT+HxzQ+1H/g0'
    'IIqNaCbz166KTBscUpJB2KWD5MRsqteNcqKNeutXrQNfuPX/O90pROO/2rhM89Az0cstnI4H5+dH6tCF'
    'gLTPHsVBqeRdNf0fkLeClgeDaPbuWH/o0Mf1kSD7M1wTrQVaPZPVGiO1vw22yKaeXLzCkPM44uSlN4aA'
    '30vEh1+lN+Cs70hhxyAd/oQRuHtHpDCSe2/plyz9wNQcyLgvhuutNMuDGdH4b3Mp4chlWHNxXes03sOw'
    '0zzywWh7m5HTVMhqOAj4AAugXXQiTKokcyXMSlSzGo7UDG0f+Om/WpcNr2bvxOhH/9r/K+7nasJ3P7E5'
    'v5ZBucbSR1PKhFEqO1tmwA2ErhaToxwBOHGdZ3QHZ4uEjQ9h81NmIROv0ft4qTI2q/VCMWOFXsJzncnF'
    '1sPfUrMZiAe2eu/Y6ciiyb6UVNyvOUqsMyBJ/EhA62iFzlabJd8WbCY5w9XarsRculS5h4cPBZMLky0j'
    'Rc55AREx2QiX4R8dUzXzMg+rmfBPLnrB+zofJEBt88JOXwH5M4IJTNKnqMIHndx9YMleZww9OkXGGnXW'
    'BeVcP8gm6DddTX7BadlWiOGXHuxHddYwTn7vUQdNpYK8OQhgSjWW0FXzEdStpPyZk+YJdboKl1g3tstw'
    'xgatDYJM7cdML4WsRlmT6Wm/mYnXFxmfvfyhr8VPsvUOJ4M8Ps0O1jn8GWuB7AZoCD7aQGhkbWdsvNcX'
    'LyFly0i6g6dU0dXqb2E1H0gmw9Tri+JiNOKBICUTnUqU1bMOiFpXSYmPLPpD4l2h3pFHsUGX8EXPlG59'
    'hca9bZxmYAKBdc4S7F4MYn68YLg/jm48QmNhb2xNmP+XQ+E8Xe2zt1felQYpC7ip7TsdqRac16F4XSo0'
    'mye2KA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
