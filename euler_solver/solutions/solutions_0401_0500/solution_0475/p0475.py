#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 475: Music Festival.

Problem Statement:
    12n musicians participate at a music festival. On the first day, they form 3n
    quartets and practice all day.

    It is a disaster. At the end of the day, all musicians decide they will never
    again agree to play with any member of their quartet.

    On the second day, they form 4n trios, with every musician avoiding any previous
    quartet partners.

    Let f(12n) be the number of ways to organize the trios amongst the 12n musicians.

    You are given f(12) = 576 and f(24) mod 1000000007 = 509089824.

    Find f(600) mod 1000000007.

URL: https://projecteuler.net/problem=475
"""
from typing import Any

euler_problem: int = 475
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 50}, 'answer': None},
]
encrypted: str = (
    'BFrcz7Ci+fNymqsoAtKS8OwU5wnnzHqcOHm7XoSovWkerBkl1cNWCoQGTvivFSUBR6teg3xWM6NX1VDC'
    'OlZi33vvskvEkiEs2AUeGQLq+Sow/rGAlpqkrQZ/wX0PqnpjWieMmWcFIbVJKQZCzWEssd7BnRo9DBCn'
    'tYlOlQLwpGxc4OiWfI9S9+pBBvqUI/DhmUs9slAj9sO72N3hICaTt1lvBH1j0A6IWLHqBKd9Fruq9i1/'
    'VcQ5Ycr3vB/2NujhsIiqnjgXIObZi33VsiKiE0Pg9FhREy2AdPYEFeZZ7Ph/EA4Nn71LL4TgYxAOUKhc'
    'JRlRaGi5I+HaDdPG8qvHIBLsx7lneG4/3kr1UdhPfiEpD2PtYznXlpgv0nkdUe8OM7As1hKjxlLNLqMH'
    '7D2ULH2R4p/tOTGQArRvJZ3qvqjuHPb8bS7XAykI1Fq2Aqp6//ra4CZZULgHdmLuHkruWxzHUyLgZuwL'
    'ylmlBeLAZapeDxJIhUiXqdAfYDPMpGZQuMrPUHROQofjIhLwQ4gM1QDypDHoErYTFTwapLVGEZPQv2Zn'
    'SKJDQkBQsZmw49C8+cf6xeHuYGL+Auu4lRLGiEZJ7CuuMUcwCrFel8rEIqVscgxOTBP53oZcRLbmFpZb'
    'afAMlCEwwQZ2t9YrWCdBGVfgoZH3nezNbKhmpfUCJ00WmjnXibXlaBdbjsP45Wk+PUXn7XDsKjNJGAWr'
    'rDQ9u/BSAG5XebT+Uz4jdZnv/L7INm4KP+b2uLwHwiU9yILdk8iNy3ryTdWh1N6yZgufpqo4BNNfpshI'
    'kMnCQl1OAoKyKivUKAUvtIAa5s7R43bGDFFnR6+yUCMdnaDe85DZHGLFzYUjRc1hhJWGqsz/oNJTbMvX'
    'ynJ4ZIJmMgxl83thSiVzyNok90yBzeAFswOxQVqWAp6RWahUNVU8uQzlomFjQ5IOwAOaDarBjQ50NtEJ'
    'zoHgZ4D2WK+UyX11A/yH1ovq/EYmaFOluRJFVtRVdo5AqD+ctTuro0dxqI1u0SjklzWbiqwcS3MukDgc'
    'BGJFfl3DhI8L+qC4d9d5QMkN5WtXOnBy+YB5rVTaWxZdLt5I2pjfeQYl6945IT/4w4/QyJYMmesUDSM6'
    'u/4LtKl6LpnjkM1mJ7LkTkL1Naq2OgUFevtZS6Cd7HPN3SZj/d3SV+Qw67lzbX8sAxjFCUtD+9PscOhs'
    'PwEzLvKKiuE0gD+3d6wIFVQx61WVHjQ8MeHOHYsQUctjADQ8SLpzy1+UFNQnmwg99CSjf8UQp6uuwYfO'
    'gD7B4fpYfn0bO+pZDt7qZ3p4jzqVrikq38gsZ8xgep9PTh7Uy9Zbknv686BgcbFCkpRSkIFu/r9WYX8y'
    'hivbJ4RIwfVfX4hgnk1uXEaRPBIQdarNcZTufZNq13o3w3AwCUwjtMlEq95WDEmG8sILdp/cgh/ZgmIL'
    'gURZMO2OTj0KGTCp4xlgnv3/7WrKtQWihOIWZ+JgyKWRof+0TXR1F3tohieBH9VQXzOwbq1bE7aqHo+H'
    'wqA7qk4zkNmXs7g7pBjQxcjE8qNWtd2KYl6K1aJlnbdXj47ssnQP4ZEUDFAzx64oHPqQrmpv3tnDErPO'
    'IesVkfFa+mSmXlHh7BVewWB/YYzHd20tWn4vqx7dG39rM8BWWCr4OZaJYcoVjmy8sP7VtnKbkdo3YAws'
    'O/skAiEL4X903ix1TzBD56MVjtbcbR5Q2jQRSOtaeorrGO22GN7ct4u6JM77dciZA8bGWtzE8nVcbyGd'
    'wqeqrjuCufPHdtfAZT303PyIcR0zHla6JXsvt8qOquJnA4kcxfDUlkh7Q2zYzbuONIJGbf8lV+oGq5yz'
    'p1a1KlPzMsLnNg3Dij2Pvfgh0RFVq+jy41cZo07WfkkPfzoSxKY4qLHr+ER5/l0vfje5vnolhCni5ccI'
    '00qM6GrwyEdgD4Qt/dccEia4d711sNgrlaULtH6gyJompZMCvJzZbTm3C0KcTB12xZvOg1WpAHs6slg5'
    'qNSD1tgaeTUAM42Meek51VMSG+1NP6dMf4IKGdGO+eTLh0ESRbnx71y3kwnOOlgzmyu9mNu9GXdCSHwm'
    'Q4CbJwkuhmNL8Z4GdDmn2DbLzvU+GtmY8Ujgs+TPue0kmUyb/OdZgM7zIgDDJjkRdiVv/415xSY/QFDd'
    '0wBFOhNO2Ydm/sK7lA86NG+3hwF03AEACFDkQtrwqSg8vKafsRHx/eOghsnaKHtlCHjIf9uHSc2BfNnx'
    '3mSlN22A1Ks/fLwSd84JNmpRRdNgppHaor6/V5UeuxOxP68GNsU7K6kL1wL+y6mirKTQiKqvhf2JOYDJ'
    'MRyp054kQw7ft8jIlpRk3n0biCJGKGsXV9c3tFx7zefmBSOP/KHmM2B34eczYXVFC6Cdrxjm0isyD7Ip'
    'XS0XeJg1P1NHEy0IHS52N2Pa+r5dmnqqxtuyEYTTVNncSOGJXOjpnLFhG6InaJPb2rYNv2XlELOibidc'
    'yDXaxIuZjhUnWbs5rcqrIjcqBh8dcIjKeVLvSQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
