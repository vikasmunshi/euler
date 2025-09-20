#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 747: Triangular Pizza.

Problem Statement:
    Mamma Triangolo baked a triangular pizza. She wants to cut the pizza into n pieces.
    She first chooses a point P in the interior (not boundary) of the triangle pizza,
    and then performs n cuts, which all start from P and extend straight to the boundary
    of the pizza so that the n pieces are all triangles and all have the same area.

    Let ψ(n) be the number of different ways for Mamma Triangolo to cut the pizza,
    subject to the constraints.
    For example, ψ(3)=7.

    Also ψ(6)=34, and ψ(10)=90.

    Let Ψ(m) = sum of ψ(n) for n=3 to m.
    You are given Ψ(10)=345 and Ψ(1000)=172166601.

    Find Ψ(10^8). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=747
"""
from typing import Any

euler_problem: int = 747
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '1CZLIXdv3ywfhUqtwRl/OJkSG92cReNoICgvdHoFZ/hu4TEM6UerxGkw/p5RHCjlelzngh68GcKB05Eu'
    'F75dX2hiUt/iWLBxZ5SjzZD7gQR6hwV3l2tWJ8oc774/5PvbxVFehVJ4rDfRubSgPygPBU56iV3TgMgC'
    'S+6ixjoU3aSZRG08wze91liTsoI6zJsxSHtIc7HZXkFa6xdfHl4NCJktYFNgJJgUMQDX4ZvTwBeoa86j'
    '4hW/0CKBu8M6+f32l9Li5zs05yjuL8YvuiX7LTHlLG5f3BIX+YSzL+WiBrxDpGgP84J6zbYzPLqj4GBl'
    'Y+bYuD6NRklagSa/ylmr4rK2ZTxaIF9J1khjxSemXmBLgTC/OvooiabjvyOCs5doVj9fbpntGFJdrCBL'
    'TV6CQS30mV8/qCpmjMxbSPSH08e5YY9YyiR4zv3pxu3lS6C7VEC5rSu7uuYcLKCjt2yYFAPdC/QBIuqF'
    'w4cBORPuGdd7sv/rvYFpF1JbWG73lmtsL2NvOr8lnwt/hiwM2nZoQSz8IDWAn3w2QC5zqSR4l9EIVhK+'
    'SmuJBL+AX+JvvhNMpZb0Gq0kBLyPvLdQorhzZmaEmZbZc0PAXOG5vp2iq2dL6c8KTdQTtr5hO9GEPkFL'
    'UU0eW4P9+w/omRP+6tU/9jxdFKl2vVVLBwoTxKMvvfV8c8OYRPRpDYFVTWp3qAxOf4O/PgJGRCNedIl6'
    'EfHY7yUbelLzcMJX732BXoZdoLJsz7gPz28/AZzWqxmzoS7JDehLviKWCTP3dfgFpKcws0P95gvR1TM+'
    'xFYeE5yxIbIkMRc8z68YbYthf/T4JWFwyoxs5vJlfAj6ynZPygBO1WdagfW0P5hoT4bgNAKq/sHzxM6A'
    'c6Qu8LeCdjkobnQnMs69BionA8Hm07OGR/FjRubkpK604X/fOCKQY8oMCNlOALwzT+5X8bHB5q+WdVP6'
    '3Md89YU3TZApYUSLmi4OvbJBhEcBMJtnxF5mc44KR9bvE6z8en6FXPT+NK9Ozv+mw5lxliqPChUIKWEw'
    'iGjlyuNl1hcLV+AT/XfFa7KpLKL/nQCjYTira6CXZI4iZh0+5l9js51ywj16FZpxcjcBrdJqyVuRgipD'
    'V5Q7LsHxTZ5bitzbNbE8FGxSca8tjIvlw3wBoxIqbEpfnVo+5SX/ZJsNdxeibyuY/CXMwNjuxKuGr4dz'
    '1TY5hlU3Z2g4afvsE0mFkri6/z6kbhWg3mUXVsoraYJKKuFF5To9/BjEggVV20adLb9/9wHmkUjVEHKQ'
    '1qQAEzc8NL2ves39QpUQJDNGbUTdGSwHXTz59hrAnefvsjZV2u8Ou5zxUQdRyVvlASDb6FCP3+UASAgo'
    'wdmLIAVyWWLVw0LvUeWwGcgGy9YeB4g6SDCs+jMIu+vJ4XlKFSVF3hAubDA5hp0I30IFruXfv/iNwlLP'
    '1lhJEDjVga1rr3RKvOJITtgPB4qbk5JPX048NNYUvGbTSASH26ytx+4FLZA4LwWU8IUqxICkg55pCiWd'
    'odzbngABCP+WNp5l2EhsbdgY+Ef4NpKologMnQRTPaOHI0Iq6461y48Iicstpzh8j3SL8LbI7/WO7Gm7'
    '5Lq3Cd7ab/i81J2PeyURtKKmoHCNuVhzFCsCD2cdLd3u0P+r4aCQ2mYCIu+ENqBB9svC4n3Dtlj8LUzo'
    '+ATMhL0wjVoSY1yjWp6IO6yIdmJRISqOBEq0mgGVM2Q627QX7lW6yKJmyi1Y1t7AArC8OxCyse7QjnPw'
    'LLBtm9XfQFb1oGAY4G0RKyQIvv2KwpK4Xz27uchf1rYcLptz8AmgJxJd2TbsiRsg9zRWy2N53TUcJis2'
    '8CJcVzEcRiI+M+qCYmRGwdXd4S1+x9MRDfSyoKAyJBR7EpniBklGP3O1utH8qnpmWYhQsjRln4RdlqXX'
    'gZ5EVxgVd/MzPDIKCeXqhE6HcuiyWf1BKbf+6E3m/03yHTWV8O1FsXlphF169PKrq07p0WhsoJLCmNu7'
    'WlwmyvvOxGic8f6NwwkIosx1v64GNEqjmrfVWopG2rQAolnpfo5r5904GLkB9wh5JY+tGlZCuuRkTbTu'
    'U4UnobhOxkgeu8fFLkGeRdLf1HA1byLHrZf9mzN9KepBr5quBvoNY9v+FWcfDwC65VGQyxlMUca+dPKC'
    'E/Lx3Z6+tZgAuS6BUZSFcC6BZyBcWnBpHMcgbslwWKDKhbuvVyTZsB5X5pVrP2GmU9qzuFOW+/Eyv/mG'
    'ULgzRsTcY1Mo5Sz//pOaHF2OSfyDTmvVA+YLwNpzrZ6Oq8Ox6lqWZ54qiJ80N/eb9kqBC/NBfjcopdnW'
    'CWtu0Oo734Tpoz6lI8tsB9kQzGGlF9il7wx+DaA8asNI2FocyDrdWn4ElA5VLrmOOwcfpOz+VQgmGjqX'
    'K7K3Xx3hsxRGZlqjpM3A4i1qe9fpqisqOlLp55CZPTTy9eRH5c1e2ECVzjan0+RgUNmw4/noNOaBU31c'
    '/Q8xCniC8qLw7UCRCkF8ppyIA/JtnJh9DSnOexc7Z6WbleceJj7wCvBAK3mN3f/LZC5ki3O7l8lNyu66'
    'LguXltIcsZIhBuCuCb0OAP2srfRadrSIYUZj+Fh9nUWx/8vmHIi9HTuZamBmdFjrb8QX9EWIxuMrqrHL'
    'Yd9ClW1hXQjXuliMmud+HDIuf4AD8mBAsTCybRyNeFsFxHHglGkbVrpU7jAjnt7dR0Zml+unhxhgB9Gy'
    'BuKU4wp9CivhqrFlERJs1qoTMJIkJ4DVOzN7yzYU1YfrQsSGqBQZ6mhXWFO3rQDWQoaJ/5xXrXw91q2q'
    'DEQhNrWhIIajhpeaDGLwP+aStx5g/E+2xrCIsg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
