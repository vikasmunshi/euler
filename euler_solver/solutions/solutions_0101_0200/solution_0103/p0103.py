#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 103: Special Subset Sums: Optimum.

Problem Statement:
    Let S(A) represent the sum of elements in set A of size n. We shall call it a
    special sum set if for any two non-empty disjoint subsets, B and C, the following
    properties are true:

        1. Sums of subsets cannot be equal: S(B) != S(C).
        2. If B contains more elements than C, then S(B) > S(C).

    If S(A) is minimised for a given n, we call it an optimum special sum set. The
    first five optimum special sum sets are:

        n = 1: {1}
        n = 2: {1, 2}
        n = 3: {2, 3, 4}
        n = 4: {3, 5, 6, 7}
        n = 5: {6, 9, 11, 12, 13}

    It seems that for a given optimum set, A = {a_1, a_2, ..., a_n}, the next optimum
    set is of the form B = {b, a_1 + b, a_2 + b, ..., a_n + b}, where b is the "middle"
    element on the previous row.

    By applying this rule, the expected optimum set for n = 6 is A = {11, 17, 20, 22,
    23, 24}, with sum 117. However, this is not optimum. The optimum set for n = 6 is
    A = {11, 18, 19, 20, 22, 25}, with sum 115 and set string 111819202225.

    Given that A is an optimum special sum set for n = 7, find its set string.

