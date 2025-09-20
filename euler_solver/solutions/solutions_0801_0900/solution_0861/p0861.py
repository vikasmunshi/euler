#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 861: Products of Bi-Unitary Divisors.

Problem Statement:
    A unitary divisor of a positive integer n is a divisor d of n such that
    gcd(d, n/d) = 1.

    A bi-unitary divisor of n is a divisor d for which 1 is the only unitary
    divisor of d that is also a unitary divisor of n/d.

    For example, 2 is a bi-unitary divisor of 8, because the unitary divisors
    of 2 are {1, 2}, and the unitary divisors of 8/2 are {1, 4}, with 1 being
    the only unitary divisor in common.

    The bi-unitary divisors of 240 are {1,2,3,5,6,8,10,15,16,24,30,40,48,80,120,240}.

    Let P(n) be the product of all bi-unitary divisors of n. Define Q_k(N) as
    the number of positive integers 1 < n <= N such that P(n) = n^k. For
    example, Q_2(10^2)=51 and Q_6(10^6)=6189.

    Find the sum from k=2 to 10 of Q_k(10^12).

URL: https://projecteuler.net/problem=861
"""
from typing import Any

euler_problem: int = 861
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    'C1LvvTauErC+N7pWEanMRO8+cFHDYsQ64CBANsbFdQpQccZyJf67zqTCk9qjuymmD5S05O+jYyOpKbiJ'
    '7iG2p8ussDhNauf0VR+cjpUc72rWOtiVLyswO6T1hXfqD0WXRTFyKfBOgAMTb2JdzAqf3W+jnvNy9ty2'
    '39bNYUVNJCi6bGQlnM/+WnZX1UJu76652PbN9iUNo/Sfgen0K0StbZjVQAyElNCq4T3YNOR/K6Ghno67'
    'iExZfrRENZMkVpHZ0Ls/Wccr/Y/qfMswZOE5bN6qkvTs0GZogNq07XkNkhIYcoXBZQ3FXcK91OJuwtnx'
    'JSu8O2vwrgi3766MwXilO4nwZjW5lUK9Aq0UaQzGFdKCh4eGu0o5FXPlbY2BTJtzkGg1QDcKq0O0GZ1c'
    '3WT5nkbNg5w7t5vKuEYYGEIi2pHoDnh8yEcbbzvD0AaQDoziHvPsnu4CBf/QNCy/ZQWO6/b02g+o4Fqf'
    'QkhwQpLUNEtg3MS3u6oIFSa6KKUVVe9Xc869brBqBy89nABftmP27OPu6CRVLuUJfd+38LnTvN++0g/m'
    'qeZ++HoceyzNmRWMMlOFzAA97WmMxt7gdJze3DP/FQsF2sOp0ZmkX3QO2StYeZjhG9tV2rHDl5rovvjC'
    'hoqx+PTBhfQlcw8RaUEGrCv47pVsDb70S5MCzrANQeH+4GnjcDeIhaUuriSBKaeXKxF/AOQN+cZZkdeo'
    '85Dcux/jd8HnpxaugWLKl0YSTp2k5N6IrlaujzTVSIHUdYpAtda/CfyDYd88fvsQKOtMsdTPxkYYyuP5'
    'IGxDdK4Tl3uAwpQ2dO9MHCw+zs7JsRKIwEfmEIbk2gAmR6jK3seR7p598uDlkjr7CpiN1Khn4cjow63G'
    'JJ3fLx7qOIFq/c1g3RzeJ/briGrwbnntDxCIWynR60m2gFqWDNmtVsRr4to/crH3Zm2S6QYHcgMcx9xx'
    'LCUDj/C+yvDqPqancIz8HO+FuMWwp2sxOsZzOB5unoCV+E9mqwgJ3xx3N7uUKWXpfwPCjC9YRCv6B4uY'
    'AVB9FHkQm9+170MZqfuxGlrYJowa2IHwbAvSFFI1McKVecsx8solHeGE0cGqOMgQXEfUR86knAJGwxAX'
    'iocWfraOkb5FJj6qSbAJoqfMR8Tg/rnouZWdplQ3itsG/kIP1lY9unO1Ms322MiTAxNi7KChMqIz+et7'
    'BjcpNENmpab3g1XCAoN6/ATWbWdNWVXSMY4xpAvj+SMFYFxUndtVaxswUF3urHiSeLIa/DpfcIHzzJND'
    'NbbFUmHfLnDxb2Iq+7ZfVxqdlHa7YRnFRRxRtZNX6PHcJvA5kPn5lsUpzhNPF6gYaStwsAgm/qSu/qdN'
    '/O3fvL9+kFuScyDqL1BOXzbh+uXJzXvzuTIcHdtY3n/mTFydtvczW8dijILtEChUamhr/PucuhrgP21A'
    'eVv5+ML11GuOeD3bXUvUcWTQEQh0aSUiNoVmrf0JF/6IRpnWBkQ68Ao4Bixi9fMVL5mwbLHw1Jdnqp25'
    'p53bUK/jLb5VdrSYFWgJbrL0JqsXInxjKTAQ7dWMU4q0KKYbeiDHpyq1I+bDQA3FzHS234yzpo8sUqsj'
    'J0oKfU/mjh3fHDc2dxu5KdfXy0y60PH22258gqdp+fJDUWAHP3kQUI1d156QsiSXvGLK/QtuUxHoZ5DN'
    'NrMVAa4jeiCRADo52UgbpKW5xny+jOgU/eBBizsdSVV4q6fkY0rZGMP+CK+uB0nulkLicgiUu8SLL7FY'
    'L0BiAyayn5gzrFZbinH2OtAu35jQf2wyHSDAF5rYu1McXAvMs0m2wWmPRo0XL+D67KO3df/fqoYfEJoz'
    'OFSJADZKOAA0droIhAuAWJqz40ZxyDvs9zWhczALYA3PWEPrzNW0fAwPgP2DXPR00TvNjKt7/ar6BlDY'
    'XQoUG9xKMEKlWrXnxKDdEl5VGb5xQXfH9t6Ett+iJR9fZagu6BUkzKBqFXZosiu+eHsZQpp+JZVJ5sqM'
    's0LPANKOuD+1fszDPq+8F/9V3BvlsNg8hFnXypGTNi6zQYjf+cptldYKGvUSqVe3iurDPrTCQ0HLq3Is'
    'YT7t1N/qIy9KTo4v0E6Rz5crkzE7KhX/58CShCDcT4Jquc++1e6cZeWIsZGC4X5qCoF9xXd34rx76hOI'
    'PgNBmEb86snSRgSSbFg/7RPLCQPZ+PYShfze1FAzk9EgAq9ChHsLXHhJPxsuSZQaVpeUOEULMjLVV9zT'
    'SjEVDPRX532etZOpzhNUFuwgdhD4t3pnD2FskW9huiKr6VInH2bn0eFtyuD3JUaU8VtjK2ZEnGMUIp5l'
    'aLHjcvG0JN1iOLDqV+i+2NxcG/4v8SVXFMO7kp8offBDuNfR70zCnFKsIoSe45LBfCgZ6asJLG7GHOoW'
    '86MXgToXxrEQ5ujKoxU+cW2ImZnjMSLFc/re+6+Q32NSU8eaUE4/WYPs7gjrGk3tSni6UEKNN0cYsDgZ'
    'YfFEMCUcVm7+1JhZIhn+66xyg3IqTkzWDnuSoMOra1iIpSzkOj7Co6RF2J9b/S21mmh6/akVMjzj7tCS'
    'Jhusan5rxp2CV0YbRX4xQpj2p2gMGqtvd2zp6rDNvNu9ChjHiADtJ5QY4s3Nr5xDNP7h8GZM/X4j/M/S'
    '/trd4AprDeVgf8cOQdEgw1q1iyxh+DGX7mNlK/ei5chaiurylq4slwL30UALB+uSCqWsCX+VJMivlQH4'
    'yBllPtqE2yZ926hQVJRPm53oDKlt5ecDq2D19Gs2r2VYHuYn0SNsSf59snsWhwhy+rAgWiWorhNj4pUF'
    'lrwoCHhhOP2XwNQW9li3++iQB1K4oMZd8FAwSA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
