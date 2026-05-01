#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 671: Colouring a Loop.

Problem Statement:
    A certain type of flexible tile comes in three different sizes - 1 x 1, 1 x 2,
    and 1 x 3 - and in k different colours. There is an unlimited number of tiles
    available in each combination of size and colour.

    These are used to tile a closed loop of width 2 and length (circumference) n,
    where n is a positive integer, subject to the following conditions:

        - The loop must be fully covered by non-overlapping tiles.
        - It is not permitted for four tiles to have their corners meeting at a
          single point.
        - Adjacent tiles must be of different colours.

    For example, the following is an acceptable tiling of a 2 x 23 loop with k=4
    (blue, green, red and yellow):

    [An image showing an acceptable colouring]

    but the following is not an acceptable tiling, because it violates the "no four
    corners meeting at a point" rule:

    [An image showing an unacceptable colouring]

    Let F_k(n) be the number of ways the 2 x n loop can be tiled subject to these
    rules when k colours are available. (Not all k colours have to be used.) Where
    reflecting horizontally or vertically would give a different tiling, these tilings
    are to be counted separately.

    For example, F_4(3) = 104, F_5(7) = 3327300, and F_6(101) ≡ 75309980 mod 1,000,004,321.

    Find F_10(10,004,003,002,001) mod 1,000,004,321.

