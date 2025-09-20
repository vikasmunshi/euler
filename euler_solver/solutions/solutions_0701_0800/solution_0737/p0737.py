#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 737: Coin Loops.

Problem Statement:
    A game is played with many identical, round coins on a flat table.

    Consider a line perpendicular to the table.
    The first coin is placed on the table touching the line.
    Then, one by one, the coins are placed horizontally on top of the
    previous coin and touching the line.
    The complete stack of coins must be balanced after every placement.

    The diagram below [not to scale] shows a possible placement of 8 coins
    where point P represents the line.

    It is found that a minimum of 31 coins are needed to form a coin loop
    around the line, i.e. if in the projection of the coins on the table
    the centre of the nth coin is rotated θ_n, about the line, from the
    centre of the (n-1)th coin then the sum of sum_{k=2}^n θ_k is first
    larger than 360° when n=31. In general, to loop k times, n is the
    smallest number for which the sum is greater than 360° k.

    Also, 154 coins are needed to loop two times around the line, and 6947
    coins to loop ten times.

    Calculate the number of coins needed to loop 2020 times around the line.

URL: https://projecteuler.net/problem=737
"""
from typing import Any

euler_problem: int = 737
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'loops': 1}, 'answer': None},
    {'category': 'main', 'input': {'loops': 2020}, 'answer': None},
    {'category': 'extra', 'input': {'loops': 10000}, 'answer': None},
]
encrypted: str = (
    'zmfpw9BKl3m3pVThs/8SpgVyV8l2xJJGTB+fIwBBO7JVHuKfplXvVB9ucL7k32hIey95LOAGfBIO46qL'
    '2Xq9fH2i4Pp5x6Rj52en+aMj0XdXCw1WoHMr2HjMN94ZJ4Bu/iS1RbIwNWmu3qAZ1+NNOOXrWRrDcPfc'
    'g+P3KvK1aktaRyL1mcXHJAFpOHdcDWRUFg7tHy6sLmxDrdiFDM0CFQRI5gMEIGkuVIr0QtCyxL7UhzlF'
    'BpD3fvfl3599NjMiau62fqyWH9ZLF2rhbcqKZ3c+Yu6V1eFLMlFA3Yy0//uAM8fEtJiKR76u85gYJHlu'
    'kxfLNOXm81BEQtsydds5AdSerihLJKu+V3fCGNMft9wPkrW3GQ3A7k8sptUGTHvLNiSu+/NRNxqRtZ6A'
    'zcZvjmILnn8xAiuMKE4+EyroxI96zLjQRc+03qwdZ394gEvniYfVKvVulBjR0B9d4NzhezX+ieoMuCsd'
    'zgnemMjXolHs0D3SWBEvO65iBsE/pVw/mqAhwm8RpKe4YGPABO5PpiGHc6WbZyIr6I91YfVZSYhoSNBR'
    '7Y06KwRgKB5ODLqW2NLldweTi28nxeIMqBtAgR38O0DrUXU/7+PuiGAB/os5piWYe1viEa/XsBtj24BB'
    '8LbMi6JUCU6PpUDOhgiMvJpO6mSzN8kQi9q77PU/LGbasxVrJLpzpHwPnmiENRZ066MXhL6aQZ2vXBiu'
    'otk2QS8bouASI1xbTD7ph0o/3I1Tl5e1iBJxvLDgORkuEWwp0DSppLqX/RC+GAUZBX9Q/g4Luew4wkX3'
    'yOF9QyUbbqvMDea8QP4WBIaOXzTQKP9R3oZgeIxiyLByvjP7Q9yN6J4GMas11I3zeAIX45J1sEe7pSIa'
    'DtJ6l3DG1i4opqmsR0juUuBRWE6Dh5gkIMgXwAcNNMZxKy8UcPygq2RBBNFShoaUgEIY+HQIY/sW5we7'
    'vUF0dJrtXUzQ/qpe8H9zCVJx+a3dT2Z4IvEW2TPMnHv+HVrEH82JNJ0MFGY1dvVJo+62ptZrnGSFk6tL'
    'oQbQF/JZtXsofwkbjG9PuU9l/pUEOZqvvWoyRU65xx4vqqAGIsjaNHFTyxGN10Fa34qNwhNNauPut2sH'
    'RJk9bJrjMkygSU3DqSMds5fYTdTFdDCV4LrX1o9y3t1/lSHI9VYtgdQRVt9Ywk+H5xAEokgGoPyFfy0/'
    'BNOO+d82daAe3qknuKEaNABhmL1ri8lG1AUbGneUpIEIQYTrYAAyykGWpSarbEP+OFrgc2qB4cuoLYt0'
    'ip8/0cF3pOc3MDjRptuuH3u76U81rnTqXT3gSYMkwFNUwJHrP9dT4Yc0ebYyBfC8femxBnl2SaYWgZ+v'
    'qeiLr7inkuT7IHPDScTHCB3DCzq1uOlNCJtX56NEIDJ/ZM2HpcGkgNMhZkoed12whTitwNWBC20doXOR'
    'UJTI/vcRV7dVf44HTJ5bNA9oDS5tzi3DHWDiv4NVgLvHu4a4Paj4E7xLiqSAeoCbQLvBQXdj+HLHICRr'
    'zzDqnUS8msZYR6AEAfW/WJPuu1JkxYfNyNJVdgyTHQlsalxAEiLp2/xJWFG/2Tn/in8HIVVzKoN+nxIb'
    'fFnw270sly1ocR7Zn/b0/inJBv4tvuB7DwFXtSMztIWeb5aNCaUrzRj5xR7MKMNLrDU0h/a6n4oUDt5w'
    'cbFjUgZbJxK55aUqSixTRakcwuqt7mi5KuoGBViO/OUckQu8rAJo0zcVD1f0nuVapK6JtzT4yaWhxhm6'
    'oBEql0Oj3diRgmbkMCA6RNaveWARGMEEILbbAG1M9I59YlA6xwdc6FW+dsAWFyc8rW3nAGtXJAHZVx6Q'
    '35xFdnBM5JsQtQMn5VAqVzbf+B8pGX2jmaeKhwwp7o1xtheyKUvFfoYdNN4WcnDBG0uEMs7hj6rSdwcf'
    '0TTgaLdIu020hb7ni17HtwnJLl5CdFWkhkQq8bfBBQx4boKVMyr9NeCZlOwow+XHXLvrLIKmtOO+vwNP'
    'Fh0fKBGQuhPHiQ5LZ2+wIQ121R6X4RpakHgkAgb8LZk4uYJA8EQuk6HN89YbvYW5sYC4bU+MJKCFwKON'
    'KG5u5Zl9fAAO5GyTtZylB9ZVw2glxjK6g39kYIB8xJnFiEOA9hUuo0wAF+2HTBkE9kgGjwWKF1qBCJSt'
    'ySyvDq5dav3vCX0su7xl/qNkVZ91Qo66kn8XHMORPjQSsEoFnbMkaDN7QJJ1bMwCmBOjjGOsKbs0QsCU'
    '34V6Qw9WqLqQmGSgWTGTLtVvcxjEhm4fL9N/0rlGqcCWKkGmRaDmbOdTGP04dIRuQQieNrqGIzw+K/Gd'
    'w8Ys3abiKVhZN2O5tDEsj8Zt3HwXdIpx1OV5+XbSyhiYL0HpXkbd0Fs+4EQyLAEIbHqCWlhKzhrdINNr'
    'Sqbtn/RD7N3P6PUn61liO8/Kr0pcQCUQV8fcGF6q0TwBhVc1ZdOUUKOYRDkyct4dIBWKsap4Dv/ZK01p'
    '850Jzh491NTQbeXXsjqOGW4yOntRf4muHLRnRVsziPV5tm19DW+YYG3flkBs3f1wJLAn8M4uqoDhCL3n'
    'S+KYktLC9vzdZuRVHJ1rBYN5ppwTQPoZ3eslg0/9W84r9YJiu763lz3mqInSeqocbY9LGL4a+DUHInGI'
    'YuBAWYwSEDuJ6LJAudsp3H/b/o+UEihp1heo84SHUPLd+dJJca6rnLHxctxt59pNXEf00QdkTGxSEVVk'
    'F2Rk5/jTf/r3ea/odNuETpfmC2IpbcEL/cqb+HhmPj7soiflYSRWXjxoVFKD7a21lerk+WVdNjV3pR4q'
    'fEZ0XuvL7c7A7qNcOBqFqeqU3e4dNd7FNVTA+2+80u0p9RhreaT2zgEFHl9UWxW+GoGy1BtKuT2huZmk'
    'CA699dLlTN9O3vMl+fIi8GX6jtn/hH59GdqUNLa77McHPwA4sjmqGKCfvdiMgMaaHTfJJuueg9HFG6wf'
    'PJeZvrAaPvGexBizOMFvhDDuXF1kCCX9NdD2SpOBFJbDf13rP+xQ8R+YfCxkKZS/P2ykmkdV5iiaEhIR'
    'nHYMs0slvdoiYcGeFFaSsyip7EqitrG+3p/OUi5hpC0Ge4uoGbUloZJ2L0SsQEs7g5trzRS1fyijxbU4'
    'pZ04Mrgof58SFxsgDCovb2ua4EfhoJVf7cm26m/CDA/t7k9Ku3TwfKWXw0LhHUYlkW8FyQPhRF/HsNdO'
    'sGPFclbNNUb7uvozVT3ZREbm+8affWeCR/nobr181Qyz5uWWNOn7aVN87dsXK5CSRTF0qtQfAF/JLSA2'
    'NqIoTRzddao+5/n4ec8hK0BYY30ny9WVLck+Q0m/SA3oPfgkAVqFS2DryI5qrhBMlcXDQA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
