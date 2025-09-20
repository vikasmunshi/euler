#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 175: Fractions and Sum of Powers of Two.

Problem Statement:
    Define f(0)=1 and f(n) to be the number of ways to write n as a sum of
    powers of 2 where no power occurs more than twice.

    For example, f(10)=5 since there are five different ways to express 10:
    10 = 8+2
    10 = 8+1+1
    10 = 4+4+2
    10 = 4+2+2+1+1
    10 = 4+4+1+1

    It can be shown that for every fraction p / q (p > 0, q > 0) there exists
    at least one integer n such that f(n)/f(n-1)=p/q.

    For instance, the smallest n for which f(n)/f(n-1)=13/17 is 241.
    The binary expansion of 241 is 11110001.
    Reading this binary number from the most significant bit to the least
    significant bit there are 4 one's, 3 zeroes and 1 one. We shall call the
    string 4,3,1 the Shortened Binary Expansion of 241.

    Find the Shortened Binary Expansion of the smallest n for which
    f(n)/f(n-1)=123456789/987654321.

    Give your answer as comma separated integers, without any whitespaces.

URL: https://projecteuler.net/problem=175
"""
from typing import Any

euler_problem: int = 175
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'p': 13, 'q': 17}, 'answer': None},
    {'category': 'main', 'input': {'p': 123456789, 'q': 987654321}, 'answer': None},
]
encrypted: str = (
    'blNHfSm23dwWzSD1FJ9LFvPiORTVzzZz0s8+zUDEFFYu4CnK9D72wr/WFAZl+BPjt17jDFJJmcuMsqkN'
    'HHi8dKER1FlOFFsHMq2DH5PWAdp9N/ILZ0diYAVM9CKglOWeTT9wrA3q3HEq3+naP7Y2M518PvKIyFQu'
    'TEn64mXcmfwzjYcuxAYuwXVYAy1/e+HekJxp7jVILg9o3G2fp6IAdwBBAm95LAgdfJrewk4kgQUoYKLG'
    'qdlegd18P5YLe+sQa3Os2RSmO/ZYSio4flPO+3n0ONFRVxdDuZFBucL4Qo8xhSt96smFdrbIwSCO7YIg'
    'Cfv2AqpH2QMwlRu0zO3AjrtFG0sl9Bq9GfC3d04O9TJ28DZb6KJHpxGroJ+w5+MlpYIEdnC7HIuvC4EE'
    'qxXmSyeHG7ohhAtRJlTZjiHewMCkA/rTIphzBNfqN13Hyx8OzCZfPb+c3vde9RCy1rVkgL/JQK/wmjP2'
    'Xcp3loeimlk2jGWZf9TYrdZFt1+pMq91KDitCAoyYBPMSLDuwVbhL2w3dwsvw1JARzryYckgJ6Ta4Eqv'
    'r9o5RkifYIJTeNj25PJ/jmtoCwKE9R4xPRmhA3939bPf3LZ7jH/z+/CRJQfVB/a3ACoO9Y2iZnHePffz'
    'nHcXwUtgghQ156IJdNVZgv4DG2B0IZmRWV3ttUH0uvGjqLjTMqgiY2C3KbXoJ2Fw9oHTZ4pBe7McQbei'
    'luY2dz2IVTXyEocS/k+fKNrKvFDcSywX8/VnuZQUuRLu8QtW60awGNTSg3UsjoDfv/uGdM6DOnL421zc'
    'srwW21PlXryYH2wIgh+kNmzbJ7UpS0o/nmjD76855pL0dRQzoC1OinfShQZs6AhLybG27XSzyAHQvfqZ'
    'ImJtLMLfhR+H8+v35vT0ISq+ilkzz9Jzxwk90uQxn1GTviRRiw7qndu5GdCXZWo4TN4rd5CDpvx59OPS'
    'VooEVKlPF3YkemIR5cDQoNYpAKZlnbCpMDHej/Llb0Ii4JziZZ2WmKsFABva4F8PCElbU4I1EvTRmeHb'
    'n4xlorP9X5j2LDDu/ImgWaEEW+bdEAy/P1LLZHa+tGRhLloxFSfDJjn6jAJc+12Pg7gXJPmvJZmMZw4u'
    'HLQblT0gXufsY13/6E0AAy3KIauUFre2Ls6v9WAS5qk4Cnm+3QBDU/aOlvfMgsmQvBKMer3XPiNpzrq0'
    'yUk0qu1N3K3YV36EbmD1rxG0qvV3wFO8sLX69yzlBp1DzDuY8Otd2OOgcUQ8vjypnf2qLzcgrl8Y3JJ2'
    'WPU9lesa+0gjvNSaro5hHFtoakLU9LxZBgOA1eSG09AAUI/hRbZD3M7Q9tq/ABGRRTBY9NhTJpRICiuj'
    '7CTPJr4hMfxFLXpEsFLbk6zjNiG8fhBaDb2QM0ZqbRxJnjoQafIhP8m79qrjdsUXcqw6GQuUmtTWCkBY'
    '6Rs+NufJcsH3eLuLjcRykuiRvLk/m55kDtaepQHZseVdaT093NfKw+vqg1MhxV+1Nt0B/nueG6IPc7/3'
    'khDSc4eOVuPFnpOn3/fZw9zs5pQbG57bYkWAWqxtIIhVM0FS24xb/y2OrN5OemGal+KzLdQyRTv4dVLR'
    'AHoKt3Yb6Y9cfopTatSigOJd1czE2XsAHhTrz3t7aFA92JCMoBzaGpPwc/erVAt8r6n5qvT+SKY6U2Rd'
    'CDxJhRlZR0dcKCH+/o68JwEWh1FbnQXH1wEjb4Qm2clnahupw+1GrzZn/zGhuYDuU3TsH4AWxdqyd9+y'
    'w2CGIHMOqW9x1J1ZOHKuM4NOZ4odlYqcbPXPtOop+vzmxDKNwavEKZWNulQjg8fWIaCceARFMEL3neSe'
    '0yyphXe0TdRwpyEaT3FX3jQLWTb0+vCt5T2D2UVCYJ9tYAxdLgfiYKMfyMHnKPMl0+ShkmL6sjCS1LVO'
    '6C4sW+LC5Mokioud9S2XYjaT8J7ezzWXT494iMpGGzXKpE4KCCjsStkbsYaNrUvnLocMw49rv1bXGAYj'
    '+bKEzxb6T8/f3Uq1VFwCjfy/RZOqRIrL/K2NrV/HIqkXOBMh1QUTFy7zSZ8n0nKfWrJhwn30vsawBxfE'
    'G/YegvnM0DBbGl6jcyxz7hBsvBLOsjIiJQw8gNHRV5lZZ38EMlm8TqBCCOXtb3MC09JYpPYnEehO0d/s'
    'gSuG8Q69keIF97/VPfZ4as0HoRhuJv2KGSpli4WEfwj4f9BYQoEObyfhW5l/aGTZewLLV2b/kO0l59ob'
    'JA5flkm/2P/JR/cQ8Q+ExwkBwU97WTNT6V8xFF0m+B4lATXUnHFjrLN5frWgCI5pOxUGrWrm1g2iyHZU'
    'PvM2S3aGFIENuE7Owf3iePWivnpcR55uLJASjBMGb2uUlIgsBDWjbI0Z1irsF9N15zURgyf1txaNzwJ8'
    '70JOe6tXMSuaBHITPjbkIRJTdp5wIVU//u6VQfxjXdYIscvGbqwEBzmjDp0mEKL/jOFrbdYqyQguF0sS'
    '83p/JFpeI4n9zDbg17WT8WtiGgiNufOsk9ZouAK5KTT64AOIWx1eWphBK4mYKmBX3GEA92zal6Jxdlhg'
    '5S5O5zTze+u/yGhsgLuV/GY1Jt91Xe1stER7MRRb9bJtavlnMLb2oNhdfw68o9qIBzNpLb29Lpi6MA1y'
    'tWUkmU7CMRUiBOsmrrvmaQnJG+F1TUF69/fN1fgF811ubMnv/AEEE7zpcDKINK+z+b9gbHOCIMkQ3rt2'
    '+pMNYWIHb5ARKUQ/EslAt5VV244R/8RnanLaFLK+eib4i58bmrRrV8lehR4Lpikn3JuONmj2wUG4A4EF'
    'KJQZKT/XLUBCZXplA14a/VuZnj19aPT5aAebqN3VLCodQ4jO9OoOmOW38WNMVXbE9DCnltZXaCCRyYrF'
    'WZlEpsnKtf23cUEHEbaKarTQrqgYhbPSkbtUGTLjOWjB7PWsoYl+HUMJyLtDopvfJX0BPgy1uEX7RSqS'
    'zcgojIix9r31ZB0nklRo6Hk78xrIPl4PhiCkxKvnWvFPWCjl+KHV4Ac3llZ3axRR52UBIGJ/rMUKLgU1'
    '1U38MIpAS777+CygPFW23aVKH8y6TiOjfuCE4cbGlPSHEmnedGkERjcKgXw9jL8I5KBtwsDNliSN1szm'
    'AaN7e+mrVRN8AxL55j+x64EZTmapIzgw1fqnSC7vz3hkA/e3AW/sGlHNTZnTCytT9YLJe7vVvSxQiFS2'
    'QjNYplxYRa1gKmwcC4qJ9z5mz7jodfTJCxzdqHXMhY0rQNvyxcYlkvRiEt25byuk+XMPIeEmIJYjvH9I'
    'aYS5Y0BWaN6rT6oGi1oeXVoryJH2nZLECK3cgy/R3Nc8z9ycY+mdEv9vGWbSoiRsbOP4MrN3EFCWWGBN'
    'JjQXMlmis2XV4NIB5FdueMsLOMEv2zOxHpAUrItnaNuc/AaGgYt36McUAv8qIFnn53tr2uPHSvitltCc'
    'rTPvjGhIHO/lpPOGApu2XpX/Sjn2GZLsmmVmV+PHbH0Eclcbz0C8Hsbe2UyTPp1EkF2NcPyjl0XNntM8'
    'gtqGy7p8vp9RQ5yaZzwUWpdcM28+OE9iM7Hkx2K9BnE='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
