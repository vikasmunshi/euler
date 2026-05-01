#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 478: Mixtures.

Problem Statement:
    Let us consider mixtures of three substances: A, B and C. A mixture can be
    described by a ratio of the amounts of A, B, and C in it, i.e., (a : b : c).
    For example, a mixture described by the ratio (2 : 3 : 5) contains 20% A, 30% B
    and 50% C.

    For the purposes of this problem, we cannot separate the individual components
    from a mixture. However, we can combine different amounts of different mixtures
    to form mixtures with new ratios.

    For example, say we have three mixtures with ratios (3 : 0 : 2), (3 : 6 : 11)
    and (3 : 3 : 4). By mixing 10 units of the first, 20 units of the second and 30
    units of the third, we get a new mixture with ratio (6 : 5 : 9), since:
    (10 * 3/5 + 20 * 3/20 + 30 * 3/10 : 10 * 0/5 + 20 * 6/20 + 30 * 3/10 : 10 * 2/5
    + 20 * 11/20 + 30 * 4/10) = (18 : 15 : 27) = (6 : 5 : 9)

    However, with the same three mixtures, it is impossible to form the ratio (3 : 2 : 1),
    since the amount of B is always less than the amount of C.

    Let n be a positive integer. Suppose that for every triple of integers (a, b, c) with
    0 <= a, b, c <= n and gcd(a, b, c) = 1, we have a mixture with ratio (a : b : c). Let
    M(n) be the set of all such mixtures.

    For example, M(2) contains the 19 mixtures with the following ratios:
    {(0:0:1), (0:1:0), (0:1:1), (0:1:2), (0:2:1),
     (1:0:0), (1:0:1), (1:0:2), (1:1:0), (1:1:1),
     (1:1:2), (1:2:0), (1:2:1), (1:2:2), (2:0:1),
     (2:1:0), (2:1:1), (2:1:2), (2:2:1)}.

    Let E(n) be the number of subsets of M(n) which can produce the mixture with ratio
    (1 : 1 : 1), i.e., the mixture with equal parts A, B and C.
    We have E(1) = 103, E(2) = 520447, E(10) mod 11^8 = 82608406 and E(500) mod 11^8 = 13801403.

    Find E(10,000,000) mod 11^8.

