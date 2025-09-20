#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 555: McCarthy 91 Function.

Problem Statement:
    The McCarthy 91 function is defined as follows:
        M_91(n) =
            n - 10 if n > 100
            M_91(M_91(n + 11)) if 0 <= n <= 100

    We can generalize this definition by abstracting away the constants into
    new variables:
        M_m,k,s(n) =
            n - s if n > m
            M_m,k,s(M_m,k,s(n + k)) if 0 <= n <= m

    This way, we have M_91 = M_100,11,10.

    Let F_m,k,s be the set of fixed points of M_m,k,s. That is,
        F_m,k,s = { n in N | M_m,k,s(n) = n }

    For example, the only fixed point of M_91 is n = 91. In other words,
    F_100,11,10 = {91}.

    Now, define SF(m,k,s) as the sum of the elements in F_m,k,s and let
    S(p,m) = sum of SF(m,k,s) for 1 <= s < k <= p.

    For example, S(10, 10) = 225 and S(1000, 1000) = 208724467.

    Find S(10^6, 10^6).

URL: https://projecteuler.net/problem=555
"""
from typing import Any

euler_problem: int = 555
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'p': 10, 'm': 10}, 'answer': None},
    {'category': 'main', 'input': {'p': 1000000, 'm': 1000000}, 'answer': None},
]
encrypted: str = (
    '6eSlKXw04VTn5jH22eyJjmrp14/kaG12ImRUx7bEbp9mewhuRBfiDWQk53bzrhKH1f8B0Qpp7EqskV/Y'
    '80UTP6ep7ilt+w66yJ46pX0U9JnFp4Vyqo7jKgThgrb28ov9C84E8i+CeJSfiPRj4a2UFn+1raXvunLS'
    'lh0VqKlxKVY8SxXPmdcg43mcjIwNECgJZnmefpXgFCRhNc4ddpeZwwRBdbcs6wVk5rCjCn6AdBGAnyrf'
    'xlVNC2eNQZhQrHNjzQ9ezgcGygcfiQ/lRLPAo2nfX3ft8ZkTeNTEN1i5S1XcPeQhQjHKALi6honVhoFG'
    'CKbdgQ5yfLg8zHc3ybDoJIRCtkjJY1jrA9Q3x31RQkxhesVzQC6wlV8cqCplDtehCK4AVmzrrpm/uyvK'
    '33039N89CwiSvj6MvyDssPe/oTgzX72QOTTaqqgjOJMxJbAwLqc/z/wseld8JVHQpf2I8LO1Vdn+hTzK'
    'UQLr+DrTce1W89hxAVbr5UG/5TsJYsPKul/d+anGhDNBb/gjRZis3LwKPJgWxRFyEc8up/9zATpDGGIe'
    'TonZRi6w+cqCVnt/7pEewj6x3BKXz68mYvJF1qhNtpk5Kzp3/2xDWATakBxqFNVgU653s0xqsEwIxLSV'
    'JS1p5BkUK+ymMgglvmIj5JGDl173vYAbtHj5yhoP6uDd8S0kwkELfX0NldM+CkxdLwJvGkX5ceuSXsG5'
    't58xrt18RMwkzFvMTgt6KoYMPIgOBRUFtZrOQ6YF3MjQ4UNTkOiQ6Afde9oXgKgkKe3B71Xkn1tQiiSj'
    'FjdU4kNFzwarQjnd4SC+toIDf5BlhZ196PF9ia1/9M2QtO2TE+1XF/tYopgKMtX62UXAkxSt+Q02xFQs'
    'nWHWcVrKDV1bC9gIBT621+nvloO2gudJ2zfzDqG14R+/FmwleUoK5W74RQSYWN4bM3m8BbkfyUZb0+ZS'
    'zzJfXNqJD29rSzC0Li0K7pzsmJpN7s2NldJ+hY3LI3q0HomZGL6LkLusHmMkDFdYQsD1L/TNq3NpNzV6'
    'MGCCXXmKMmv581x7FQu29P0votZ5WIibhDoxsqMeNg6qcorktuGVr5LUVTTZn+H9nCi/PgduJweKR5HS'
    'A7dIi7zw9DOa19/7bF0n3+bGTcH1qaeHk0xBgdFheZarXl9vJTJ89T5lT3o32E5SwVUTaxjODDziGInJ'
    'dcaJWiiHGCGSbtuDXRFtKWMZSUEpskT+AVJkSY+2T9pmFjXpG4HNdIwoknVZ2uXrWVJzj9nHwj4m2Dtf'
    'JWJNC5pBO1tPeo36Iy1DoN67SpAqHOPJZ8lxPliPyCa/0T/gdKT126N59R4OkOp92T0b7Fb9qo1CBEfk'
    'R8Xv0uhWrwv3lV559OXtkM2hl93FjvDzo5b9FACYGt3lf4WNWNLNH6MATX/yxJVgmOi+lNjHp01El51D'
    'O0yCkMw7c22FpdyRo51sKLz3PKwB5Knwg1bzQVbfWrdX6TQRJ0JhDbgScnYn5bCEsXvwMTgDQT3krSd5'
    'LgUpbQphlzdZiOnzM9TW9udjbKfIa1yER2v0vHxw3R3ywtslso67j+iyUhfNPxRBwfobVxRpPuWBoCOD'
    'LiIeFDU5E3v/E256G+t5RKJZeOkIyOpjkMesTFZZtjrHj7h9MriISF5eFUMrO2V+ZObQZ4rk1Z2Sc6gO'
    '9rJbQLNsX2BTsWb+6SVvJ2gO2wweuPT97F8akLgXlEsxeiqXo1XE+99W5bxaIqlZ3ID3IYAr93Oo00Xu'
    'RRPZwYChSCLzvmRiqEIN/rLCIjLYYsRN3ntWSP3Trl/0nyEuPTKz5WyALdyE6vdvqhGLVhICycIVP+y5'
    'HRqyhGahYUi9kdnjne8RCyjNtbX1l9bpZL8+SH0oUOxvezUEVdu5erXLTRd887W9Ic0aQHrilqz/GI4e'
    'ONAoBl+vzZ5ZPthfiLoXgJ7u3x4cjWfBr+sJ5JKX034i663SffOJwuvIErGc1YeXZ6AQRNT6mviBBd9A'
    'KVfxOCY4I18F92XaCp+wG5vE1hmawjnRnvFbaftL6GA3h7zw3pxWWDLRRsEOFWrdWcEQayDwnw4sKxU5'
    'JeK10Z7lAx2uvY7IwvXbNtO/elCe0pqxieY5z7SsfOqUwYa1y+k9wnV74UHrYWWLZXA2UqFnSwehtcne'
    'vsKhAWaMbjDcDLqtTBuJ932CyAQxDpXYOlX91FZLgdjJ1YvmLz2i0nJU2kO7ULwrtL58uo7ooTM0LBSD'
    'abvir0yWuVXCsX6VyNW8I4/LSZvyQkBVT/k07oxlFgrDmGkYKQbqmv6MUitGnrCz1pe0b3PMNOYUV3Qj'
    '2MNVuMlRojQoCV7cKezSvEWjo3M94bLvHlFhpavL+WwuQmp49CBnJk5QUMjaa6JcJbE76CbCFDshdMMI'
    '6eXirUAbwqWHwzMt86Hjxu5O8acMKar0v/aHSQn5Y6vhcdQu8rL4fZcKushN2f87INiexjFGb3XyYRAO'
    '2R3iR/XFMN5IrMREuR1OfOGyVFaHRmpkrqzIY1J2/pzNQQMxssg0hTEoLJW3S5oyakVCjs4PIMfE2sZR'
    'oLY2foNnncY645Nw8X5mS3nZhT1kyy8qNjAfjM/BGCfbqoG2ZKClB7oiP5SAVZ91wQpfAUxjAO1t73Li'
    'TYcEdUfclJiXY6aLc+mPR+38IHPpQJhw7kQU38Ag4pgtjlcKmc6zVPmFeP3zGTL8lppWyWP65ZKFL4LO'
    'DkQHj/96KyTP/sQW+UKv3lKKpkJDUcxFKKDzfDMwjORrmNxv1ylqU5EP4rfyEF6xaTg08TdqeuKY0+M+'
    'jMcOF3iNeKYHoPMQkkMoqzXn3/MJ/QHPrJkpDWCd1J33MKAExCvhYw/XVRzH8TARKnJT5r2I6b3HJuGD'
    '4rOyIwPOoFB+VLEMXrcCRVUiQGmBIQ/Ms84cdJdBrRxpsUBzVdd/lLksFSdNDZKs'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
