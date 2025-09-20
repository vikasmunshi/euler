#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 832: Mex Sequence.

Problem Statement:
    In this problem ⊕ is used to represent the bitwise exclusive or of two numbers.
    Starting with blank paper repeatedly do the following:

    1. Write down the smallest positive integer a which is currently not on the paper;
    2. Find the smallest positive integer b such that neither b nor (a ⊕ b) is currently
       on the paper. Then write down both b and (a ⊕ b).

    After the first round {1,2,3} will be written on the paper. In the second round a=4 and
    because (4 ⊕ 5), (4 ⊕ 6) and (4 ⊕ 7) are all already written b must be 8.

    After n rounds there will be 3n numbers on the paper. Their sum is denoted by M(n).
    For example, M(10) = 642 and M(1000) = 5432148.

    Find M(10^18). Give your answer modulo 1000000007.

URL: https://projecteuler.net/problem=832
"""
from typing import Any

euler_problem: int = 832
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10000000000000000000}, 'answer': None},
]
encrypted: str = (
    'VxebKr4soKlYDddnimFnDlz26PX38D7h4PlPx7Cl8okMdusI7uFfqDV1Yktd0RGylrjObQ/Nc5vEXCoW'
    '3qJF9Ygvi3TGCvyugCt9m38uyC9fN98ShtaLvH7HgqNQOD/A9yKsZlGUAOSZ5bhwLu1E4lHFsR7qdXTN'
    't8NVUwqcqaOViwcbS9pAjrwszGdrQvKXZV+LwH+OdnhWv4umvwq9pTgX9hU6yEBmm7lzC9LJ4k/Rex9j'
    '0W947csX8lZ+DC7YtdZe2EsWaxETZROAtZOh4j2SCgytCXESIBxxANu+e2XyYlnKHR8NDXptYBNDMUys'
    '8H9FR+MmsDk09cCjfVR+rShX4YgpIU8qxwoXNzxHGC9cgSnWUB0sxVKXs2Y4SYDgRIocKGoK4/zoNzGC'
    'pz2Xax/DFYhfOL81hJYmiBZ85gW+I6UVhEKYZIppoNWdrVIMNXu+S2uZ83Jdk2NWRylp7Oz3d1FIqp0Q'
    'efU249Nctw9rgN1rA56yNDGFkwQeqTqK9bXTea3sepSvk4bKRt3xHFUS7qzn3XQmmCrzC/+f6c7e0sP2'
    'luBqfsPFxRGvR/lcU/EDnmG/osNzcX10KVvO2Vsk/kCYvmUyugGQXjFonbn8nLHxrCaT3i72MDEHCymt'
    'MgwUQ0gbzRj++yGkuAnImI3VYEEgMntY5I16dtLcEdjfQgpwjlKQtnv7ePau25sFdLnjUnOtXhkwocuu'
    'ekPEAwhEsoW3RMknnNZ/+t3X9KZdGKqGOoPsDQ/emQOeKrYsEK2yqFL7CbeAE0yy6ePWRR6B0otV8WCK'
    'JAKlWwz11ZsMQAH3UdE9WcAkRWc1lUlEFWQNKUMmkH9TVNcmCTk4z1FgQtYLQ0KcueX5VHmwxh+Jw/iP'
    'teyWs9keVgCS8mf52nOLvmmKWIS/7PFnQEd7tbu3L2hgN3W6f2sXIQUXyEny+Kf84/XEUCHef2V0xChM'
    'nDJC8uJN1bssbxLUMqlzsssczmuOyFONpNhed2/DZStdA2oZhOU/IiILGZF0XUkaknpB29T9zYC3JD2M'
    'XF225tWMb49Y30EyWiO7ru17yTIghFq8j2AZVERQZw2wAvsn3jGpexBBRhhl0PXsgMfRlq6Z/v8zb38c'
    'ftFI/kkiC4wm36ALG/U2lkz4ImdfAJhIoBbf+fLkU2uLa5dHS2VVfsMzk9bbhcAXrExp/4NQLz4dywLg'
    'fje+u95/uUQNHnauGLsb+n2EuWic/88RUJmlyomQPYkdo1G4sBImHyoB+jh+6Fj9vJ3WM5w58z3hT/X3'
    '3U+pDe9pBTA/s/VBN9UCt5+sF1wLvEia00JK6Lq/tK9vOaa39La7C/n7XTwd18JMyhf5kv8pf9WdEeqh'
    'rBwaAJpAqGiQS1X6ys2BMKLNSPichSG2W+bLPihJ+VX2V8cCvSpQFDqp0Zf1AL18Pfg/Bew/U+Wy4FpK'
    'Tuiz34bMMAaa0+R71Zd3rhRbq2Hd5Nw5suR0NxkD15Z2xspzswYZ1M8ssW78dkpHZPDFFnqLvRH2p9Gq'
    'EZ075lxR+tICc1Jug0EEa5X+G6vUigJxx61OxyPRNgLZW8sEOiZ8hbYR209ggeOlrVTgYCeE33VhVk8H'
    'AfAv3DF2rvXTH0m0QfvVS15STpiiW6eDMVGO4SDagyyB32wtTa0BOYmw4EVMOp9/o+un3whW/NvfVhmR'
    '2TwuMcvDeFZMuHSj6FgIHh8Xz1YISHr/T0YtiXkQTiBt0tl9deo8YDschLdSJ/JpKJyCa/4lY8YIt5Wt'
    'EOocOE5nnYRG64iSADrTTY67tQOB76Ze3nuJcDbpOjYHof97SzT1++cuyVUsFJZRT1uMPmolOcrBzr6O'
    'HxRvKqKpQ9wP27uRSrgA/jlHT+zy2X1+MoGw4XW07BTSpafqVo8J2Hx7s3VkRYCK1GsWd4mLJ5XuxTUb'
    'UmP094xOSgI9ZmgaDiiUO6gotE0KRgqWGH9UtUUC8iMildDXUE3Az3a01gVTHXQ3ZGBYV65TanRpehzL'
    'fV4Z9tTW5g/SboO1vcUBqFcTcERCOowdSMx7qFOmSEGlOxraMU62zxizpVoudfc/K0dEc0BbbYbAJflc'
    'yd4PImnCj1pZ+irROfSvU8uIns9be+medAYiKeqlQS5D96Xw4vvThIyv0/JpDaSiEKZP/TnNSS6nex4H'
    's/W2mVR6DXvksxmID7vOVLfqm++amKHj4qF5pIzCWfSxH8hbf5x20FRYG7x1bOIHvPknLf4V8mVTVzjy'
    '/YCPBikLs4hTJspqTFGe70cZT8K/khJPwSPSsL47X4d4/243ITX9mniJp/2192IG7S1WoKDowUZgV85o'
    '1V17HJwTBTpeD+74N+PiFFHqYWMhhkv7f9wx7QkXvtnyaFmzVrGR/KPWDfR3OXX4pqz+tXvaHDqTCB2F'
    'kZInuxMM/QG4/RnRBv24GzQgGvX8ZdngYoLoXUQ16t3U+VQpK6OEeb+j5ARLqo9ZPzxf6WZkxFyvZmYx'
    '/6ISZhne33Jy+fh9zUHJagUBeK7JObV5TSJ+oxMISkq1NdcNDzQuL2s2MJlkAeKhm8ohlU1xlmlvquLI'
    'ZlP33cOgrXX7LshJ+SKNls8nAMnUfwEtbkuIzQFbxTD446G7tUQwd8OO4mbjBkE3D3eYeKngcxkxB8Uo'
    'piE8pKGk3cvf4DQkoo3ZKlmcM8SwV9MmFTkMXH9dYz/zcFu+PK+rT5QE97P3cQpDJ/2MIOrXhX36zPqn'
    'NTGlgygAhPJknfNYAMLwXMrkUpHQ/L0Zkwfv2IZch0LIrUKWPSATdg+c7h+NqkVnSr7r6Jt80YZGgXxN'
    'X+COY9DLYD0fOqVS'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
