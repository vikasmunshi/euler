#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 135: Same Differences.

Problem Statement:
    Given the positive integers, x, y, and z, are consecutive terms of an
    arithmetic progression, the least value of the positive integer, n, for
    which the equation, x^2 - y^2 - z^2 = n, has exactly two solutions is
    n = 27:
    34^2 - 27^2 - 20^2 = 12^2 - 9^2 - 6^2 = 27.

    It turns out that n = 1155 is the least value which has exactly ten
    solutions.

    How many values of n less than one million have exactly ten distinct
    solutions?

URL: https://projecteuler.net/problem=135
"""
from typing import Any

euler_problem: int = 135
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    'p3X/C8FJGBvNW3GjK+TeATj2sCZ/NxcPTijSVEXMdiSADcbhW96QREhhJlIqKHO1rsWC79T7p0qtjhua'
    'ZBGtRpEAlZByEWSt75oJd6L1IOBzoW0sbLOd9xhy5agFIBW8shlq1BXa+efKCeQ1Dbpj1nGX2WnwzPjg'
    '+GxIKv7QlHL9eelCDR9QeHjNnzng4XOYe5VOc6u85z+hH8VeA2Qav8cyzdJHjwx9vSzz7MEAp7DhS3Y2'
    '84NzBszcDVBgUjztTB2UTSUjanFXWgD+pTycqmef1qUKSM0vM7fkzqYM6U/1MKmr5dSdJm1QCr/GrSCp'
    '5fFbeENTepbdZI7LJWH/JeQMlA390HuWzaVMWAHEoH4i0PwbvW1m3TnIXqqGEVz2arqdby22hRFV//wq'
    'iNdkzuaYk2+tSpkXBknHArgBIWSlQvgmss75NkPd+MsJTzCeycZPhiT+xELdJSRkdHMME7tMZlkwL1/i'
    'Slqss5K7wZcvThsHa1PVwKBLfFJwjvdP6t7iN94Ti0lsFOcOV9eeSOrVrGBYBTzE1bkpZowlOZxOs7HD'
    'Nm20+o4chFiMZ/ku52iDjavM/1sm/GO0N/cxoltZ+2O3SyVtYO10SEHIi71by9awAcTY8rfXY+yVhpL2'
    'vt3SIencWfoVjGH3+FP62F7SeB0X4/ntGlV56t89Wj/XhDzdfaxOg56Pc/L8N3xqHN9s3xDM4D+rwont'
    'KGFp7QZlSdtXp+tLQW8o7NnHl9uwp9Btrr1K+4Cf2DHSX4jMvAN+j93X6OlDZhkKxxYCIR9gIfxxqT+A'
    '3E33h30DNV084FWItXnmuI4fV/GRZ+oa4AM/ChAuiYgA0dLUL4jT5/QdDGrn54OriF1XhbJqAt9VQEwp'
    'XMLKsopjci70xm9aVvwvVcjzoophBZktjkFIuA7R3YE+QozXO20twf0lE5N5bfATsHH3g3hXxmUhajqt'
    'wQq1FfvDD+WDLO2B6RGf9xETSGErIKa42KXKBoFeKlUng5RA4lEnHzB5OJwQUIXBzpoQRzx+Jaj0oHbk'
    'TOWl0QJgRXcy9UHxC6QkTCCb3MIL3RL4evvbTvsWpI/tmVvgw0GTLRt0qGsPKgk0sFx9s51J3uI6JDXr'
    '3d4g16Q5goqUOyArelpSpTcJ63MLuOH3IlN+gpFKRY4I63mALDmErMRXTjx+PtqH8EaPYybnd6mvHqqg'
    'ix77rORiC4/NdG464c0LNLoJwrNIhrX606KqR8Tvm9C/PkHCRrBGiFtIrnVGG6wlxgIwm2ArrTXu6SLS'
    'WKjwx5f+ncf6roxJZuxLPnheYMgsyjX8cRChMGm3YkQ7p7d43u8vP5Pp/jFJ2l3XlIV7XFUwHymioM4F'
    'cGwLVasVJlYmh4dxl88w2I8fqOwJ2q56zuv4ogolvQefgjx6wslgEz3KoHZL0mi29t2gVkaX7dC+wvMv'
    'mOXM+hbuYimSeNJNL1Wcn6UnlGpP7dQRCh5B54veqOjNlfS1lO+l4E5M8eCxp7uFfHAJc7es+lJuHvuB'
    'nIxb9nGUGtOc/Bnzhti+aO4cHSWncllXAjBYUqe8z4jl7Q+6eAKfrHe5g827Nyff1EYhdI87m0Nv361D'
    'TWWcLjT9qrZo15Op89oGQPR70NG9AnXhb2gZfOn4N3m2wt1VurBcfRXOiwZ4BGKtlS8giYMkPi8u3upb'
    'PondV35dAQOdH3mfLLPn8fHCHqBbkdJUiHDqfmn7zY5VfEF9ApTrzqmci9Ud4EDWUUGBmtastNS2qiQq'
    'PSubbIgxNJoSFNYwmuY1rtLBRMzDFkLVQDR7X4QM4ezRhMiTt8KA1Pc0nP0IYwCYnLB3Jmid91/J+ECH'
    'TuwPcuqWbTbNt1JWp3XFZP12ftUjMu7Spa9syI/zZQx1OccikKregcHH+RBe2v0Bxikk3Ksnj5n/VwwX'
    '5O/fUrlKHx35O2ow6K3GEnkohg+ohcs0R2ZA/hjF3+0RSS34lqI9BnaMiAGKFN6B+AgP48rp/inn+PCf'
    '/DUqIwASSiqFHnYErnvy6P81bWneXeu4A/IHGPkZuew1nDpud1larbkEg3N2xs1DjRuooqLYFvglP9Jv'
    'IdSiGSJOIMOMTvJxYsOpj6KM3PNWU4PlR5ewe/AwblF8M3ohcAx1End01aPIotzkXPP3l0G3V7Jq4B8E'
    'mOxFZydzIPUD/pJPpGkAZwd8dafh6dduSVfSvdlGZELWeUuLAIQV0T5BRZrq2Qsb7xejytvxSEc0iZty'
    'D8BvpcQA+BaQrOnAbfnjGckJyzyTaArUrMOphVq4QRJUAVTC8b4m1e7sofBSj2qgIFvjG+2xb4TV96m0'
    'LLf3sUND5p4xMS7ZueYBYTSt0iddqvDAsCW9hFC6+fs3wa0pKaIxBZrskz3nF3ndRKuA3lx5KDnPf5tO'
    'fi6gU2C1kQwz5vZnpFGoyI8LU+EDEyvwUb8SqxFgw2pFqIfec+2N3Z550LadKxJ3D1bLcaAfv4oZrpg4'
    'HOp9SoipwMjUgcx/y7Hz9o7t0VzzdtdX0MSjoObiwoRRZ6vuOl84RQgESV219kMBJdJODBQfNMGJWHhd'
    'IA/lQEhet3ZJmRyTSlQxUw3QegFVh1/rB8wznGYavyFj6E6yumPbJMQq2/dLN7FsP3PfManBTpJYfHE0'
    'DDOd3RpwMUqDtjO/SnrIqPxx6ZkvKPtcu55v2UVyzO/hpt+ScmyTPEMZJspTBn8ZWuCSmrwGpKI2elGT'
    'U990sa+RPzyN3Oou02ysEoy0KLRm2QoqcPDMFoz7063Bc/+qznJcaJ39rM0Y0CUlsbK8MwR+Q6ANhzWk'
    '1BmpZkjkezGI+9MM'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
