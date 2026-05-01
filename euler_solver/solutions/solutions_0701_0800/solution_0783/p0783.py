#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 783: Urns.

Problem Statement:
    Given n and k two positive integers we begin with an urn that contains kn
    white balls. We then proceed through n turns where on each turn k black balls
    are added to the urn and then 2k random balls are removed from the urn.

    We let B_t(n,k) be the number of black balls that are removed on turn t.

    Further define E(n,k) as the expectation of the sum from t=1 to n of
    B_t(n,k)^2.

    You are given E(2,2) = 9.6.

    Find E(10^6,10). Round your answer to the nearest whole number.

URL: https://projecteuler.net/problem=783
"""
from typing import Any

euler_problem: int = 783
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2, 'k': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000, 'k': 10}, 'answer': None},
]
encrypted: str = (
    '2XsKEizXyLBBs+L/jXIyaSseER6TaZjg+vFu6Dbt7hzBc1Xc41JZ33SVz2+xE6pem2NvIP12KGfS/DO0'
    'XA6OP8u+B37H4PGUDnChgMqfLAp5tC401/53M4s4wJQueYENMKqwZdMlqHB8RcUqegWu/tmKVOvFNGH4'
    'bt+TmsUJ2gmYyLKi1W4TIGA402ieJMRN5AhFRXYQ2JkW3GC2m9ZTHr1amd/xCH9eXu8T4P4VaNgaS2xx'
    'IfVdWCNZq1SG7H6wNxKuejaez3JcCQRBvb+EU0mh+0ryvxr6w2u+1k3CvmLIjR0SyUoIczygZXIh0xbE'
    '8Nahi0KMJpd8W46ZMiQh6ifBS8/BKqH/jvEIxZIVi2VVeVhEUSjCKhs53+DcsFZqjfVBuIe72yaoN7fw'
    'fNFkTgCB1uoK5S8wcBaYQuaqfMAyJm4NF5Xcx6DOB5eh+EEEQk5hIbbPRFScmTJnLEY/R+XqNV22wBua'
    'fcPpEswgQAWh6Hl8BMc4kF/qV92sXN9nRCVY6AajOaAOM5h70VgjWjQ55sDVPMtDQRQPrR1Kl3eYGHWi'
    '4jeSb9K4ZnHazV/D1RCFM3m/vyiW5YB81wUzJsK5FOfmFmPerwXcgE6b2WaflvclxsqxYW0Un4yLJT2k'
    'vxljsYp3SILp8YCWAZpEl3UualOjhSTi30FR3TrRaYdO5a5TLw2I1bCPV2aYqcT63UGVsI6rQ1nToqUG'
    'SJRRy5Dr5RlA6rWhrCebdVYz03tXboihXLK7YHZXOdkiD9AbTavQJ8PDN3xkBqxuY6eYzSGk8nyVOgil'
    'UO9GiAhdcevhNuA9FvhjufB2QUloqdM6mFssOD70oGgjv0oVLC0Ta2l0bdNiXKqrxPCP31mvvngzrY37'
    'Fzy8f5qACesBR333rhteLmlWkLGhxj268yMo97/27yL6pUGs1G+wO8LkMTiGmKfC9jzTxsHybk6GANZc'
    '9R0P+uX6Dg2+VonCnE+5C+vdzshlF5I/kfA1V67fAtqbDeZcPVS0jvakorAHObhEzNXzvrEy4UN/haUY'
    '+gpyitA6qNfzm8VXvbyKacL3XLrFNYHDBfpTviPARkA5/+w1JZiIfWO7ykhJTw077lIHCA12U8sGodTl'
    'AUea3TfLVRgpkiq5NCN4RiMWZONETpJqSebi2lps1tpQgUx5P2vBz1jdTs+IHWNC0eJaS4va41TTWdgr'
    'tbW8YuMUAICTuw/cmSNWZaLKip11O04F/89pnG8x0Ots6NidIyPupTnRwq4ZJolnLtdShsXRvgCi3bkm'
    'YnAY1qviPR/Mprx0F7PzNFKgzDznZfNW/i3t6+J2ZxomKJ0v2bVTmk9frqZv6Tr45QZtA8V8KF9S5mZA'
    'DbbVvoYyRs/QwHNSW1ix6TUf4puPDT7luHAxRKw7w7kcUPui7AdDVHQ3yVEBtVftED4bfSgHWtt8XTXk'
    'N1sQrikJ9Mo/RFckQM0DNSGlfAXlO8jaeWOlN/vh6j81j7djhTFJudyydlcw5tXT2fZCvLK6O07cY0wT'
    'TBV9n0fwCW4bn8WskdX5RdjPqxF7VjHKMb0riz0AxpPQ9w4pmtzxwUYf4HTK/aR/tZ7jtAs7WplMYIVv'
    '8cktccASLfHOChh0HmKTevlPupSfzC0sP1uFhacrdtZ30pd8njJJBv5s3LkF6p0NDDC83HGbQFvNG7F1'
    '3tW4U+Yc3Vb761+Ea3SeduyNlwQsQQeDiwz4uWYJF1U8xVIbIUkKGGMMwaU9e6WMbDDsYcIEDyhQLN+b'
    'fqPq/JWKVCqmWrpQ0loWf+Ix1/Cbsuf/BMEJDHkImZLeXrrKaKzgkTohVDrkX6LmLBjwJvVcTBO0GKgV'
    'Zys14eMvsOMZNCEDW0goHbT31G4qOcIlyJIXuj3dWUd3AzllHPEA7HokmKPAbu6v56HMp7yd2d28EdP3'
    'M5CbXh+3id6LYxZQwEt3jWegTLwv07wtaL5CMStHsSyLQHSKGUyj7ixzYnLtJFeu3IiDVBWSZlFycj2k'
    'wxBNpan3s0lMlctvbcazII236v+U6EKLIqUqstPRnsnW0ZDlUeudXZpJ8V52KgTg9H0RkF5b4FSuQbY2'
    'Owleg9hyzqquKWn+XIb60fPRPDHoiLIFC4ySuUjbrCkRvu6DoFLim+GA+e9uW9NLBtaZcQk+ujaiIwcU'
    'FQTwgfjh4s8pRPgsmBqfLttXv9KgKvvj3hGiV9A6X4zEY3r4xYNTJPG5FxTE9VShQ+di2xIBG3z7DJGJ'
    'mDWdBwqK/uAQG1MMaBJ8vuqZeVLoq+PCxUFRxaVLa+PI5XjTeJYNIHe5poECpdoSXUyMt+d4BidGxQZN'
    'GgRQnFFWoA4kBKwl6W6sSMOkjEWK3A8dbX3rFd42CTXZv9yOkbpkeJulle+DE9owBUJm0Ve5ln0D/ErM'
    'gCUM/3GDzdjD6TX+k0zsHCI2nedfgt+7u2h3Sv5D3VEjXWOR6KSUfiKNhCP+3420MgtGk3qe1E5Ghhss'
    'HFWGpyWqsonpfhtA'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