URL: https://projecteuler.net/problem=103
"""
from typing import Any

euler_problem: int = 103
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'dev', 'input': {'n': 6}, 'answer': None},
    {'category': 'main', 'input': {'n': 7}, 'answer': None},
    {'category': 'extra', 'input': {'n': 8}, 'answer': None},
    {'category': 'extra', 'input': {'n': 9}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10}, 'answer': None},
]
encrypted: str = (
    'rw512F4KpSOWGx0eSE0vtrXyI9ymH21478p+XXxsYCNii2GtlkFlXTt+xHrKRIN8ZRzV5uT+d2OkZ5MJ'
    'NFJdFg9tQSkh1KlAaSiddxvh3BPew8OV2XZ/OFN7Fhwy2IwsYMmzgC2bVI6+lDs85xweIlRpKA0V2pZC'
    '1hd1cHSgWUjdpzIfcWFoytjZCjhx7hkG6KAdCXGNbGWBStwKqnzPJDHzZSW/lNKmh1hvnhIL5EVG1F3B'
    '+/fWAdWpVL/JMayZmL5N52fFgUr6TYV5TfQ+72TBEV7C8BRCLgMn9dhgH2Jd3TLqXpKtDDnLyOVNyPW0'
    'GU2EkQZ8t0sQ8KRWpJkTdydZ3gi56vDsdPR/l1wkGl4ZlUlTZiV7kRJlG4AdbWhVnsIwqH6ojPR20dN0'
    '+7txiPmDeqFtD/0KjW2FIj9EetDIbPtCLFbAWKAEP53QpAlzDP9kxQ7j7smtnUGft1123tY/9lIXq5EW'
    '5DJHyq5qaowm61fL5wrxahYKKdOHbGX3lP8kyjcsFBUbjEsCJ+7DVf10VW0eF8kvRe7lQqe5AuSDviDb'
    'GnPCH8fdW4jjUj6bojLnmQoL+xK5fJ0/7zZaip9WFA/uUL7wKA5XbfYRDzc9BOGZlCIEyl6+2AzW3mm9'
    'RrOraZUgQ2/WxL0Awiyg0jV5rNCGZ6W0JmF4cDh26OT0wIXdKdYpqdsu41tDWd5ykTKQNK3pwUlhwzcz'
    'q4Hry2bsjNivOPPQC19iyWceS97sWwxm9wWYDcLvlExRphHiupm/PjUoMJHkoSTnnyZROb2/IpvA97ov'
    'Mr3J5CW9EpXR7K68P5L0T5huFMoXqCCxnQrgj2Ro+jbvv9oRNOJhdLCm+1VPdOGKMFuz4+jXBSimFbhs'
    '0+0mQcg8hgENiCbOMAc4BKPJBqVmF+JcmFoXObJJZi/AqAC6ZQdw0cCR3KWjo67jWYEY/mRKR7Mbp5KR'
    'MPyXONBEZeVSf4qnRbijwHsr8xT/cW2Utmvz72dBJNmN+6UrI+1XfNPZFdKxCIyKPUWZTshvUhg88/0b'
    'rX/1h2Fj6nv4be1rHb4ThCEGbRAB4YswHy8F97HWLS1d8ax9CEZnd026u6SgeD93JFPLcGLLXlKBDF/u'
    'xtTzI6Ptgx4UCepxi6JBFK9js4FZxJWxeigd9UX5G7AIGV54kCMagk/pTSZpn0dIKZhSbcw8JhEh6FPk'
    'kViHqsypDKzJZqhjhI3e+yrYB60MySWK3pba5G2yNultfvAmkSpD2jYe/p2R3YL+fttCA+cmM6dWb9bD'
    '3XIpswov/eCQUSkyG+tYOuNxyzTwzLnHFIXaci7msM0v5DVymwh2KPCQcOT26gOyHvy6BCd5Q93ix8c3'
    'pcAAS3DL+rH1DZ39jEpu+JeQIwYz/Q52m4mKqt3cnL9bPWu8f3wN4XpwmO+LkWudISLQZn2cYpJIhWBN'
    'o5JhQn8/Og2Gq8hxE1nYre1qLD5lyf/8Zq2D0uiFyTPPXadQe1HRasvBqzgl5V0oKpL/yObnTrzbWqLX'
    'Xku/ezu/uWKU2I30RuirIYkj4rdn3LlcqOOzhJRDLT3KnafvfOcAwbEOkCV9oqgz8wPz2lYcRtGoFWBa'
    'TuHclBuwJ6DR8DIkBCgbt/4eoKk27nvkKGXjYzJ2EdfHdpgaFJfTEUZA3H0kFJ5YDgjjOq3KPfX384TT'
    '8Det9jPJjaRrpLfA/ok+hD1Bs0j7x4zmvlypckofGvq5rDCdpjZf9uNnQS+uIeyktZunygVWJYBBi8cW'
    'o3yx0BOZ/Q0P7iqA0PbfnlmSon6sgAg7ImYEpiDiFD4oRXDVkarfXhmPeoR2mNW9osUC/gCbUziMtRkv'
    'ePU3X/sr9jft5elDwGs3LGJkwUDwYvpAGaFX0F2oNWiV62xpnTuqCa+tzhq0ELXPupfof6MFJrtr350t'
    'TzW4offLrfCNGw+PjIpGtQSlLWAkBd5Qzu3BAWT6nGkBY/JKfs/q7OwnKP94S1I7uamzlVyKTyssNBP5'
    'TCRvX3P4Awxxi+4VibUg4dVgmVNcZE6yHM1jhWQN7v+Q54jo+waSpf0/eU3+mAFrlJl/Biseg44VKRhk'
    'wGIgUUS9Hck898CtZ6pzcTLeTO5qEdcsDUDG7nQLgibSXTfre4leaE+SmcZFKw3c306H4VdkkhwcvDuC'
    'DpWxVF263hl76S1TVpxeAvQnv7EmJy7VdHKaf9gkejZpzXAQKp32wBfPpdFPAgBNELjwXsq0npe3aIRS'
    'HntnRMecDZg/z/qCiT0A0b6HxqKTCAWMPB5JGjJf9kdHyExzndKFCvjeJNctp4p9bJNmbQAABKNokoQB'
    'Y6Iwyt3pf+j6LKz0Z6qgjh3VU/g3Eu1x5TWqprFD1hb+YCU6nA216WImyrUAXwITp1ttkz27GYg1a/LL'
    'z1zsoMnHFoGbGA3zv66Ib8VPlfea0lxn4WAg1/O60GuLCpCtXO5rEvTRmGkyZqKZgxQxFO5YgKUFtsj9'
    'eHeFkn5jnZKkyD++pi2Kv1huPP+pyWk5q4+MiNU2qEsjeWloOnfLl7Ln9YSApgvN3fttu79sGv68cTOL'
    'W1PlL6g2Peb/sZSegIFx94Gxmz5XI+88qhdYVwERcQuNtZ1wsAp0vCybGIh/ZTspEh2CUj+BiadhAsYw'
    'n2cmexuL3oKQhc8yRllN7lXv2l1icnfDoxbdK58BvLpKRiSM4PiDVxXLUMF/+8kJWWkyaTiYsgwobr4b'
    '2apJBtLPBHXtCGbLkHWbr7DW9sHPrZeRmadzJOxAThwk05XOG9uUXrGQznAYlGrWWcrBlxSuembWdoE3'
    'TeqXrZOcRsDQsk6qw/41ooYPpYhduaWmgPgWNBVI8j9EWP9+scsuX3eGGzu6aAj1v074AOZoBM0dyKuw'
    'BaBXYBtUF6Jv21o0yrISV82idCGTTsJznN3w+G+e28puMVXy9HYjPJ6YsVD/PcPzqEXGs7Iu4XiIScmE'
    'aTg66PxULz+1mDdPFvnQQjb8f8umykRaHWdhYVNKNHGkbaUchpxU15a3tYeTfMI1NpInaoICsEsWRes2'
    'CEWtnXDkWHNNuntt8hsQo/OdKG82YvRM5eIoUz2f6ZClBAPPi1eT2lxnZYLOuJlwnv3zGr5FGzn2w6/B'
    'LDETTbinJdsaxpPAAIcPaKzeWmNd+sy3jpSbJZNRWZKMXFuyyGDYOWFjEsMrbg9R867IRWP4qxyg5pMG'
    'uA/Ic/N5nATFLnFhSrifATLb7qTVQ+Ztxr0HC9F6ZZPMZwfVV4yotozy/ydSlZU9mKoqpnXt5NCXq8T6'
    'S6RC597AcyT6u0MOKSV6RMwsj2MUlD8ZDu7s/wl8eUYRsLp6BDP0/4nkho1WfkBcLagcwRiJCDhQSOWH'
    '7EUQV+F3qZIKlBhHEEjeXr3zkJ4FB7Usf5nZLRuy3I89/aXHC3yxylr/Oe/7OeslA/oZxZ7cGs5ES3G8'
    'hft4dz355kSWmQfjnrH1vBLQSae5fXwwnoR58avN0kI0EZ8GwiAHTRs/LT8AehR/vYnDbQS+zrfwfkiQ'
    'Lf++vTZyhCDyqTRmga1QVZYd2z9pNMNL0UO/WeULubJyCuZb/8TbHztwLPYUSviEp7wS2yzZiqRLLf+p'
    'vrBxsWS8ZLjAYBQvo4vOlmQINKi+KoDAa1Sedpt8g8OpshZ+84l4Ze5nB+ZT3j3FR2fT7QmUUuQ4CnpB'
    's7mjnsZU1b4C0S59eXWR7cAaX8sfvfRPUXL+VNNtbeXx7T4ZwpK416u23/SJ/Cxs2Smqz0J3wSl/pSvs'
    'QiAF4vsnu1lyHYmAc+BIcLCnp5H3ylk0CPTDdwa3V9svQONCXVHGBrU/jGP2yoArOzEIQc8xNMM4Cqed'
    '8Yw4t3NY0HjZJwpy5x0h3JjkenqACLI13xggTMh5UxJOVbp5EKf0r4IuYYnqokHB552uNkNPJXm64MAX'
    'jM+eR+Q4ya3mksoiFy24Euc5jUYqQmY6ylQYLlv4TECo8mJGbyujO15gANAkmCeXAyXgiq3juz/0G7Lg'
    'zemxUZdQ8enYUVAaWZ6tOrFe7JWFsfPVBHdjGkF8Vuyv9bjB6d2WjtrmyvwwlOzZSL15HYv0hpcQEUDr'
    'WF0YaiazkzT0jP8gUf14ajY4jCssRyzmlC9xoJdIJ04vS9EqaFd2ooFzOIkMvaVaP2cmU1Xp36dHalKI'
    'xTrZivu8eSvD1xtuEzzeOSRTVuBDFOACproiqsU7a5aIN2F3jxlXFWCvSIlu0lPFYkBL1UAzhqbl4tLk'
    'ogTkihUJBFWDLHij86S06Qz9rJVxpIlaosG46geREPRszEWOJ80VSsRtGf7sJ7P5Bps9XcDUY5WdNHTJ'
    'VY34NR+UQWAXYW4tj+3kw0khjiw1p3CpjamnYnKbyT3XxA5LNRWbxLw1XlHMmO2vy1JrwsAk9NwcsqZs'
    'ZdYtWiXwD6i19iE6/wgdf0A3sRKDFEny/1N98Gvy+cA1ScWOoAbWcMRrvXFGrszlcBlra1U5nwtIjHCo'
    'vxZK7ghRA4PtSLlL5dfwFyGavxUqmhkSVtFkfz/7nxIQLcLFZI2/xEBDyJrNWupGZjKK21U0ABQM9voj'
    'eKPFoiJ8tFiTtRSZBqI9ijKrXvCvAyBOz6fpKYV68l3oGh8/gfb38ODS98noh27onL17/MyZNqlLNWvo'
    'wglsBi5QFWsD7rODj4RJODy6LCnhbw2M4HnI0PGPlW3P9oVxAUVqBgiNvsdrqG1Hj7QD6sZS0Ip7PNtt'
    'Iz/k+eot9TSdf/dqU38JAb6a57be8DkhY0N9ZJHGTgfGKwzcWpNrDVEabOtCZ/7If4ebRxCUvx6hfcN8'
    '59Mm6Klw6pOY6scfvw8So5saUDjpdu4ub3GBMWThyPX6EGvMPyzvGXY1d6NA9LuIr+kR9el0ajjrCjrl'
    'l0bCpUM7/Zi8nHHcitj3+ldPPbWDcymyZt2MJJ5PHBizpaWuXjV15A+IemMNFToyKB7gaOCp/AoL5lpN'
    'olImgN0FGFcrn6SURbxBGuuIIEHm8K1e6YzbHSE9EhfUmNUnc7snsyAabRfSOcLF208rPPRk+ycDHJ1y'
    'pNiEyhAoTiCm0umuJJIkUT43WCgWGDWf+0q4Qr1XUi1o8f/5Wv6PHgytw0CvZAnVL7QPkWM/APKvYV3M'
    'ebNXphoMF7Z3jWA6EHVtXMbTonUFnHu2zPBruhcL7PfMu5CBkXdnyclBAhQMt4LNGAbMSYJX87rf/ZxC'
    'hYfs09UcT2wa1j9l0qDBxMArUiQ7RsL6U/gGtBl8QQ8JW+ejMYQDuSpwYOHBtqg1jxZob832tYpsESZH'
    '+gWFznfHPZKnpTzebwZeCNJK/xZmjWGtyCdcGZmiEdWVvVC27p/C5ZOA+QgYN4Z7FY3W/SVnATwyCVFC'
    'sJ85Tk2QUd0hDcnf/JpnsvoqYEM2UZhgE9xFD/Q8HFF9Qv3+d3MOw8VcdmXw/GpSDIGLbcIFLY3HAD9e'
    '3cjKufYta/3Dxl2ObcWv0CKYgELunGH347qKCQg5t3FTGF8PA/j1mli340rwBr20u/k5EhyfhddD1BKY'
    'LnzCr3/tdb3NXF0n6lmpxd+eXoIh62HdsOeU4SapWxSBZbXrwWjWdQUE5VO7/+fEMjN4KPmMXuDzJVX0'
    'Wtvt8OrgUBM2dXG9cLauGxR0ThtRGZfxTVZQxmQVL9pX52mPHZrM/Xjtr0lHUyE7OngZfDyohN6KCsdP'
    '0L8cw9kD5NXM13isq3joPWyxFbLmasYyLh6Eg8ZsXHzz86QiP4yXnKq0q1cJJkKGwO2z3ds774bJ2j0t'
    'pkJVdixE5zShMhxDIWu2nO1XIcPxQXF5Pzblul2idO4c9iIvR+mFcZhx70tB9B22vX6lsi5ITct7+BBN'
    'K+NbNckYG6cDxlhB8kSwlZfQkBl0V8negrBBxGJSDEPm6pq1Vtk6vAsMARcS1TDq0DbXCKiING+Dw9so'
    'tbpCFXixYk+gxW/Z8n8sAbnu4a8jj0ILMSrEG4qJPCROrbCXQwXms4029eoRe+4WNjvujqjvbh09XtAK'
    'iTY1pnsUexfjqbWULIKyV9Xj9cQ3vN1yyjQdfCeIugcQnIs/mNiTsSxvdRRbKBPFHl3RvnF4vEZ39JtA'
    'xYVt3KHmBCUd/zkvGMZ1MsBD0IOMHspeT56AliE65Se9IvrCHDvxceND7ByZ46kSVKFgdHcYqPDd99Vs'
    'MRi7oglumtp/umJ/qFtw80G7K8rl/NAwr+UQOmXYZPslS0SZCyUyG6CsSo4WlnVCT43Q7Wfc9v3w2piK'
    'UQ9v9y6TGEQYxkWULvhpCWoERDJ5AEB1fxONaArvR8HO++RHbkjTsy8GVTxcUUueDhDocYen2opJ8Cio'
    'xuhFTbJWRtp9OH45Qq8xlZ/mtRFOzqCXh7V5dKUut28PXStJI1lnwJhQknRH36CwdAqvpVXnHjhAgg8v'
    'OOnrbt7ZUlmWbQAHsHJ7mm9YaqlB2uHtU1fgtpmuOMvSersRk128q1ufF6nf2Vhw0FDAPIi0Lp4qXH1D'
    'B0ww72mjAjJXkyNoU2Dy84NZ6J+6gwsBe9uvw9U/sKuQGGAY8cc8l2UygqDZDsCVnYClVHGEWCNSebnA'
    'Iwz9J0F7KT9Cz5Nr7kyFRIstVOXq3gHG0+98j8bCnc3ietJDRs/CBQH+9OXwCN5EXKKF4JfzMy2Wydo9'
    'uTHNbbNcCMpoZmmBr+1Y22UVFwtr/g6FPZxAyecvcB+CsID2eOSeJ0znMXgC/0TZzuWOYSyV6Kc0sHr0'
    'L04+CRLVOMZbSqofx8FJmIvuc6CZrGg/izfXwnHhA2HcWIKh32oGKGE1renLYLH3piWg+YJgVNJqtKh/'
    'ucaaxFOqFyhZ5NACs7g0AcOddHHB3LMnUZB8SSgQTUBpsj6JD6wUM77+IGM3vfYD5VtxT2NjzIO9qae3'
    'JMCWgFG/ewflfe57e3bOgp2ColR7iX0VTTmRTJqcNjaVL5MTl2hoSWBvuqnoRjddnAoRW+g8XgiF+1l4'
    'Jar7p5OSgpRFF91srNvmiNPHZaMY7mRgtLcbvEbs8UXjJ1NtOBaHOY413Cpg12X6P1+Z0xDqiD6BiG8T'
    'eSXdN0gm2rXUTryci7nbGczmF6PaP54lUewpExp3P0WLO+sovGvXOnVZNfFC/itY'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
