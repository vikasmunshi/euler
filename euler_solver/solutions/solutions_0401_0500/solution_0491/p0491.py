#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 491: Double Pandigital Number Divisible by 11.

Problem Statement:
    We call a positive integer double pandigital if it uses all the digits 0 to 9
    exactly twice (with no leading zero). For example, 40561817703823564929 is
    one such number.

    How many double pandigital numbers are divisible by 11?

URL: https://projecteuler.net/problem=491
"""
from typing import Any

euler_problem: int = 491
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '7kxCR8ypT3tSKHZJSx6nxY/f0yo5hrNrTiCCzQmNXSOxGFFSbfiEVu3yDPcdA2qbyo5XQOPKyCE0FnZI'
    '25UOAk9kcMf5nG82DAKuTcWk8juQ/jKwp0LqnudL7UuC7+T3uWg9c18aCDE8JAb05usEYnX9NfbH22jx'
    '5jTQ7lrogXtr5qXSEQLK5YmwcKAho/1/YZSSb6N3oJmnNH7vGMue2ObS+gwQqBoMs09xsvqOG+qJqgSo'
    '2Jf39w7g7IM+k8l9E7Nbexxa39fLuNaDdnL43RyFPRDokwryyUy07BiGDg7uhZCA/lmnR8AyO7FvefJb'
    'RBCBwTr1+uUj3L1pkKm9QOaGzIPXNVHf4MhSU6EvUgWno8IPvNOpNwDUKAwXvIlSIgz7Sa9ZY2Y3k99g'
    '1m80scfONG9Hct6n/LhiU3JuJiHn2v0mS/I5X2RpciIBeN30RY5q5ESSUF+orjZIKsgUiq4cyr3ZqphA'
    'dHQfqLsf9yMwP4mrEg51BYI3ERzxU4PIaLrZEJVxPY7CdsYTYZqN4M1mTdS2NCkqf2z5vXhxdV1bRykw'
    '1UtrJfZesshOgWYwWH8N1JOgTUaen6LTvqQ4FC877BsdCswM57qauCSM2WrEz4o2l/hMac7yrEuJnaB0'
    '9c/24tdoEwFVfyNzqwFpgNhBfKyRoAFxV9FxDJjNynEx5LlQHItRGGtCujqds9ijcRgmAfKp/K8wEF3e'
    '0Ij+knbJbfB0EbdId2R/xs4j1zA3Y7nMiLd+a8aN37VFzbDi2MI9W3wP8AQRS+LKGIAtmNg+o0jCgcbV'
    'lhGhAOuue87G8JpRiUOUZ5IvIMKZDTaUB/TeWMTmUnLWCbPwKkvgbey21PcxJ399WrRlO3MMdGZITDYh'
    '/tzA3fOxOzwQHOLL+5ejES5uaQrDAkPO3MuWsaTOBs40Z7Xkukx8ZXIQaygnU5twdXMUGE7od7XRzIlb'
    'MSfGwD2z4CIy+kJRPmq7svcJSGJAcU2bfh6b3YKdjJLi0BHcRXI/JStLfdjtzX9j7ezsOAQoazgjOM6X'
    'NKrF6ip0FIWebbfgID+TyAypbdwviMRGjfqpUYTjneTksAb2h6wNyziayBrwbqRPrx+Do4oKmlrKnPwA'
    'CGgAL2qkhpelAOF33Kmd0GqWXzPazVGCMxxEgEa75kxZeaiOSCi9pvRKGX7CTmRBYbnsvZzz3asbxdX3'
    '9pUSEFK4yEJvg8XJhIalYBP4tJvdMEsJtPkEl4Rtaok/a138z1PKRy2fvB6pzpYaPVBLfLt947q0DgTc'
    'jlYvd0GXCu/VvZ9KKVNRvpnWAq4SmOKYSrJJgYTcog4+nM7DyOMB1eeHxslGH/tnWRWwe7rZMNgt+4mg'
    'Te3OVPmCjn3epiPuLV8FLdTNxR9JtGAUGnmOkOWPmG66G0YMMZMGgSA/iekO7tAUKE6Cj6Au4NPMjVf9'
    '0dtxpl6LTCYB2HQofXq13sBZ6tDBAO17xFJG/OR50nnrI2a7P6GyQ8v+rPTWg01qAW7l3uCHYGsewzti'
    '8OmdotM9Wj8lqBoY93ikQindSD9mfsgup12HT5TXEi2nLlUHtPico13YUqQUSucTLyQV6TazVch08brM'
    'Yn8hJ8ZAJZeRqHjwF6abfUw3V/2g+9/vgULp87/a0JG3gUpiQhaCdE6Kpj9EOIxZhUZBlz2jWn8o2PiT'
    '7HbUIWlFjyagjfrPbfSkETp11TeyrPlkgF0y7KYa73yz9AdEZnPSoDGOuwZwH/Iw6GjKdRir40LxG6oB'
    'fz4pqhcj8PAEi9s1lzV7wlrMDMLOH7y7ZNto+lV2k8SNMGpOL4ucy2OXnBVVzqbg5yXjmSIXMVp4Uiji'
    'RmCMdJxtiWvoX+PhHxBvU8UfGcX57Lbs+RVWyrmvmsjKxkubR8ayXgkZ6LrtfH4Gju+0I7m5KWTGpMnI'
    'B6I6juCEV73sTBnNbQ1ed/wD2ywb7zd8iut6X9oNBacbMBHY8ucaTiP2P/0YX8nLp5zeABpyMaGn0zJx'
    'vnq5w2kdwqG1SZY3U8CfRjNfTebNetqoN9QuOlBrf9WlYuz7/vIpLz1jz0hB3XB8IoNd3CGrGEeLhdVQ'
    '+MlsAkoFohLg4q652FMqdLixUjsPDVm7YSf3cCRgJMITseIBDoDSGF6a0O79UPoCI+7Hk0GZOptDOh5B'
    '9UPr0Rps1VS0T9jq8YvGYAD4Wr+w8U2GlKfYr4PMc4hDAENWIl3HvhhncDpxreReVnQxdjnuWwf4IgkZ'
    'YGfVpw3L+ICn+xQKEr7wIyzwwaCGDaXE5KH4VNO4zP/MX4u+nop1Sp5z9g/2xjaO'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
