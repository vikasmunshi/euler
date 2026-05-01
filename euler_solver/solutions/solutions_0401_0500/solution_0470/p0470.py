#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 470: Super Ramvok.

Problem Statement:
    Consider a single game of Ramvok:

    Let t represent the maximum number of turns the game lasts. If t = 0, then the
    game ends immediately. Otherwise, on each turn i, the player rolls a die.
    After rolling, if i < t the player can either stop the game and receive a prize
    equal to the value of the current roll, or discard the roll and try again next
    turn. If i = t, then the roll cannot be discarded and the prize must be accepted.
    Before the game begins, t is chosen by the player, who must then pay an up-front
    cost ct for some constant c. For c = 0, t can be chosen to be infinite (with an
    up-front cost of 0). Let R(d, c) be the expected profit (i.e. net gain) that the
    player receives from a single game of optimally-played Ramvok, given a fair d-sided
    die and cost constant c. For example, R(4, 0.2) = 2.65. Assume that the player has
    sufficient funds for paying any/all up-front costs.

    Now consider a game of Super Ramvok:

    In Super Ramvok, the game of Ramvok is played repeatedly, but with a slight modification.
    After each game, the die is altered. The alteration process is as follows: The die
    is rolled once, and if the resulting face has its pips visible, then that face is
    altered to be blank instead. If the face is already blank, then it is changed back
    to its original value. After the alteration is made, another game of Ramvok can begin
    (and during such a game, at each turn, the die is rolled until a face with a value
    on it appears). The player knows which faces are blank and which are not at all times.
    The game of Super Ramvok ends once all faces of the die are blank.

    Let S(d, c) be the expected profit that the player receives from an optimally-played
    game of Super Ramvok, given a fair d-sided die to start (with all sides visible), and
    cost constant c. For example, S(6, 1) = 208.3.

    Let F(n) = sum_{4 <= d <= n} sum_{0 <= c <= n} S(d, c).

    Calculate F(20), rounded to the nearest integer.

