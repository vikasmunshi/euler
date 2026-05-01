#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 870: Stone Game IV.

Problem Statement:
    Two players play a game with a single pile of stones of initial size n. They take
    stones from the pile in turn, according to the following rules which depend on a
    fixed real number r > 0:

        - In the first turn, the first player may take k stones with 1 ≤ k < n.
        - If a player takes m stones in a turn, then in the next turn the opponent
          may take k stones with 1 ≤ k ≤ floor(r · m).

    Whoever cannot make a legal move loses the game.

    Let L(r) be the set of initial pile sizes n for which the second player has a
    winning strategy. For example,
        L(0.5) = {1},
        L(1) = {1, 2, 4, 8, 16, ...},
        L(2) = {1, 2, 3, 5, 8, ...}.

    A real number q > 0 is a transition value if L(s) is different from L(t) for all
    s < q < t.
    Let T(i) be the i-th transition value. For example,
        T(1) = 1,
        T(2) = 2,
        T(22) ≈ 6.3043478261.

    Find T(123456) and give your answer rounded to 10 digits after the decimal point.

URL: https://projecteuler.net/problem=870
"""
from typing import Any

euler_problem: int = 870
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'i': 123456}, 'answer': None},
]
encrypted: str = (
    'TCAe4LQVgpbmx9zrqexXkAA8x1y9Qtg1jiTXN0fxlm15rmnxZKElY/mqOFIE8wfiqgx2Xd4VeFZVidow'
    'UMVo86p6BiISfQ5FzqmRghi7+2nEV/fiehvd9iw1fgqTm5NBtzORtgywsHQd/JkIrAsbJKRh9oG0kiFl'
    'dcfTvS0zydIGYUPZcvTsFZ9I35eZmD+bwq0LBvmstsWXxFjdzv2R8k6RGzq+xAigqbfTq7++6mGnjflZ'
    'lgh1NIwR5pRoSRHWqy0u7JhI+zCKZZzLGJaWIdjaxBAEFcYmWHqDtmK+srp5R1Rhfs6OrKxsnBlA7LWf'
    'lmq27hwzjOvgmWYb/TpU5vX8PCXxyt1XCxAKYHHV/7Z6R05M7/8VJVJ83Db7cwJFR/UjqaIq+s0uocMg'
    '0Vf78mCaOu0qd5TM1H/LpQPh2mhOiAeF6enwSqlOl+mX9PLrdQEkl9ByIIGrojP5nIAP7KIsoM8cXAM7'
    'estxwI4AIIVDnZ8PXhl3X0f+7s0UOyH5lJqFEQyVOJsB7PfWzcYn+dhovRkHoHWMttqPUeOrLxP8L4GP'
    '+7kZnFya8moVVE+cj8H5U2X5XlQMH/ccZK742ucbvL6dscEBqoqPbb+9kT2Gbf3zYbo1+4hpy1d3NI47'
    'y1GSLNC/POyZQuYVTC7z9RSQRm6TCu4FX5Sd6P9y/0Un2b12doJTBPLWdwyjWO9bz3s5kBMz64WNL6YT'
    'ZKXc8BH7R/G9VKGw+I9OBCXHG5+BH5Jxa5IUy4Myv/DJq8Tf0d99n7J/VeyAlb8rxN4J9ActzdRf09jD'
    '7LRcRF8z2oqVHPi/EpHbq1BSCVj4khXalqlzo9unQmO12xNRPpHPvFvMJjm76P4H8GfYNnr1Ok32GcQd'
    '6pGk2CEiEake1jaTk+wPLNfDSA+HwHaybekhr3gQqikFgRhk8AikVoOByxNBYEqJbaTNjaM+UjijR4WU'
    '2nH9uA6KSliHq5bRREj9nHR+moLbP1OsQL8GpB4QuK8vTIsDavBDw5tBeANC9k5prko1ghSvDQVYE/y5'
    'uAEhCuARSrRO2L3xfnFQwaHFf5KXc90kqg9qXUIGDUWUOrpNB51+0u8LXwgRTt7oUDMJV7J8BwrOGQpC'
    '1Px5/R54474Lk/5QKgxydvjLrCSo/IaUo1V8XlTKUyLLjOio9w6CSWqEO/RDIFxt4HJvUZ+9UPDu0EaB'
    'hij1GiJhvAJOm3DxQ65DjBP5bPbQYz5w3lwBiEa72Dm4HuVa3+qXRXYEBc+Mfb9Y7J16F2gi+bEOi5fo'
    'n2OIe9etWMXDLjeZvfVpEM0wA9hZ/GNGgz935xzuEuFj9RJywr3yJnwMLDbKUKvoxHL76HjbRW3B48cd'
    'kCa6FFKORfdIq1POQv53TlyqDs4aRSwbO+51rZHAHw90a8ZNRZ+togAZmoSveHd6b20WAI/1MSsnlD2H'
    'M/n2cmkWQMjfkBvWbwdveehCZcZJ4IySSGZK31j6CsT4Qk3KfW3owNNUXxCQdg8cTyKdXjm8Zv+wFLLd'
    'AJv9cs3QT8DcBd7O0j5m1aFlkvEOVPTNTXIN8QuH4NMByvoL/JsF+04sNJV5DN8WJKiHohkIGY00mF0n'
    '+FTC4oqGpfu/1m2L2U77rdrBE77KOCx7lZzJdzc+z49ZqGINTpnAMTgiaHZeXYXiEub/ZwJekdnbDL0d'
    'DpNnEq21JsogBh5zdJkOrD5GvO9y7mTnkWHUvvCuplpUxgm8sDDD6wyd5oobTMNnAn9kMCUcXXmsvqrB'
    '2trvxHa0v3LvWwcxCbJWd3K1EcKSVW9Fx3zdsh/wSYQ98puWLkdI71NTzpkqBiM48lPwx8XEyboMF+ZG'
    'XCTWHQHPpimZmYd0RgslPTqQrdwITR4g6wb2miEsCl/zTu8Cp+Zqx4TDSJHNu9fjsGTrwwop2i0+4QSg'
    'XP9+DHQhwtmouBVDAjVWFyn+DVIzlhvWV6vCB02UNE+ZcS/GowSLPVCihAI9PTXOmlz2W05YCfLi1LAu'
    'BVDeRS66DXfsWnJbGYjuCBUEO2dybpt5QF2uG/jBnZbfh4V6rH54VdQpT0TxbLXL1bEAqKtgPL3jNL5H'
    'n0r/9xHKbZvnT7eRapurQH7/p0rlVRVRq5cuLGc3jAGpON9ejtY8wv6Kma4Ih0ViK1wNeZS9ypZPAFXT'
    'ZEyHotnikURsL4xa0kgL5ItRKh8cVgFTdWMiHT/0Ip/aZvhV0h/pgdE5VOoHxrNJnnQQE4XyGEN8F+8M'
    'bsCgSiiVKvklVvw6iqZjFOilkbGkG3re4XZqeFq1mrGLU449msxH+SJ98lLL1GhLSdXpT6TQydNOLHES'
    'PnLt+vHKjl3e5qkBOOa15UWQj47tPwgJSuNDqsV/9EvSANbBJzny9YWp7HDqk44uc4artOKgknNsA9+9'
    'b6f7z/H13/OXuRfjUsAKwjR5Buqtlb/PEalcSEMrCMnwhGQJyXR/KWe2ofXeTqLbnAEUacaNsLE6MRxY'
    'cJl4rcniGoita0YKI1vVJDRxJkpmLMjwR3wKmX2WgFLe4AGvNbtNxNOcdDbDe3dSNpVZMF9oE682hrLu'
    'smVAjXzwhlFd3r/UhHX7prOrjS+97wOcwGhsi13s/DMOUjuUFPNTfz7MS+w4V0CqDohwDpQTawHyT72k'
    'MWigG787OjSKm2hvoAAgZwLBLPrX97NBvxYInkwBUYXOnitOEmoJ5pB/zujNFcg7RedtDUfqKS/5y40P'
    'QbF/Tn5kADfLmjvML13YzPMYpVGLwHlPDOBE93Ea7p+BYp0o3CQ2xV8g2VgNoZcJpEZdvcX5Eqp1Jra2'
    'u31wMZhmUUKervqirjka9VK7//0qZ67/n5WnNXTvn3MmMZ7SyShpVskurwqa55gU+rM/lh50Xb7vdIXD'
    'ZoKeEhQZN1ig1rD/OjeqAW3Cv2yKDanUBoWnZjvWpn7FdYr02j8BlKwJAUOiGu6DuQ1PS9aE11O3DCWl'
    'dvAN/Gu9H+F6YayxgGeGAL9k/mMUWxzXRtg3J3zGZwwz9O9M6O5STf7lXQyWPKpZi4Xw3v7JN6l/qR2t'
    'Be4OZh//WR0kGSC4VSQM1PvCKP9z5TizfSVI44gurzBhccREiH7SwKy5EFxwXb5M/EmKtjvYH++nO1rX'
    'jPsc5bhAxdgV/5CBpVlfK1ReFtwFQyC6DFnCaSg+84MBBJtx5Gi54pkKz07tQDJLMlYhMY15VdHJre4Z'
    'ml2E/JeMMdqat6ntYTRDmpHpwBgtw5jH3+dRuQm55ARqBE3GBou0JxJ/oj0i2kqq'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
