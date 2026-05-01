#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 633: Square Prime Factors II.

Problem Statement:
    For an integer n, we define the square prime factors of n to be the primes
    whose square divides n. For example, the square prime factors of 1500 =
    2^2 × 3 × 5^3 are 2 and 5.

    Let C_k(N) be the number of integers between 1 and N inclusive with exactly
    k square prime factors. It can be shown that with growing N the ratio
    C_k(N)/N gets arbitrarily close to a constant c_k^∞, as suggested by the table:

        k        0         1          2          3          4
    C_k(10)     7         3          0          0          0
    C_k(10^2)   61        36         3          0          0
    C_k(10^3)   608       343        48         1          0
    C_k(10^4)   6083      3363       533        21         0
    C_k(10^5)   60794     33562      5345       297        2
    C_k(10^6)   607926    335438     53358      3218       60
    C_k(10^7)   6079291   3353956    533140     32777      834
    C_k(10^8)   60792694  33539196   5329747    329028     9257
    C_k(10^9)   607927124 335389706  53294365   3291791    95821

    c_k^∞      6/π^2      3.3539e-1  5.3293e-2  3.2921e-3  9.7046e-5

    Find c_7^∞. Give the result in scientific notation rounded to 5 significant
    digits, using 'e' to separate mantissa and exponent. For example,
    0.000123456789 would be formatted as 1.2346e-4.