URL: https://projecteuler.net/problem=671
"""
from typing import Any

euler_problem: int = 671
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 4, 'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'k': 10, 'n': 10004003002001}, 'answer': None},
    {'category': 'extra', 'input': {'k': 6, 'n': 101}, 'answer': None},
]
encrypted: str = (
    'Zf1lujKYw5EmGjZ0pLwNbHx7NfrVLKwhi/Th3ZuJcyOi7dMByoEIiBnkklrm+4bWPT0kc9hBtdKfKcQo'
    'gZqqJctOsdn0BJlv1C+OdGvslUftCvYMx4sV1pLzg5BFJHgDy7lwnqBt+J8OtcZdOHDAH/d9yy9Y4I7t'
    'moWAqcPgPPcI9LoiriVX5WC98XxH24efJjHaN9NC1ebfGEVodx/Y+pfUkEWJDgepJBXgy0MQfD1joADR'
    'N3cv1qDJLsKUzrpsHA/1CJzn1NNkc25i/BV6m2Rwi7d2jpc/0OA4q2bnRQGpQrrtM0UGE00kkkVBGqoN'
    'o8nSnF+W7KIR4LyjQNuZdd6YQbhHuIRQjpOBCJ8aLUEHKVndskVJ2g8gpE1qJuYCpcA4XhHvZjHyP9JU'
    'FLmFTnqTQMUHg5WDCoeXpnJpbU1/KAolZJ+VrXZmwxe6Do3aPK2aJMWlCGlVqGB7GpIDtitbFklTlW00'
    'I2OUfyslzBR3Nc8JGTsnjhKjV2z9GF6DwcfYct7uYU8RBXTIOCpSf8oAftidzj80dDBLJKNpppbszAA9'
    '8pln4xNtYCfiIVqnuvK3eAzDu29DQwKYUEwXwn8AnK5mWwHgR71pPWxTsef86IQnQA2IC8NR+PF5Dy7N'
    'klmu7DrI/0dbcZEf/hJgXbTeYfAvfZlD/P2C4u0x2YCEDuzxiQevD1zNIpom+1jDvSamEF8xp3unrcH4'
    'u8u+DCi2N/AvxKulW3epDVAqRK7fm3Wx+kNVDOdBL9Zy2/5hGB6AHMWVpCtJyQ3L3uWguWig4nf3tMsC'
    '3NeBoEU1Tl1Vq8URiBC/3CiQ2//i9VY08KwaEr2DdVhJWozA8h0hfalfZOU5oVuwY2cCmFrRhO+tWar2'
    'XcVSrcle8zhJBkbJczWJZbhQv9HRe/fhy/bWkMFa1DN7+Ua2ZYG4u1+Hd3QS0gGCeHf4CWznssG3y6ud'
    'IATNQGwbx0qVDK65v8corJ+6ED2LDY5u6crLPkm0ONK0rmI8hxdhTCYnrr5E8EoBJJ6WbNkUWny1Hi4w'
    'ydi4OHCy5DZXb3wJwUY0gjFnw9BlGGUolVTmPBp2dqd9fEEOcb8F94DxZ0eIqvAlFt9JkRPgnaa6kEBZ'
    'Hllvz54bx4s3WcHO0ovG1xeCVnbc/wpmZoJsHzjjx3SlhV+bLt3Hf4fRkCOwvI8+pbyCUqdbavEE3dF1'
    'pawQ1xW7ZARotn1FACI3oBKSstFctwnhM5GFbf++Owwid5aroa9KlCtItA/QiQAss8f9mBxRnSYQmZhR'
    'ZtsVSgSseb/vhBGlp2ux9MF9rtCKGea31RbIbiO+lfRMsD2q46FOgHPK7a88XND9owOud6EAAOB9LNbZ'
    'vmsWpV3Acylvwq+5He2tZb3KiAodnFKb7WRi2PgTSY21tM2v7iVecJjHp70AZr5HccBIwVyPcjD7r2jO'
    'eKTtkdCll2lp0nZbqgPpRzRbTp+Dz6Zx7zFhSlXd18i3As/kLBG2mwawYL/bkf5OyO3aYJdmSdExZu7p'
    '5/J4omaHQosbMjCIxlg1DvCWN/rwzzO1Tbhf8UM8Ky8TbsJkk9E2l4DXkGlpPX4ksg4NWZt/veZCmes0'
    'TO0u2scOKyIKzdFH6Xlis4951To7e4A22BQtdknwFoCuLHJTqIR/3PeZZyO/owDZNsibxnH11vlPu0O1'
    'FDNwAhOYByawkhD2GzBitSmmx6v2qteoBNjrghjSDhj4AKqzUUSyvg/3SJpD2QDIqPw6YOL65cwxKTbg'
    'Hp8IDqvetXpq6HzxN6SiHc/ZIktW14m7danlmyS8EGT0SfC1XD5fvut+CwITuX3sXvRwANxVAxQEppFP'
    'Q00TTG6KcZVpTzm+EMuRaONXjdZowCaNvvrPDFAkKGLv7HJjAcjX0g0BVbaJfNCmBH0czi0aDuS0uP3O'
    'OcexNDHgTHp3hQBDGXAtrkQ5cHjYVfznvbR72B3fwOAGisc6mwXO0QTnBv3x/5FUyuMjO+PPdyPzoeGl'
    '5CncIL90Rf0LfuhnPeITvRzW6QPdf4oTNPhTTEvuoYOsh+bGmx/QqwYenOiB5U874By/eDkeCUVoLejj'
    '5GIGy5ZE+U/VXAiJeGp25szh6705sg/oTNRVjRNdd0MSTMVowa/PhUPTHq+oFp83pGWuHoXcNSSbGJsN'
    'UBrXYJiw+uApf/F9kdktQWhIQx7mnL2uQbhXTjSwio56929Adq7cKLdGKeEZrIO5PaM6maawX0GLk2kj'
    'o2BlI3LMiXrgUSRiOTZx2YCfClhSKsnKjnY5E5BPyYGRSC317CF4atv6OY/Y8MwqiCrcA2ccMvoAD+Xt'
    'iOJHuUgC660P9Y0TnOuoD1NfT4qveh+7cpAZUV694jALpumHp9+g5PdmHPC7Qu0esKRJu0fj2hMebPyk'
    'ykHvv22NiZ7xTju6YmN3pgXnpjqjItyx0chEuv7O1ZqZ+EqttbcIm1esii2l0RwkkrFqDA8RbuzdW9qF'
    'RHooIVTqgQrS8omcDuqR1NO0utnvTaTBV3+BzZbxO5jvIUTf7rb6BL6tJEHvhKBGGPvlSTM214zMzE3l'
    'gYG3+c/tF9VWQxg24XpLcVsH3Gos7XQ3ZC8q0mfSiq5pHRST+YM9HBX0cYbrUgW82GoWRZkV7P2TYSGw'
    'ICiv/yB6/5pJ0mtnlKbOZjWXoakevIJfhALcGvWFmfUltb7G+qCgKoQL/CUQr7IvE473pwIGMh4/s3Lz'
    'rYrEF3G1emoOdeBWtsgzlOXHQBv43W2Vy2CxbC+zSklwEEfXrefc+UXXiJaTNQ+TyusXYHA8NBEXRwA2'
    'fhdyVkgdBhwjWH5kzx0q4o2ODSje62B7JCp23vf7TIhwLR4h90via3U2Uf6Tk7SEy5iuqhyZbAy6KTXU'
    '66KbEQTj4DpiJVXvzQiiLO+AV8r5WLisx9Wm+/Hl89CL6yigtMUtdhq/eR6IuupXvZ9gf2j6FjrT84cH'
    'SQWV/2gnAsX2LKbo+8fn6KDk0+VeVMkLJJCz/lwivipFD4wMfYjyeywWtZLTBcejn4leiJz5Z8+7Zwqk'
    'VpRiBrlkbNlyLUNvZCrNL/qx9+oYtcvsONDpLXJ23T4sz7AxmEwRJsKR4RBnDZnW8YkN+oLRiVuWtIuy'
    'hS9QNvarWSgAQgnpbSeEryoBiSOwQWo+dNLuSOxYHGP7aq3vY6c5y3p4XOkAtHQNtri2cC1FoJZfHZt6'
    'vHRRAAEsjtj6v+HLgON3bih8dKIaBsFgndGUIiXq6rYA0W8QQHybIVHWVZFQd6kaSz3bgLoa9wnhZv/p'
    'waac3nsgW/16iVfVkRCDsNpB0q9YZ4k3x2ynh/efdJjgcErz1It4beXsxfUII3QUZpY/5GgW3DZ0vwRa'
    'rD+KI2pcd9mZBEXIHPGampqGSaXMdZ2wzUIy8h2wVh4tCYZVXFXJ/DmVkqqUnCNfy69n2XUlAKz/L04Z'
    'rOVn34NM6mx0c11Fb1muC+DrqXcry2lrB9S6qfj+KRK2CtXT21VvnpzGgE3Pv1xHn8qWkwePv3boNrTX'
    '+Yed6yMfiqIfj1joOogU8yWAPwqXZNij8jLDxJtA+GDH/KrnxphBw1WIcXHZUdoy8a09hEdy9DYAx11y'
    'QWmIvPMbUCHvWStCuAKsPRYuUahr+hJ6YKwu2jWJPqCGWt0nvbVAbnxdt1GV2KjNgse8RyFpfpqkkvEO'
    'EnHyJN0l9RZW1vYCid6BD9JxJyaKknI76beyX2FF7UK21CvO0iGZpbHCDKQ3uahB9i3Pd6G2VAxd4L8l'
    'JnUlQsxsVfTLfNLOWgiQxGdsCrfzR+Ax1I/LMycmxh/eOjvTf8V4aripIKNx4neXUsMu8iGCeGxHULgk'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
