#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 750: Optimal Card Stacking.

Problem Statement:
    Card Stacking is a game on a computer starting with an array of N cards labelled
    1,2,...,N. A stack of cards can be moved by dragging horizontally with the mouse
    to another stack but only when the resulting stack is in sequence. The goal of the
    game is to combine the cards into a single stack using minimal total drag distance.

    For the given arrangement of 6 cards the minimum total distance is 1 + 3 + 1 + 1 + 2 = 8.

    For N cards, the cards are arranged so that the card at position n is 3^n mod (N+1),
    for 1 ≤ n ≤ N.

    We define G(N) to be the minimal total drag distance to arrange these cards into a
    single sequence. For example, when N = 6 we get the sequence 3, 2, 6, 4, 5, 1 and
    G(6) = 8. You are given G(16) = 47.

    Find G(976).

    Note: G(N) is not defined for all values of N.

URL: https://projecteuler.net/problem=750
"""
from typing import Any

euler_problem: int = 750
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 6}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 976}, 'answer': None},
]
encrypted: str = (
    '0P+nXZuYgsZ9/pMR7nh0b06ErDVw/AZQE4iNUo8RF/MzPj8rFm0r1lr2ativJhjU/1LGyMsGud8guKNC'
    '+EBX9r2iHrY+syV1u1KLQVh1qCcrQWN1RDVSvZWxkraDgp43bqRZNKOui/WkfdN2U0Yl31PnkVUiWOdZ'
    'j+//qdqsi4Ddv9gJoUiNDz7ilU9ovKmSmjFMjlO4GCVgyEBTL9DjVihWFtNhrbKQxjk2yUl2fbr3Ruha'
    'k1rka0o5lc7qMT29+CetHde6HZM4UddnVzJwdRR/gvbL9robxrhz4Wq98wFaTZ5l66GMz/wLTbVnXVZu'
    '43p+6S7m86xET2YChkvatW0ss6MkKndOB5ZyHVZfsOx0GF5MaQUq3v5ntAllO00U/UepyVNdPGmgjyix'
    'cUXWVyexrtIFn+3TfjGnrjOAgBqQbs1oeaKszGzWj+Ynbx/iz8DnNyh+ShqgDIVFM9sbbc80WgtmhS6S'
    'wcAqHB/v9DOO79rmDbz0O73rve13PdsEI5yyTWStCDI3LIb9wemPoAYllX6Rr2mm6V2tXVcv7RM4qguI'
    'HvGAi6evznmv8ujByCix96KvPDaJRaJlmhkQ1MNzMrG6IeXgwnsnmRQQN1IAWHdouUP7pHcXbqqNsMIA'
    'yhq/IWjFJGXo89H/ukA4qFF5NnUFtxC2bdi57ILMUycwqCyBUDCIncJA+Tf1xFXBuYpDP+GyequfM0a4'
    'VngG3x/A18AhEXKy/6jPQhzperWS1ylnG+4lkK5fL2R8Un7EirL6myn3/HkDe9naI3rpN0t8CqyxAM5d'
    'jKzZHU0J2qmlMM4UzxJgyb+udBdMnVi/K9/ANsNaNAccIwEfYryu28FDqa/qHn5g9J6oHGVPXZRjRjLs'
    'UcADoS5MXFAbjHieCYQ7rz/ExT3Q6DusN5cLUzs4chCkj6f5dgcLE4zbdM0DyJAwn/goD7xxLgRll5w8'
    'XJonXWygaA2g9kNtc2YoSaKSraw5qRaE4odrfcW5YZbVFNypSe4OvodhmT6y5Jv7Y6tZ7tDbkwqiHtLc'
    'kR1UXDNw4ch1AYxq9Llq7rMDJlxrhtO72rGg/C0dPJp506CNt8pwaAgCIHc3WdtSCOA/q+Xj3w9Xszce'
    '0Kd4eHRkzuAvoOM1IBK3zmy8OGlgkCorEb4Ipp6X3PtX7qkGlofmp4vrvOZWg6pjilZ5UHmRFf3OmHW8'
    'nCtGLce58sMeg7IfuCj+TvxKknWykVHspWwMrEhhIIeFEORSmmSOXgbwnQFxzk/stvH3lF8qsuHyCQE0'
    'BNezIUa/LJk6fpoXuxTQ+0rDCpogypakTZVORqS9lrICxJyxwaIw+BwxQM8jTr7CqC0G3IuYhDVuZtzg'
    'Mray0udA6ZkrCIJDrrhJc0QzCq0+ZyhM1ddIq6LzZNESWKIdoLHq0gXgt+x60cdN8KpBf9Lrof6tVjKK'
    'weCsZpfv/pA4zEPTTrWpt0B57cQmwk3Us/rwYCg67rVL69C4RlMen/jYeuO2heIWP4XzY2UugWY0malZ'
    'l9dg39uP3OiBkmeMQmlNuZKUjQL0Hg6kJ4G37gt+qLiD09YrZ/nYPSOVMKVcKyGw0VBAoAwc2t5SljUw'
    'Om2PQFDtuCUsJTSqt+w66dnCQ9s3Ggue5Yj6mW/7/IhwU/vge4ny54oqoR14FEXg2mGafc2xEkM/W7pJ'
    'ykULDrzk25Xo/QTyTKu0ctQZyFqf73GGynuHOw826wYJAdF8fShsBdJg1sToSILOIgIHMGxh8QLJGpYb'
    'Lbc2noT2ATjh6eUga/ebShd8zQ3OspNtiSHWG8fq9LvcajVLk5oprjlc7E6grw0FXaL4mZ/mDEc7Bdmv'
    'yi0p18/xGr2BcV30NmQE3S6wACOenOoiVR+R9OL871CWNG+n+AAAy1st1VBch2DQGmNqIkcUqwyHgSFZ'
    'Sm+QgC5qUicDqIrtYUjgvSpB9rucGqTzZ2dbIIs5llEU8NbABN0asMH83odyQ9Ui9iUT0j3jNxfmVFOw'
    'nzbe1poURjOc3euaqq8SaUllQZ56djR+u8O5iUGG/6DFkh1RN5HNB7aXXWfw039OLMDL6qEnL9OpVGTw'
    'myQt0wk8WR4HSL6+cD+h7DeKmgCGAoy0s5xrklYdHHsfCFHsOYVqGAHvJ0Y46TwgmRHMhRcAtHmNCZnC'
    'cuQRAbbisjrfaG5yQXLkkf+LIbYm0/gIH6w2hDNbIRTVhQu8I16TFgTVxORYytM59Z1jIu7ytxP7ZlvH'
    'P1iW8mezbpluuIk+D96K1K0g9GeZ8wHJmUwHCGFdFV0q6QmtVR0lQTNoKZRALP0Heto1EsUehz0KGPXE'
    '5Q1tVtuI/09WKYEydvA/rVOLjfTkpOvtYb5zyghIAZf15BuP2mO7qpDVInzldXdFQK9DzTf4wO1qfm+k'
    'rrunuMHXIkx8gRt9guqgbboh/EAP6g/Vn29rNrajMxU7NV/Kh5iz6nIrLVsDg3TVPGSuP/ifw9MBzxhY'
    'mPeLzyI5O7m34YqeBySztH7w4Q8cyAo+Z2CEYEiV1U4aMoSZWNTxGuQV+uGs9fuR3qENZCZEtgLyrhn5'
    'IQ2ArB+jvyIUcsAAnEOdCgZ80KvKGepUTZC+CCOUXVrU8k6LATAhboQ3FF5ovYBFBKA7MckxkYinsqe3'
    'BDL6igLTLUjcte1zmrknZdPto2tR6HeeI0xGg4b+xgDBFe0ft9x4O/lYd7E393wziIPwUYGu3lWkH9DA'
    'ez8nkro5KJpWmDa1HxPbkpeftaLLafDYz8ufi2vwoWHPewApHK6Sn6Ftzka0V9pIvQlpzSZ63lIF/BqM'
    'nJHzwfXT/akdcfyoJOjI86eka/Kq4BkYldrcXUwA7+Sw8/T3JXRLC/DELLDNQkrwXha3t9N74iq1SNfD'
    'iB3erX8TaKjxZARdVGwqSTXRHsWAtvN/6SlOKeT5Yi7S4fiiCV7oCN2U1P1/rCPoMBIaE7xUODAVYKk1'
    '4HAXZNSukpjmx150VS6H1US2smlb80feJuv0F9rGD6jEUSQ3HlNq1oXv9piWoqWVzN2DOWEUZr9798o2'
    'Hf1ezzztzVZv5rcOgfMcF+Ie553xb9zg93Tx7kq5HUBCLe9At8pb5RijHEv4HLE4FA6Cc1e8FROvvTra'
    'bzJ1RazUPx2U+1Y6'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
