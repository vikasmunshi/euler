#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 110: Diophantine Reciprocals II.

Problem Statement:
    In the following equation x, y, and n are positive integers.

        1/x + 1/y = 1/n

    It can be verified that when n = 1260 there are 113 distinct solutions and this is
    the least value of n for which the total number of distinct solutions exceeds one hundred.

    What is the least value of n for which the number of distinct solutions exceeds four million?

    NOTE: This problem is a much more difficult version of Problem 108 and as it is well
    beyond the limitations of a brute force approach it requires a clever implementation.

URL: https://projecteuler.net/problem=110
"""
from typing import Any

euler_problem: int = 110
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'min_number_of_solutions': 10}, 'answer': None},
    {'category': 'dev', 'input': {'min_number_of_solutions': 100}, 'answer': None},
    {'category': 'dev', 'input': {'min_number_of_solutions': 1000}, 'answer': None},
    {'category': 'dev', 'input': {'min_number_of_solutions': 100000}, 'answer': None},
    {'category': 'main', 'input': {'min_number_of_solutions': 4000000}, 'answer': None},
]
encrypted: str = (
    '4k7QLr/2TN8RAGLVfQkITcr/DxhTdLQOOpUFsUTke3VI0OMih6hlXJTaQhmGpxxt/VoF1CSYFSIw2c2U'
    'IUWlCp3ETmxI9VRwfdBjyNdZngews2bDVcrLnI96EolxR987EPkXexQmW1jdqv8LD+0l9vxQ92TO1yck'
    '15gGxPP90dfirevtGgUpztm5F4QfR6YRgNdx9s85y4Q5j9uGr8mbKsLIU+bQ77ZY7v0hPh+LKLTtEUb6'
    'SI7nVVX67GquvoSUwnE+GlUhmZco1UAQoXonwCwHt+CNAPa8VMfmtSQIbhoY2M8Tp44Hn678h4eMD4NH'
    '8Id5AoftdOptt2HhG3vlQXCY5ZiOEkewVPaUT3vIfSJvgWCpERnNYvclOa0GpeUGYNDU6GedfSyYcrKg'
    'ljMsZ4Ldq+ocOLhcoC6DF1gJ0mjBSZ9oUSFOZh5mKI/BCzwXBMzwKhmoD8OfxADwPv5c2AXRRoUTEa19'
    'Rqj2y6WfK0ilU8Pl2Je1HWmPhfClfgyd1nUR6inYKvRuqH+XCJJ6TKzVlYXzBoZmplHNzANut+fNaMas'
    'WY/zdkkeYyUoNJh88RctzsJCWI3sahIQB54i6iYXhTW1kX8LF2lpYwmybFB9q2+rHQRLocWo6Iywm2Kh'
    'AVi4sxliEBlzLW021wSXr3GPYiFejAGEDNqoBqIa1tf4tP2L3Y9kvWOQg7U1qxhJ11eCsS8TUi0dddjA'
    'HxgpkOFcAPBtvmA63DwLEcBoWO7Bc7b3pcHz67WwcZNoOt3TbnbiQSvesTdxUhjLro8RBvx5ucNFsSEz'
    'p64NrBu6gicCyeTzwvHMujvWfLE6HNwB6awAeKFOGNXyeajdn5LPA4g42x09v8ASUvbfInk1Lkg3q1E5'
    'iTq1TOThMPrxqh76n2/C7/Sm6cO8JvKsmInPGvawt7QQXn7YHHr/+l7mY7ujwFtYCId2NGEXqBLgjYFs'
    'RU5gyJkmU2LtOErH8D8ett/OQlOzQcKeYaSMUkvayDntNyBdHtk/pBso+Rd/3ctCQxc8g6JyNNDJ8DkU'
    'pcres1yBFvp9ICzrROzw+Ho1dw0/54amkqfXYtIUH0PZslRrt83CvBg5FeHM/djyjKOwSUYzcXfgENtl'
    'k+jZA0MszRjes+3q29GmBCGIHceYHEw2sMrxwjU6C83iuab7uKGHrxmDYGgtdcbjsV9UICobK+BSFMPb'
    '3rjrfiP90+Yr82basymiZSFfvgOq2/jCz8IFJIQxmmy/LjY8pateslwsfLu2APSmONGIOjnrNMBXwblX'
    'Z7wAl3tj6T204GNrNnTIISOiKoZS/BLmhEbCNmce/dCtYqeStjnbiWawNZV0i3N7et6umq+SuxswKklG'
    'ReUHWrfsGERuJVtBuFfyfB5CYF+4yo3lhi7j3R7xVVN6CiND0c5+6DtkfRFXW+4En0QERin3mAqpvrGj'
    'Iw8X8FTWruvPfUnfHpWSYsrVa/J4jLxL/gTeFmyuddjMuNjJTv2h+1nffsWcChvI/ovseZ5pEHfoMCos'
    't1c0BCVO1AjT6tqxRPQbIOLbqiTZkjOycYw/4+sAgCgWKPmvucEr/MCSyMFM+hW8QI1Co9zQ5rlWE46l'
    '/Il2TSTAPnZSWRh0kEg+G5DqkY6WV3MpR32XUDZS6xQM04/wTpSluy5/UkdYVSn/LWhMcpvx1EAwwj7C'
    'k5T3FcGgC2JZeVpefo7KQCiSGZUXyTtrLcKwWKTe2wHK9rKixHlOgUoXMzK3ZrXs8Isn/16mfqCK5BRV'
    'HBxpt6IPB0SosSMufEEAL0DALvdDbbeClI7bK/qyWKadEmQ2Nj8QSLKEHQSDMncg2S7DRcuH/hGjHM6l'
    'IURzFzqZcBma+ez0/XoB1GzHqG00Jnx3wKa4VTNgnkX0yBTYvwhWwStocjK27bCibXBhBjqpDx4yZ5Qt'
    'c/PyAyoVTjO9luBOQ+qVGNUfVJ3QL+kY9XUhXqvNnGFsYoF2XEKmTyJ8dG+TwgFkyt/Ze7cFIP2Qfj5J'
    'd6i6PKboWtm+cjLEXWeejYLNFECLs3K+/fXiCXWL2rf+fle/2O1Qavxc4yBCwU7OLJAdtzXxDEfM89MQ'
    'yepyEmj7ML308IhUBKG0vGSwrimed3t3+ajxDprwzJVDgik5yhpeTaiDbkP+6DP0lJjjnpVjgCNqfOR7'
    'XYsVSiYgPIAS2iRLZ54KcjGScqx4ChOPD2x4B6YcGvCJ+I1iz0Rv3FPnuFCM/bOlJOtUvEDpD24wZVE2'
    'RqckTjcADkKgx2wf/IVF17quqc+JSL4Tykqm/3sgqYzFLQ03gmfkRozt9zLj8oGbzpwr6Bfw66lI2sIb'
    'Bd7/C8hFwrF/qRTOj5FAW4SorcFol9tGgr5NVldYWyIDsbBguaJw669F3cgjFq0WBQOqQYWdPUhHe4Om'
    'gupoZGCBe67L5lDDYH9CVz30Hi18O8/WLZf7lZlg+ye2HIPJhACf90qoUkpSQ8HD3TkrLdSHM1BK9S5d'
    '6zVEvbCEjHjq4T7uBQrnfgJmBIcsLc0y3Ru26wBbLw4QOm/W95G6/cNgZDNNTopZSXEKPvsp122qhKJK'
    'C7RY9kEb8RDE4PEM5Ke9y2mViFQyYNEUxGWI1pyK9OCec+nCeUFlzjpsbTmfz5VZiH+XQcE4M/c8UV+c'
    'IyWhpGpOl5rknxCKv7joEG0GqoNIKHYlFjTi4/tE9kuMRsachl0jLj0AUsMWChyo+7hK4mPi2m7RLXmq'
    'aR/YgJuuf9uNMl3NR22bcgWlcJycT6eI+qmRJboLfk2m2M06ZSgImxjJWy8YlwpjoqBFLesS4XkIb88K'
    'cDzQ7Kkr3ePZ6eY+vIAuxiXSwL6lFIXrch+9WMbEHwTfIZbsKbwH9bIOsWB9bsmZcU3QNSlwqoHTLFWy'
    'hdi0a0Vkpl3XcpNYV5Dm522FxIJO/nZbdadkZ0k+stw0hIsGGCE0TztRCKDhmh8jrCqw0P28SfWAzPyP'
    'n8Z3gMNf2IIUBR9N4IOkgwqTAVVMcANQa/jfBqhiKGPVvAHyl179I8+M11EHG5T592q1Hb6+msq5FKD0'
    'x/KKqlLIbCffA2Dalii6J/87rszK/xF0sa4OMQH8lW3GhrqM+s6m4OiW51YjbsVsTblWKDeymhkD1Zn8'
    'BbuM4m6bnFEpJt3eo1Acp8oQuQHJYsz/DE97O0ryXKcvgrvk+fcF7QrQZrEy6WSwiT2VYsqdn3p96dHa'
    'gPIQTMTlLOjYmsxGh+Wxv2hCwcPK1Igv+yVNtIVLtIACGevk5yPpq/5+YHRb4waPqvozA/mp3pMW6uy2'
    'CXcFD3jsYOMEuzy1YWVTXW8hdbGXJP/XzUGnn7sL0TnqnZSc8yCeAl4yRx+yo18HikywD+keo2NjJN0S'
    'Q8F7zuIsXAzMAJf+KBeixA1iYD2y058LUHibxsDPezj4SISxvsLhoNqplc/Wkn8uHp3G1VXZVRQRPB5n'
    'x+dyCbl08nthVXP0+aop4tj0wkevQ0jUkQjYYurcVYHvP8Ak+KNI4388eogMyVFvWWcOwF00AU4pq+BA'
    'bgrfERwKv+oRZqK/6mfeFzKuA7AQpnyjeIYY/t8Q2+sFjXRGioz50s/NpK1TTmqfl3m60yLqM3JureNb'
    'sHI2u1BbYdXy245msoVMxLdjq3QMQDMhV3ergEukKeVyQT11wNNxLPnyMZVV0c8AEln7iA1fN5twDYuc'
    'I5dPxDkjs0ttuDsAy8L8+2wxMhPB17Mu8BjAUmDDb8yhtNGnNFeWTdfAv12d4eRLI0UXdKuBEnxvLRLg'
    'kCiS8s0cWI6rDB3X99RIZCjMQ3Df/ooyLoCbSagCQIWcJv+2+loHMRssLAhrv56gv6ZNBcdIEDY+sjFy'
    'aJAmUIS802imzfWVEuUufKrL1u/l86/VmIOcN4P9F2YdaqJlsoXFZ0MfBdvmJeIzr1sSA/f5pvL5VJCz'
    'dwS4/lpLr1xpCKqjwL8wqU3b7mwm/aE7WNcNraIF1L/7WDjDOH7b6EWJmXGeFR3++uszRzYiSAbViq6E'
    'hfJhH/cqbun04SjUHBVKXowa+hKptaT2sTpjSMQm/WKQ1Y9HHfBV+90lZSztYxDL3IrwO0UkOQZb88/o'
    'T7AVuFH89ahqAV+N0HQ1RGTdhxLLBe87DxA/yFmeAYOUOrjdy3nqrlj6Cdxne09P96Y0+QY1g1OhEexk'
    'MDPg/VHLpcb963pkL6O9o8FgNszMIia32tnGJgHLt2OGGJOVGeipBuygd1ASTnC+hPWbpZLv8m3/q55M'
    'YarWGBwjK/Hv1XIjZq6VxHYcgjoP/kPVnf8ZuGxU8qnz8DdHmE/rksbcfGPSClvQvTeJp8WywLnsxAWK'
    'EV9Ve6FyHJMLhsG8tpjcbz240ICABjyFnF8kqCtLSYDvFKIzl9ENNuDmWq+UfoJOemogstZn107V9KZd'
    'O3UlnX7pdE7LMNOF7i091vJyBt95yFOjiQUJbxvEXHVN2zVXPyKUOx9fE2F246A+aavY85ne8j3Zp/8w'
    'k3syT10/QcUxmdrCdDp9sWrxUb+SQZ+Se6yMyb1gwvZIeB6+ePe7Lx4/hzIxdu/KeEXSXujPYiZCYnOI'
    'p+OEfHrZ7cb+lAvckJoJo6yxtBwiXkX3dJG4RVCPTMXdNgRmGYYPy5niW7LRaSZFvpJzusWoevEo5Got'
    'mM98BzvhVL2VdTb/Raxg7qvAXJReGehoMLNyGUDCrKT7/REx1r+ntWZlZMMACJUU9p0PqD5kubOTVNLB'
    'MZ2xr446W9ZGPxnpIOqW3YQXT5J/GZb84lTxAGyYZxFQvIsCOLCf2MBwZ+Q5ueycrIF6Xces/OeSNNzb'
    'WmtiSc6uUau3CuRgkFM+tvG+PhJX4i5QvqdIdgQGaGBadY5OxZEqQS+r77WWIlcENvr5OT8+CPlKTIbu'
    '/aNI+7wUY3byZPjk3HE1nO18G3GmdBnMfTK4lzhayhFYk8L9MS3zVkks/cBm1tC+n8XIPLGH+0Z/etqA'
    'vTlgD/apfRknA44Ayx6OI75MWFW/F0B5uzFi1TbispkGU5oJVXW7WXIzrej31EErYutoiXd1ixH96Qig'
    '5ZzvoGkQzKfhzE5k//oJ0/HNIAI7PrsPM90OALtqP881xj2xMrRnxYNsQu51KDBEBva+yduoz/jGCKjf'
    'eJXEb3LsUGNv6T3ThFb6ItEm+P9JlFmHa3/3zk+pq3cpRxp4phX+++h175+x6CVPu9I7onYAHDOGptd1'
    '5u7IdxLnJwC2NVsUU2hOY4042Bo4iNjJSWwu6+otyhLB3vUetFqKTC2XJaw/vNR1hUp3qpo+X0yKROj0'
    'bvygzpufJINkjmM7tgtcf1prp7IFPeB1XwCkj85p9mJygr8k2bE/xC1WuWWJ8p5j3p+Y0UcpyxQGW6ko'
    'WC41h6kE45Pc7eg3VINBmWxV0bK66hFQ+REEbZWV9mq9RLXHeLevMZ7Qrn37kR9qZdqIRvPKPFfvu+lC'
    'XbkYHSvFiItXTVt/uOL4WnHLSp8fIuXdzqkSQPabqnzho/GOfG0/rrB1SpY7L75ivv1lpVSFIey3VbFa'
    'uTaWOnsNM4LglrVV5IVpV8zsmw8kPS0laJFsd+euMDr9WfSnZ2wYQJf+TSkIvN5KAGfbmzduOPZRo2yK'
    'J4uqZ2Acc+WNIxqHxa8fNwYAVrC6lO0mKQiRpGmmcNC27XD322Xi1Jq+KlQh7ZsNZFlaEERPWciKpr2q'
    'avZ/1cMO1VbMtHlGZC7HUZpp/xm+448IS3o01vf5Mh+smlvT+47PrfsisigXJPWMk+s3tMYsZVNF3nH4'
    '0C7RvQAaKP6/4pXm2EScMsG/BnOEso5rWZ8OuNT89V/e/mKR29GDLx7zPLyxWqcGaj/6zjsupxl3wV6e'
    'YfervbLkIaU4qxn2YixHInuYu0ZsOMF8yAZnMoFTCOc+5l+dFPRsa2Acrc8FFJtbeAbdcXp9pt0APzED'
    '1iHnP7dWHUDrHrfuLtUem0kzLS0C/QQ5nn9oL2ugZ4m2gE0lDRR3719/gBhbovPjO5GS+DDkE+6Sxxx9'
    'NOl3sYbEetFIvjsJXUdowSQzqle+NNntANSKx/d6IHB0CHaIV5lfy8lqiIaoSdXvzfCTBH/qv+4yWvMm'
    'dIOmpCW8LaGCdrxGsbpnVUtyTkWeZy0Urm+6loF2Gox1p2chRT/76Kwdt4qSn7VTiFJdf1XxwQHhvbYX'
    'BdWd+olz6Uf/esGC3V/q2oB+AQXOvICldjDU7ZHanN05qeFXILPZ+bgBRAEH2IHkQ3xMwLT/Qa6COwnk'
    '5hrF+Jp3NtC264J3FsobjAxssYp3l6iW2jZGCxqpx1ahBpUw5+xef/o3qx7WCYF/8A52OmpnJ7icv0J4'
    'THyrxEoX/XIYoS+XJ2bF6krxoKgq46569pPZNGh3/MuFaXUUbldBefRMONoyfipzNgA+POQFuE7AgPDs'
    '3aSAwZH7QX0NincVt0SSfyA4f7LEnR6OBXXcQKyJQhTkYurwg0VReAXlV1QodnXOSvpDOvlcrWkXWDW2'
    'wXmXF+eIbXNh37gGm3D9808h27KnlPFPdwmCu1qSULh3MLPUsWXZzlyxpwfXGWZn2cI3kSmYkK3Fj0pw'
    'qeYk6cm+XjfZg6BMLhtlpl1Xqn1Q2kcxazCJJQhv4h+S0xunVHVqM1awGstyydsQeiwicYmDC5Qz+ovx'
    'ChT1yLplDhp6kUX3nC+lDfjjxnNp0T6vIl9HfU/2XBdkR9AkgnJhIRSdz3xYVDCqTfuyd4G/OR8gF0g1'
    'wJ7ZfFdwhzQaGhYIT2OPDK+kqF2jWMTJmE5gMSmCuUIhYaNX/YeictEDX1o6jGwqvnqT3R8ENdY94w6z'
    '4OZFoahznlJEp/abugPcIggIa/8DbYIDr8ciujCtpLciDm3ZLqzU4JrETuj/Vi9k76C0f94p1UxKYiEz'
    '72PXNSLJRyG5lEs3te2GDCbLdmotzsPW'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