URL: https://projecteuler.net/problem=478
"""
from typing import Any

euler_problem: int = 478
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    'h1+MiJ9J0dM/6iqzxwOhmUsELtGoImzWi5f03MRH3V/IanKPITEYh8OScXpX4dm6R5nVOoY07CnqJK3A'
    'es6KfozJHRpVwNpYsRmzY3u0YRWL49p6xXGREuY5W8SLs1B4/80zPniJ1sC/84wXTgjZzIQObhRkLHEH'
    'IszsOqCfhoCc+drcXVKppDEsXWnmqR/7YjegHCli2jpXy9uHCBgsiGD6ue5qHUrZXmW+zfl5dLXu5KmG'
    'epBDYLyDTddQFsCqI4eq7QGBsIp8xzrTAYe/61PMqgVeb9BIeDOTSX3ZL8tHN6jd+WuCJUVDzzDZ1le8'
    'TdXYsIjZHfWLhj7bYHV3fFkog1YkHGVPq1pj82EQLzPkkYkor3wERD7+if/AvvThFjLGzWreyBDCIz4q'
    'uC1UxSPj3PlnF9jZ1hN/aD21Wly+0Vshp7rWHp0BdNOJRlB7o98mCL9FoUBvfMY89pne+oS6ejPBnqpC'
    'vPFiDJsRGSgphv3cK/w2uXZeqXdhMI3XnJuHzI95WfnWmSfDck80gsjOxVtV5Dkqv/sioM/3+VXvd8ps'
    'vAj3AtgrVqGiRbudLm9h0rMjHWwjIvsDQf8mZCPsYr7+KMixy+a0V28ecHbU2zm8Hphdy1vvIQBWi7/w'
    '4hjML5LeWvPGS6u2buw7qX/ynkNUy66FDl8hgcX4MVwoR5Bvdg//NPTmDOFC0vc3il9vTy2mB3c/Jyyb'
    'DuAWDl2LkKPtHBbQVy3WbGByQdQJZy3B3lCbRt+8k8oaz7KGOEtTaHAumjNQDQBhlyRdsLWtiE/Rk9dA'
    'H56M+l91Ajjs0F7QfYN3a9SmmJ8w1x2wfuMalGhf2jztCQ0KCHXVToNUrdP0kHej5uQovmTGQ7SmNCSi'
    '/Tg+UxRgUaYvePdJ6ayVCIHn5+IDtYkIGu803/4ezOzluEcRMBCkORI3z9a/Xyh+5rdsDjEPfsfbEija'
    'IpDdR4wQ9aTzoUYkyG/RR6Dn9ZxxuJ2qTtydQy6Q8nmY3eKMMdhN0xNtagtjxP0J368UBAXCDAzN54DK'
    'C3730gYk3M1vIiRXoQnIzlDe/Frt1yOHrcoIVJZgMJyha6Mf2nzjoxNXdyCUJWpZT2rotj/kbVw+cetV'
    'skt09MO8AyUEkbHICWLFwgEZJJCVVuf+6qcFZBE2xwUmpuw54jxJ38Mcgo1Y7Fk6kGRJPYenoTGzlzMf'
    'E167c/xXKXG2/ylUsK9pGWlSQM6AT+IxCbRtjOVWJa2FArefrMprrcV7j1JbLS78XuGd96LVEyhAi9kG'
    'wZFw+Lnu2nu7whZn7vJh73Hy5cDo5NsuRlqVgo6h4RUEPqplTrRf+ZgPZLVnd5GpyzfQqOHRwqp+xzKD'
    'lKyd9Tgvp11F9/dkpyVPtBy9B+ZK6WPQiifnj1DQYrsLt9Sj5XFhROePiuhaw29n/Rn/XCRtBg8f+J+X'
    'XRrT3ecgI5hNdHH95ub60XB7KVf0W2+eYb6AlKI33Fqe+RmB2dqjG8H8uneePAm8rKsfF4vcC9hnRDIe'
    'zdp++QA/CWR9Sis8N+YsjB0vEv4YIWbUXJoCSgf9+g2BfzCaegUsZ8vgxEHHPXwPs+xNxdv0zUB2/LwC'
    'duZmq5+S46y0ypbOmn20SIcsk3yxDfKWyY/yu+00Ehkz0CSP6CEb/gkDojRSOEuf/89hDEvm6RJu1Ni9'
    'qBgqf+w73gj3NaQ3K0B3TJpqGY/D/8sMGv4iTKtWQFUtBWdG0B8AtVG7EILpHLmgm1OinkxosoDe8ECJ'
    'fnhkRyrMhoYgp8yu3ikM1p5Dvi60Ya0pmkxSRteV4ePt1S5G8RYF6zPe6F9/L81we/7J17Wo0IooYBjI'
    'OXcHtiq4NG3l3a+NBnONLePXSWQhOAuq9YUavCVzLNqKbNMZet++D/OCx1DxHoOIf0aLso6fj61Z6H06'
    'un3sJXGtV2oSYxdcoRL9fY1yD6lxrK5YMygBoTqOTr3BmJy20SIZSC2xpxYJka28oGBsSJtJ+ACzHgpw'
    'TPBB70dy9/IxFqqk0PLvxcbWcHDVyQXgB3OH7pz11hqBmS5V/A5PSDllJs1JnA1lbbJB0owQY1/FZVUi'
    'Du0DPtEt7As9u66iS8yW2xn3zipdE18txa0g4mxZ7wzY6Xz5YgpQ/iU4BSiyNrxO/6CLSLosbULT1zsW'
    'Ow/kaorBKnk9lhzFDjbfH51NbMojnbU8X+eWeCBApy/04Z/2fz7gPpqXnHpJ8omLqLk62D8+A4TbayZi'
    'dDReVz8/dLL74jsxtEEHggzIt+zy/ELfaCjXTjdR6r7eqnD6A6qO/povm9/A2G5B1/NqtZFq1oJ2LdS+'
    'tq7vpyDqBvWNTUU3WWp13HUqi960PkrGsTgKqCeIQafZGgEW38ADgWEMsCHc/LhlaimpSmwTm2WZoEWN'
    'a6YsZksOEB7U8gKterIFVeQh0XUcG5jjXCYzDXvU0aSyld9UkN9PDMaPEAk6LUKVcpHW8c+ee7sZT89H'
    'lTETH8qO39btfaL9UHHaIA5Qky+Y/g+haAoIRaBDXJEHk8brk/BH2gq2SjLzEn/B6H+IQNp9fw0mz9o7'
    'jMaNmk/DMQGieFviS+qKxJV70z/XDCpuXAxFTOfyzCoJSx9F2YxB/f+wQvDmlB7TY7ZjoE9DQHQRZk5a'
    'CPJeiFMxa4kYaoDW8U99UjNFtUknFOol6ZDr1JmHGdcNFfIUvgzO7/nPcrHBT0uHGBjJ77xPys6SSVwU'
    'Ejv8H2ef9vOm9QwVbbtZghxg8zb1NUxB0rsSri3y+hDTWNMDe6z6heQtCnrHg7BtIitErzZin2HWo4Kw'
    'hlsWVd7a6InsxD4vIupEQJXcVxSud8l570fp19J+nuLe7xM6NTIS5GVR99JNlxmoVXDYdwpwPOoZXmK1'
    'M86AWN5OQsJ6rn+ZtfYS4IVs4TrQW/SCv9jERtVYVw48RRIfzAocklabs7ow3OTgHnoYzloquA/XEAaJ'
    'KTcw4eV5+opPxOQ1v99jnMRjmT+cxxVHGNC2yIA39KGK1Vwm6X6GsVVr3xdjGaGsZuA5sR01+cCkbhQh'
    'i9PB5dTH/SwjooW2F6vx6Q7OP5aPrYlaNnY0FyWLurFnTKYzM5Uo/x/IbEDoZ6KEEKTrY8FR59WFqZPh'
    'Va0ZwrKWyq2LLjPjd/sUQu82Dlj8ukRG5cCrctynG5VLPvUIYhNgIETRTIVHx71g55N2mFvm0dp8ATg9'
    '4BC0QgYQV/5nR/4//1lMLA3D2puUftZRl8UzUMkc+Wht7p5S2qb7+a6DR1SEDaz2cC09gV63XUCKN3Fq'
    '/qjeM+zogQbRsXc4yplLgDqGhjLBU/nG8yaTHtGKnwqc4IhRRB8BeOqooJ43ojzScv+pCx2G/ZNXc7Mh'
    'qkeMQ7D6A6UAh94SiAhcePFnaphfcL0ArsAQI4Fm0Vye0F7UapUwW9dzJUouI8FNPLxQoqUHlIfJJsjg'
    '2XAX2a9GwVAHP+VQiXz2aXESHRmO5fjPIQ9LeGzBhEdugsrIq0GzBJmoKSTmWnkH3H29YHOdiAZOGHel'
    'Es+b8LNF+POa2EtBfHUZTagingP8UrDj59PrVYFmcJO7QsvBUPbyHCStVrm7ie/HDyGFbh8hWEbp8hIq'
    'rNDin7FbRdSGhV5qr0yp/q597k3xl2/pr65/LD/frhMyVUMcLDBoSaLkbNTd4jiJvaYtW/qVscT6fwgW'
    '2umh71b1dNrMZK5XZGwxegswReABV8avg+3vQo+QdOAGcAzevXRmqdTwbX+VTKzc545DK7sdRBVzPgjJ'
    'Tqti9mBtQPOauWf5SQo7lVYNLrLt3eEsf3F8xATpL2qL1nh2fD/KOipP9dOfBpO6/P2AaLJdWEfJ0pHO'
    'di3Ci2GyzeD+n3vF3aCD8n+c2cC47neR0VXr8QgPVKOSwi7KNAzSFBoxqGRqCDzKSE++ZqcosIinO8Dj'
    'BWLaxnxJfQqpcZ6wVmzY8E4DlieKeBRk2eaZHalcq+lgr3xAjbtJt9x4H+drHeKFUBhL6pKYehzpeamn'
    'kpSr8jL5jZdUqKX50w4Y94A/Yo3N5KbdnT2z+USAmJHCpD+7klmP13t8B/VnPOkuqCpZbb3W+/DBk6Ij'
    'qSfPNh0xW4tdm2tC6KVuDcGCgAsqPrrv96QgOggHK9zdX0AcbaexudUdF3x3LAA9zXQSyatnuvOaDdLJ'
    'tXBI0AcUidU0XvFJxN1WyzfKKqJkzcPuXQBT5W79J7D+OutVKCvfeReUHdVXFw/M'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