URL: https://projecteuler.net/problem=470
"""
from typing import Any

euler_problem: int = 470
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_d': 4, 'max_c': 1}, 'answer': None},
    {'category': 'main', 'input': {'max_d': 20, 'max_c': 20}, 'answer': None},
]
encrypted: str = (
    'KxrMxiRKSwh6A3Q8lax66TSJWrvPY8Pp8Eo0SiQvJOxgCcA7EoOyNhGCy8Qj3OWScB3j7HpNb/1skBSI'
    'CXq6jflwKpYvKGh/wrEiCQepF0ucad0xcgDhl0cnmJjsFekrgyftac0CbXJTSpStVKPprEg31E23Qfx4'
    'es6uaxtAOzfY+vzQ27vVohuFVhsweY7UTSP2eccmexUVrZX7t80h0ZM1COSCfCH6vUBxT9kUI/3B2drK'
    '2g1u7e6w0DK0bVbu0vLheQ7gSxQN3GrJpNVCP1QQnwsBm0s2YvQcfyFHcxBEOVzlMmAjBDPcm5TGthTi'
    '1NAqVtVWQcqRZtkLogkWemqeZMfDObf1xSrWTxFSSYcgBMLeI4tX0HCaG8vOxnzyBetzFv50n+SdVKG3'
    'kHpfD3H2471m9HLjkHUslzohogoXcOId0Op+MD37cQxRU3xhz8o8OerAYd8cFIiumkFuNRgxzO8I8GzU'
    'S7SQ0YcQwvUXVZqtDNoigVpfTKilhqs/cOY5Gwh+9O494gn+kPYTrp64gCOyeTjsV3LZNAu62QZqzfmW'
    'bQOSYsBVke+YO4yvbTgrV7FhOB85ki/lbELL+XoFjUql51dGtWZS85ydIcUnwBfGO5VEpI9oXR74JVYp'
    '9WyKLAHcfTKTV9JhZfx3Gj9WsM+PGizHJKT+e+R72iOQeFpsxZbHo7PqyVNAyWEi+y/cSkdNOEwXeax0'
    'zO8D7BNZ+Of56RfXv6uJwZQtRPZP8e6Pe24oLU4A+5ZEXaWtyhLrYX4iDQ8ej0tWhD8E/EJkTbfrSZ6I'
    'frh3b5BcabEKsM1qEPm8+03FBgL9fUBvNI2GSIO42wMWkPEVEqgG+TyStUoy9V1r3cVT0qDxOXufCirg'
    'BNLu8BnGvH2gkp9YC7fKWaeLaFxRMKlWFBAe0ZYZcOcxWZncDFGotP7+928kL/QBwUWn4jdLJLhaPcVs'
    '84/C6KDyLtBeCXo7ziVTJgR5ToNe72P6u5sMuyJVuRQpNmCaEF2f4T1z3gtId5FQK0esnLdLi6Cm8JU2'
    'Vg/jtBQiy1djLqKb2olg4U1L0hR4/NnoWN/dLG2gx+GJPXF8hp1xSUhGSP2DOd3VpJkzD3Jdya8Yh5/C'
    'bCMs6Hidca7AbvGzt/ywI2IkkV9figi3XoXTxe3BtMGREIt/S3lmg7htn6jQuU0RDtTZerAxjTiwwmGp'
    'zy0r7gnih/Pc2XHC2sZTtuULjmxTe4MYoQWvoK4UUYzofyCLwG5IryyVj9IYdYRyT+xiw7ZBz+rB5FZc'
    '/t3GCer11t46x+0a/kmBP2J0LxGMQtMV+h9k4mqmwz+Vk6IoaFYZPWAhdrYMX4lkLe+XXNk1tcrs4908'
    '2B0Pon7rNhuootlhIN1tk6Qy16YkdoO+C7Kee9/P5g+HLbXnBy8jj+ZiynByTs4ErkQhId98d0DcfxiC'
    '7cqOrdunSX0VsgGwAA1AyOG3Xkq4AIlIY8iwurTHLSkrR3dEX8/5vl+HtC3Kyd6ZTIX6Km8hMU7f7ZZZ'
    'ZfbmnE+oQKqFag579nZXxPWQfChRZdIyvlu1A67047YtYkLU5ceTdpiLjVStPbsZ7pJSqGLTWSILKsKf'
    'pn3MOY/hP0Nsa7IymqOqNr2ZKacDeVPumTwBEY7PK1lADEImQLhVRjun7czZmQUZ5YyWVvWguMLMTWqJ'
    'cdUh+wueuDI1Db4zUp04wTTrpCurGuEyWp4jtYJZnEnZdJ8ho3n6sSSVL/+WylQCCTY6t7wF7vjWnWLW'
    'RID1QUTAZUSl1wiZjHwlonYOlUyOWAYu61ZTkNACOyXNk5WgqKa0x6YiULAmiK2jxqTONoxZ8WxhZzyy'
    'wG4ksPkWl7YSealoMrllD+uH81ZVUEuwiUG52W0ITLcHgH+tdWKwZZ5pl2uOhn8S8Lt03uDLelhL6fxx'
    'rG6pp+CI4sNjdcSkTdZax9uxBiOkQRbSMNUusWj/0GFgxsaSJf1uYAmH/VGGMouD3k2tZNBhqmtGGULA'
    'T/v78cD1tPmTIZ026yS3uEo7/4Xt0vqXihrVBSeGu593mqMXFn8zAzhWQoPvGR3qTXmh1wUkOYk6Weg5'
    'l6o0rmb9063i6M+QmcouG6FNcPxmWN3vCojYJpM24O8POClZ62lFznpo/kSJ4QVWRXxe2UqueYBzRYmG'
    'QAGsssECgU40jqamDJIO6UwyU4WCl2uqwpE2MjHMExQ91cRuWO9BNkv5fgDmNN/gb6ZHFZ5DqFtUSrj7'
    'zUknwy53C5ki/iz3/aS7vxmzpQYHjwsbvbpwzXcZSLIb0+3Op90/x4vKUgC98tK9TR6aXpa+dxa3tf+t'
    'siPa360IIwmQl1lY/1Poi1KQz/gbNd+Spq+7qP4Pa3VWmYrPIYKFMXMHKh5GtLzOgPnOYAGiR33Lyhvn'
    '3EqeMrATx5X2XbVVTr5IWdOCR2tXj6UNaCemobu6C0PK3KM+x6gVYbVhH6M3Q6+VdGLGVfoacAURNibV'
    'dNP7KdQpsNusrqYm4NJ6GJP5P/f2zpb47S0rOVJexw5ety7xKTYgLfasx6YiGaT4jGG2fRbsnNLh4eGI'
    'Rfl3fs6B9g2qluPp9PYeVAB/URjGikEPLmzWEhqFXAwIEg+UPbvDjTpvWWR6nm9f9pqDnLf8EHeGeLat'
    'heaYHWg4uSqG3S2ROnOzqnSlE55r1IwsgdTwN6BKpT2k8AWdR0qwzowZtJLVKC7pNgXG8H515UtYYfz5'
    'tErymIkxPkVMu8q5MqNi2OLO73fNCimX7CiMHyJGF7zQQVyxG3vDbOg71iexQ45e6F1Tl6ar8FvLv5ft'
    'u+1eU0zEsMGuBC7pbj2lf0lLB/wxsjv9G9YgFET22FOrTJj6ZY3p8LtrUc7t5VpzptifOnJYbHfUcDBT'
    'Qap2KNVpd/QIeAkUD4RtaOulQAeLy9oFPt8bom8y6G2GIBz8tW5NcC2WwxDPA7KaYx33VAT98VOpmy/4'
    'L9aVZuS37ajJOqgpUGguRDnEsjVpYwfuJYeH/EqmQFOXyXY+58JkMBXV1pE2qqp2r1I7c8fkmJ2ViR/r'
    'YjDYPUWGH9lT+Nu60H+xUSrLITcPxqpNfcuxm3pa+emdF6fFLbic0fNF5oBXfpFHJirQvz8TIR/5l3J3'
    'aIacU6XILGcHey2+tkEN0u1USk3Th+aXsNSc2MMuRsF7vkJh0/9Af/hGqyyZ8yzJz/B3YGC+p7i/ZAd8'
    'JSHE6tLlZW91rCxSqWOy4upaF7PkWzH6qsW/vl9TEMXCgOtD1uDfQu44UIZkFNbg65zSXoPumoYOiXaY'
    'i193V9bZH2UMs1J9ymfa3eTS6KbqNtie0YaV13DWnW4FN4alWaLy0rOe3NpXgnfL7ySEMz/KivKO3Cff'
    '8kJuMx+gXiQogJHq4FZICn/bVW5EwxbM/nb3Iog84lCiOTSUYHi2y8Xh5PQvBM3V0lLogzYhs7upFVsw'
    'cl0+cWzYoNdZYsZ1PDv4kDLFN8BqvF8iSUQ32+jZjBoxrH5yQIdBnIjnrJuZvh/WegPSdPTwbQojX6ZT'
    'q42qiSV0zBzxuJX8272hBUM7NYoEq9VdDcFJrENzPk+dHS+ev+sa+A8Kdr6nth13u/Vmr9aHxgaOMkFw'
    '1NRxC/P8K0fNLkF8lVofkpSaYDNq5sWqaD6Jj0s+mDmQu2C/0malMp4Pa9wdndnxxZv1N2VQb1h2xNsx'
    'Of3EooGYUYeRPRXbO7v7uYIgFnhoGceEOT+yafOkCrNOP4sogQCfu53ry58FIibvfRj+Kj+E2SKcAOCN'
    'L3hgWPm2m8UQawOYA+cu0Oa9uryvOGsv3s1b7/9RseAmFYeWC67L8wS7dUCNI6Cql1bkmj8/6A8tGs0a'
    'KtUIuyKFLk0L/eTlDWPvbOHMFaIb3/7KmQF+dWdpJ0H/0o8oDwcLr4JWXpc+wrv+MG4S56e3AJo+JgMr'
    'P/dbjzDVhL7luwruWx3sS9uhZS+plHVTjJmzYelfxhxyvIV9CDVV9BuXGTyB4APkcaupWO3m7LUplB2H'
    '/94YN77fQDhRbErI4lxDg3Dnsmfs594Rls0GlrOqgGqHtu3ZkB7CjUh9o/JfcxGXVD08PQICatSioJnp'
    '5lQgXAeCC1nPV2eafNLC7rjdpFAXGhN6oTV4cfW7vruQYAxOu3qVOzmUBnka0N/g5BAWZ4XS4/KqeBz5'
    'EOkQeANdH+Qr5/qDYwvcU6YEkv9sq2LVLj466n4eEKsyqZem/OyUwA6K+zfNuSNQBxeJua593avAnj6C'
    'o/2OJGgHQDlCXTWUapkm+/PuziLYk0KYOsy+HSzrWs4/LQKtK1097CL9h5lMqUygr1LUyDUK8IpvmPfA'
    'Bc7s/RE+SE/FK+RZhLVWnALCTWa5eps8L4396Pj0AYM5VXR9L4l+XWWHaRC64kzvjZ0gJWTRdomv2gX4'
    '0Zi0vbJzKRpmpnCu6KxHAEN9rq7KxKSSB4wHAM78fwyZ4iIcH3cQUhopRobJ5eybL06Y9SarN63Edc9Y'
    '9vRo6CMNyqqxwn/q67Is5tx+EuvKFfHRkxHxSegii3Jj6UuwWMtQl8d/ZYNJ/CTgZoQ2le+pgAcr6CmA'
    'yfVcrs1TVbbc6iOkDw8hrRk/IrrCLTNN4yMFxihrn2F3eXsR1afVWJJBNqczs7RgkcZAC74G0GvCySBR'
    'V45Dn/MAYXw='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
