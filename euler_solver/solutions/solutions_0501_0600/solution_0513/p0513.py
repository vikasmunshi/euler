#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 513: Integral Median.

Problem Statement:
    ABC is an integral sided triangle with sides a <= b <= c.
    m_C is the median connecting C and the midpoint of AB.
    F(n) is the number of such triangles with c <= n for which m_C has integral length as well.
    F(10) = 3 and F(50) = 165.

    Find F(100000).

URL: https://projecteuler.net/problem=513
"""
from typing import Any

euler_problem: int = 513
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000}, 'answer': None},
]
encrypted: str = (
    'dGV0/SABz95MwRjiA5tHYebYzRAEc4QVvKhAxubLESTXuUKzD4UugXNy0ogMwnru2BvpahRiY4l4M1D0'
    'D2cSzdqwGB0mCTZn/oju82xznTm8ztC0RH9EnzqVzf4B1Neh6V4YcZpDhlvcTNXrbr6QwraFtKsip58B'
    'd8nH/19xI40vRs+RTrN3LPH2CP6gjdun4RQ0003UL++wEJLiYNtQK20Z7y9bFmMPTEGkSl33u8iE6ArM'
    'yjVjmgQU8/WNi8M7QhcOumRCa75QFxOUoeq/0p0xj2GAlehq3Cz06ZgrY0D/3MXOH68SA5OzK7LozGXs'
    '81t0I4cwN6fh0GVtaGl/RfQ5wwnlRI2x6bFq3/XfotgXYcT17nRD4EpsBnN8YQbYzIxGY4PVtOwxlaUl'
    'TCzaZje5+kAdyLpuM9nRCk88suBZFlFDfk+oF8JyMxyiW3u93dJZtc37Do9lQL4BYaeVt51DULlbBnUV'
    'iX9zyq42D3ZndCk+jkK5gcjyFyGsnbDTUXipI0uxKqLTTNJ4jzbpyVlLz1tk8a+s+ciISWPoH9aSmdcP'
    'RHpqX1lTKzvN2CeY8/hWA2Pt8GNjI8/zFuJ3XCypQSNpvqZZVVtWvJpXO+NzMC9BLk0F3Cj79k/RI2CB'
    'i0OvDsllDoWF365W916+IhL+gB7p/Q5BvhRUj0kgVBpQhKfqCnilhp3tBo75h/y6M6gui7SYm4lIJFZv'
    '0erpY+J6FdcnorTIKk0ZoxusIxZlTiLarXKVnMbVW44elWw04liP0eRdfFZpzu5ymPzjj2LXmgycgcFl'
    'wDTMfnikYA55rJbGYz/h5f2p7QAk/bOeZd1kIc4WNa7L2jXCUIY/pWHcGoyLxQPfp/8TzUbo841XMrwU'
    'y1UHx0tK+w+UtblgjD5Nv2ZqGxaFUewMUnU+P7b1SfN2vFTbSLk1I1mHbJLlxWlRBgQ9mzmVNYcNJFlr'
    'ZuvxcAaySTwO7zMqPP+Iql/UkWTcwYubcJc8mBEqBOVW6aYVGGP50BSi4tepgaP06RYq/gJXYVcpFIxt'
    'SEyfcIZWzz6x7Mt2KjtXqAZ1q2Jrf+jf3qzIVftoBkrjxgr9jJoVVGqN0UiDv0gxvAN92t32fUDQcmGz'
    'OZrzkJn1ox3MYzgs7Kb9oY01zZtJsAiEU44ZX+4XYjKfMChwmnwezu46nXj8y7xQ0wl8mgzs/qccqqxR'
    'XweOeOOC4AfJdqeZ8co3TWDbDaysbZvLoEpwENJVVi66TpokVGdmRIMV0SAWis9J9CbgCKEAtkW8RaU/'
    'Ov5JpNIrKNmnuLrsCSDcBXf4B5QK2NU60zhEuqP3OPAQ01f983ptS7RTjME6T/cHB/GCDQtL79FjnXJI'
    '7xePOjEyNeTS8uctJGkj3qzE/cg8KzLMCTYyrzKWI7vItRgSEoBqJ+wl9XU3tf6fipedBptG5NG5g826'
    'W0/EZMah0AqTWYNwLcqHWedDpA9Y1VTTLodl7y6JW1uKQL9TyLXb9tS4I+GlkMwPJiQ/YHPuGSWocNTJ'
    'NZ+i5LdIW73Pdp9vODFTMwiAOuza0jqY4pMg37a3w/ONf8F3kYLOu6Vo1piEFgOqefNJHY6d59TA/O60'
    'G45EXhwHRxxQpnQ3KC7Opxa452UKThxQpvNAYC0orlbQoUDD7WHBv500uP9iR92YhbU6P9nAmJ1yDlFq'
    'XuFpNBAiaHjn93IMjMDEP1jydzcqtYItS2ZSTW5/c9SwKaHcALmqR8YIpPBBQzu17vpKHb/QfJzD6OuK'
    '8oJ3v25G0T3Is415QHg0S0rX18xtvwLHig8z/tXRgKo3Hd+0ZJk0doY6ajnfreRqmDEticrxQVxJ1yOF'
    'UAOtrfydr/nVlQNp7kefBXVeEUE6/Akbr1mltQAS5vOjTshfnJDjEkcLzAm8GJ64KUvBPh3DfQyTTfM4'
    'A1SKpmbGC+EusyKPKhvJnAbQgvUP8Bf9fLHc16FPXlXUL54QAlqQ/Zeubog4YbKQZZO7XQYFbm3ERNII'
    'qNINdoTgB8fsgLzjs0s+9K63H5lCAmWvWkJyVFh/ESGqZC4Wgo+AwQgWLzApmXXRYlekFF5QXmTx91qB'
    '+Wf6md3pg5s4h/Ms72gWdR0zbFZIFF+4z+o5BW/uhfOcFwDGuy+3rr+1S+ZydxlBNV0B95kGBtQ3B/7C'
    'NG6QUhOXMXhQr22uN48feHZueReXQ/EHJ5DmX45qkpZVCkngbIeZNr9o+jW9Dy0d3vENTWteXYfBfIzu'
    'Jwvv0gsfyfm+p4r9ImZla2Q/YaBoKEUHGOmkns3PB54lJ2P0EqFx7cqH2mfOIiQN'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