URL: https://projecteuler.net/problem=633
"""
from typing import Any

euler_problem: int = 633
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '3gRAzw5fCMBMQZBKkgHE8OQorC3fQW9nQgFZaVjtBrApAebSzUkaJ5fnybbum0FQ3O+ZwozPpG5TR0Xe'
    'Kd7sgk+qiu2HJsP9sXxtwKehVAvK/SlhIDer1ONZih4eqC9TgHUvSbs3zS0Zm7Xz5M6TkhKGzyVsJiqE'
    'OnVPxigq9XUjbQlZAJ4t4Pmkl9ll8rdZwujFa6z65S+rnBookf2VFQnetiL1lGdOJqI8m5NYDctr2bf2'
    'XVJdZfUMqpfrrUSZtdDeW5DqH2csEOZ4Rkh0iUO/NZg3F17woQYPuV3M2OfAndBphUdRL7hhp/emoXP1'
    'AKfZ0VAjfjw4r6mWwltYdzPg56JnUF6fzPqgtPKdoYLkE4ua9Lfk1Vlpn0+h4R3U0UgNuYrGKcT7XD9u'
    'epUfSuymbRzZ/EYOktQ331EMBIei85HyShVoj1t3DSL3yI1Rbg1EhmBJFhgJa86UnYF8GHXvMb4lRYx3'
    'irdCpKJotdf/YSrq+PzsLBoVTXbnt0y0Nu0IgH4BiBXj0xa4oErGV6D6M4RttMt6+DCsCaNgSEO8Ve0z'
    '5+rfPi/l2a9VGMmhipzNnx9FAcRhjSJ9l7UYN1dIyX4w2mRwUuEK8uS14Rtpmp9mh6WW+K8uSl92qU7F'
    'MUlFvYzZRY6OowW1qss/0fRtyCzmM5lIbW4SzTUx1ukawJnmUkjBH4EIk/5gupxJXLuypHrwST+HzzuJ'
    '+EfnklTlN8VI4iwKdB1HAwXLHNnXd5D/QkGNrxEs4UiKDa9Ht+vT4Cn7tVby0hwewAFh0MbnLfsL5cbp'
    'B3ZjBqf34c6q94yW8Pa1RYi7gwq/Iqiu+HRP9iEagVDwY/gkmtuYT1ZcM+3UuelpmfoqZo3dCMXfR5QQ'
    'WFKcPko6FNbmKZXdtYS3nlHbYFrjUJXqcR2wT8X+RyooNMKgVNfiKnFoeRUGjryjNLtxho4BJjee5jnF'
    'YycbnWh6IDGNk27i1G7pqjBzHN8MrR+xZPREljUDpagjm/cGq37cwXCTcaZ/vJfSpWWwyyYcnw+u5X0/'
    'W2NdSk7GUKP4P+P+4oI7oeJEAdw2M+DSltdf47HYnWxiUnpSseLdXmFk8bYBiGKycgf0qSjXC+NovpKC'
    'Sevf3aBRI8X9SdxmpcXebrzlYWD5AgNUXaOlmn1M4kkHO3TO573nuRVtboztKXeLZQz9Qr8NXso7ACCK'
    'wrtZmuN+1867TupFO1ZbDTBg3bW4/oZGQmt8Naj13VJp2pNp9I+zrtJ6AL/OT53tgkdADxNug/rOW2Fv'
    'ipG00HAhI8Xf4XeeaKOvrqYVNqcnJpHEMIyMwrbNf66K8vXH0O8ayhij5Ed7EsrpvsgvMXvKdL/1kTnx'
    'F81m7Vr0AsvdZDGTWTbmkQ4/rBcqejfDl0mWyk3T4D/+7VvzEMs3IOcuTe2u8pfX0BJWSdi89qABbfoW'
    'yNZN14OhOzyfzhPX8YnEFUV1bIzQnNEWjYEMUAQ4HqFL4D6+JFgglO/lkqs/4Qa19ROf0Ck5mpFk4JoB'
    'KyMMBx2z6P+dJr6DlHjPZ3AQcK8YqGnV8jNwk34J0o3IQ2Z+cKek9jnEgiyFziblDsgGX7C6uwvlCnbA'
    'GmStqRdEe0Y36NUQo/1k8IrvTIXdrxiDk8DlPhKfDNweTLIpPPuNLdddXvcBsAm1v5Lgc3uNG2vh4Fbp'
    'vHJsa3QTRY8w+hDJq9h7JyS2hUOd+YfTi+dFV41V+5mvL/GSuGwUqP7a+u/lQB7uu+8PYh/nfSqNurtp'
    '3/P+i0eekb/15eyrWL3S7kX8AHCSAwuxxgjoSmGh2YQ18Xne8ooXZYzDgS0ZS0vuPsp7GNbhUIZJbbPH'
    'YlPNdjf3uLpF80rHIdSyU00bewhbGAYx4zfbpqSQM1EVNHRgEeZKl+VeFV1kzGhSK3NgNZ7D5FdyCVN2'
    'mxVOZdH2W4AFE1xexjQ2RjJMzvLGP1bxpwsjAY2CUgWMR1Rp6aUK4I6cBuqPfPO2JjF1j3l+gy3GJS9X'
    'KiiAnS67wLXlsvXlshrzsOe7275rBm+1mFbrtAIuTIJ6L23o3oHYD/cGOYpfA8Emwk3vPebCHBGfqT9S'
    'hZ74/sSjOhpJM5vg6kmA4PhpW346V+fqdRhD9z7V17kQrTIeAtVTc8gQI7tns84CP1wf7UHNGKqfWIzQ'
    'L02xw0qiKRqNK/rsJb+fNkGzyIzH7Xl5h36I/VkFJwh9/de2EYfIdx6JAlE33bXAVe4u1o+euD4MnqzQ'
    '4OEPqg7w1RsBCyjpjUMJRLkQvdqngmnZPoceWtrVhxMn9Ew0+0ytacpfnwGPcONKU3u/4pAUDmdZ/42G'
    'uoYMMcLoiV5JRnleP4+R3tCii59vPupN1xZPTb4aLyl+aKnG/bt4Z6GRebc1/uQgK5ppdNcaLa9W+mh5'
    'jpqtUHzs6VApecsKKOf0QIGR24LO5qkKJIsfg0CV3Kh2HkiCdIW4da8lLzl1D9OqKVsRt1deQkgQI4KI'
    'SKykmtmO1n0PxLmlxGZZ6P23QZwWLbCqP3ILl2rSG4mfJ1+xcn0DnQTkWsAZmlTg7gakrP2nFDNN2mjf'
    'PdxmhlQcs9YHp9jiIN5B8BdFLVjMb3nrFFlJBiI4ov5ge+NKms6NRtr0bokYnr+3gfzBcnmuyZNV3rLj'
    '6kVI6OghiKkLIaD0uLoAXuvrtnWaLQ3y9czgSGLxK2IWwYIkkweYRuOC1/wf2lEJc7NtUfXyYvqlipOw'
    'FUDIUnAK5X5m4luKT2MUpptFAy/cKo31quh5vha8GYYizyJuM4LIncDAHSmGpdKlB2/b0eMsElKKUcqg'
    'ecOPPLUyEZWRIQlQifkkhlbp/JLmRrnM6/LopjTEfWOyGAzWnrrhJ6qyM4EX6GAd/Kh5e43qul2KBKhE'
    'stgSdz/7RDk4hmo0RN/rlatCd7PSR5wydWD/LP038vYfuOeF20nOKWs/GuRdiMWHQrh0jk9eZ+ekrXBC'
    'zvFQ2GHtzDmdK5jXl73Jn5Q0RL3H2KVD9I4LTVNoBLzmvbtKSBwEMiX11SWICeWzZ383TIJ9NeMHwrVg'
    'PtDiaIqcBBM2XfTJfTeuMcAOIMOE7hk+OJWYL1ALq8XjTlMEoMdnh5A6zKm5tzpiNBojf2vTfzcdPV8H'
    'aiif8Ag1ll/JhSdl2iCT12MpkKtNulzrvRT+OeLGXdSVzkynwz0QEeOqyxyaQCFYWV4nkzn52GtODXi9'
    'NRrydu/MdRsydxHdpdQuQmCOgNhtYDdvhNPGfoA9cFyMyBGu7iZUB+g9uMC4hakNiPBiqL1aanDhbQdp'
    'MvMH+wk7SuO0QeaOlxG1tS5r67K3oHgl2ulrnchx53BPQhCw3ODEpfJlIxJCOjEXpv6bwjvs9maaj+IZ'
    'rJ5oh6+FxyPyxHAmYnh+kLkjMmlzgaDtiWGtpP0WMYPObnsIYHFUwHFS/MNsCDrhRrou/X/putryqw7X'
    'JvJoTdMNrlK0gq5IDpoIMJ4nYRqg5FYFtoceTvRZLR9TSWRrzoTSumYrOWuErPpBw+jON2JYQ9sFXs+T'
    'uYs0fj6RMPhwH3ziPNJ7KDFrTLrTA9TsXkzgQ9LkJ21tSzfgbWgcGfm7ptCTorwT'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
