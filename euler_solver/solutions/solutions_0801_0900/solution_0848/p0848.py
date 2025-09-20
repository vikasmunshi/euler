#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 848: Guessing with Sets.

Problem Statement:
    Two players play a game. At the start of the game each player secretly chooses
    an integer; the first player from 1,...,n and the second player from 1,...,m.
    Then they take alternate turns, starting with the first player. The player whose
    turn it is, displays a set of numbers and the other player tells whether their
    secret number is in the set or not. The player to correctly guess a set with a
    single number is the winner and the game ends.

    Let p(m,n) be the winning probability of the first player assuming both players
    play optimally. For example p(1, n) = 1 and p(m, 1) = 1/m.

    You are also given p(7,5) ≈ 0.51428571.

    Find the sum over 0 ≤ i,j ≤ 20 of p(7^i, 5^j) and give your answer rounded to
    8 digits after the decimal point.

URL: https://projecteuler.net/problem=848
"""
from typing import Any

euler_problem: int = 848
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    'jwDDSkbLA7g5RHEKoejfiQkiSgPz08kTZD9ytVhygkPwTxAkgIpo/makF/tPAIuW3yk2Jla0wXLI1cph'
    'jGqCxTivCKaJL+lcK9qUmWHvwodT728PTKp64wW43YKd7nK/Dohzeoe6K8lPZMGBR/79ZV7KR5nc8TC5'
    'X3xUeyk3rSlhxTcq+Y1CzmvhVdvW+BX9nrD5WKhAyFvRNXXpenF2D3icfMwyS8UyKMv105DoQx2NIWuK'
    '8NmBCahcDje0Cu6wJOt7aup9TlvK+rMKcwdYvV6hcudapfu+0eisStUB73HJLVoh5teDlpRGC2JtXze1'
    'nzJb7grIX6rDOzz+IrkkMgrlHafMxa7B5J655WEJ8t/7EJIyNLcNLj0voK3PNPPC5+r5D89HmhI9ejYs'
    'QXncAYK/IVmsz/ogfu7gcWAMDid7WtlhGwxVnmnH+VaDAY5Df48EDGcEiUSfFl1cVV5nhaWRKNEUjnGM'
    'Vv+5mFm0UKAICL2hVEYZP/VZjGOygbBSYzNpygU14zUlSUvABOE5SOcNVPFqGcepuau2nm182edmzkZK'
    'TRn8ma9XUO/mSZ8rpNh1yFSzD66gZpGFuUcwbVNvF7lbcx1vOHxR/UQR3ohgTrckDrC1PtiIsWEpqC8d'
    'iOXMRhYSG+M7UJljZPYVBaBUav5/Y0AHayEPFGIFKOFjmmcNK+r5Sk6EVvdP+xTqZrwLzNqfyQBunTE9'
    'bex66hQYv86ou1fLr3hcnGrF3kFrZuvv7FB0v/jvtgklEXxu5ZkPzbMXm099hxPPIN9ezyR9YsUZUuri'
    'zz67TgrVl5m4Zojm/8JGY6ToNus1GsvC3jBySzxd4L4x9RqHG0kelzoSv3OHylwUpHeDlrD5BGlEAOIH'
    '91EAYuUdJFrTyDMvx95gaL6vF6DM6Qh44joZxbX5U32mmBFmG3fWcKffCepXbRHVUpl4Q83y85eHutb5'
    'A7LbVR3Dqv47HcJcHpVO3YfB9k6m3xDfaCXxBd3s1K5oOcKKDpFUOtsNmwE40O6oDglUIXBYFhmA6APj'
    'scgKGoanzSxN/HuF01Gzc9aHdFipiVIrPhB65E3qim296ZHQN9esmMgkVvZD0GSATJSvTLalnHDP4HWO'
    'yZ5o4FXwWKjlcctHls1f8QndFZocOh0y/sWRxAqFVoLOBMB19eqA7GlGMersCS63woeixiiW8rYoTGPH'
    'BhY4BtJv6J5Nfz1hs8WtIJQ1Euux6qSxcsnCXvDzE3RDc0WDkG2TIyJQhi2bpLEfuuw4CgM0BqaeLJTV'
    'NvBq9hk7miWXxKOvx5uw2fUQzt0fiAMvVfmFNFmkvbLQJuOwqDYuIutwoklQoApjp4/KVdP6440aI5GY'
    'opjOE7YQqvbCF2xOSD5z+sHG5ds67WftLFBJP/NLaBq+fX9ZiKo2o3aNd9F4VN3k388I+UodwkgE5yoq'
    '/YRUCbIOEfee6ZCGb7lCIk3wL9uQveuSBP/LFNtUzsjtbENrNEiB3jUmN9GrLvyFMqVIiwlJdSw3EcbZ'
    'EJlPx8aabaG78CpQSS1It0PzNCJfcNVTzpuK22Ck1wi+yGw1MWMFERZLqFEcqvQD3PUY2Ox8ZAFyar3/'
    'YA4CKAsD/sJo9VejKTz9E4mV2shvTls3H+h95vFHAG02s+ziHqPwAKI1D8AT6+UAQBkUw79HpLuMYxLJ'
    'B4WKU1dSZTdjVs2oenPKKbQEoTZLOKtSP5rI8c+nY1og+HQUOuencLuDWO8AZp74ZhM+VXC+0jlcnNi4'
    'LEzE5tvaxFpoMxyUv42NrzEeMUTJbTwlzCEYGrOaaqieD9b0WeOyTCNabo/jjVMDeb3bcXFgKZ1ufD13'
    'dPV0hyOsXxTkyeX38ffnf8kG8iemORQgwDaRRcnFFIWGOzIp+uFizYt6Kp7KqzTw2TM4Yn8n9K42QJGZ'
    'hsY7CSvqj4RgSKSozns2bvKZm+ljyM93+MFjtKAHW+GeYOKBCUYIHpxQoLI6jInW14OckoXBemg6sW+v'
    'OYg7yi6SKjtbI3e3XMAo0baNfeLOoWSc2W1Cd1oIP4ngSxA18EvGSpJBo3tVBCvYV0PLQj2XfXXzL6hp'
    'lNYQW5UD4CPzkMJFdoQFP+7GdI/0bb/d3T4DJCeLhnjUjZ9gDaROurAkBsy/29btakf+1MtD8zEXmGmC'
    'p80cchySIEgMGGH5/cXIDF1RshMFFqjRgKLQ0H73iIR59agrwSwpm5NNZR08RIHu8sBL1vDCj5lNm9US'
    'Ggg62ybmjhg4WHfJWAKDkGR5vQrVhaCQ1OzA55xUatZa1x3+8QNuNUBx4LWAOqH5GepOSnv273jtH7uv'
    '/hzGR7HBOTae8v7s0FaN8sZBpesCHQgtDh0CbGCUoR9+g/ru95Mt9OHSnZ+BBtHFFp/oInTFjPnCx1Yt'
    'ZiFCRYo8GN4oVW2seRF2hahyz52Ypvncw48RgePioRqBzSETmn9v+S6AFWnvM/cs8kRsczCHdOtiuVGK'
    'RcZl+0ogAAGebMjllEvniLZa9YJ34K9bb5zCtXYvL2tHjgb1PT7i9UlKv54fnIKFM0stD1F02+q5sL8x'
    'edXk9FYaS1LmaJ+TbYXex1k/F81jncLqJg7/RxH3Wbec+8v+TBGQzzxUX+kuPPweNNakCfY09kn4D8gE'
    'diB7kUB1XW+vqzWlqaomQ2tLCdtztDdC2N1/ro1fTI8ScGabp2eVibXzm+2a+JTspdGoRR73D9dIZROU'
    '4jdZyR00nY9AKO8/SuteU8fCWHEuWbpboiyHUyuTysbS8H04tBMWhpvt3ztGLrOKlygLgss//57BCUVE'
    '4lRUhYKJSXjrnsJIhozmVPpx2Cv9Fe27deePYt7Fr5Etca5MOCF9d8S/b91dFSyITwnc687pAkc+AOu1'
    '0TK4J49QX8x6vIGcvDqET9g1uz+OIurre1ww8dVGmLg='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
