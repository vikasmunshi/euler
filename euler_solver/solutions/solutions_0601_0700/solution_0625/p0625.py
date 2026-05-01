#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 625: Gcd Sum.

Problem Statement:
    G(N) = sum from j=1 to N of sum from i=1 to j of gcd(i, j).
    You are given: G(10) = 122.

    Find G(10^11). Give your answer modulo 998244353.

URL: https://projecteuler.net/problem=625
"""
from typing import Any

euler_problem: int = 625
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000}, 'answer': None},
]
encrypted: str = (
    'fhQquHW8la5OV+j3jbElcewqCnapqCAPl3csuBS5jopMroTLrVodpe8TC/zvAZ0p/Fvy62ad0kjsmeDv'
    'us0O5qMeNj/tLl517CtN80B5spjsUvbXgqz9GW+yXv49RsWFOJrEtI9SqQVGNnEczVOnaJn117M4EOEt'
    'pXbXe91YurX19wYBjdfLa9whocp+G8g5Dea3hSMIgs1PUlVmkE+o6DlVq34VBe66wEY2qhgD/s5ulK5P'
    'CEsfdac397/5tbRGpk8OYz4Or3oWAwn2m+5NZfmJ1UzaJJzyQOB5burGbCwz97km4252otrx9OP/43Ls'
    'pydhTKdL3myMDqPdxT2aOyMY2C8BoG3ngkPWItgOkrHDgInRtsSJWB8YCHHm2yfepZql+gHsUyRsXUIZ'
    'wuAy45puAIMQiZzgQ8gsfDSob2+8Y+/rfa2f483bI4za+TMqs9if4Z7Rez9dL235d+Hjhrs80g/wVSzG'
    'tLIcjT/VP9mWA2r5+ejlZh3TuHgDPOejGabz8I3z0OpJETkswtjWm+jwhhoKpUtknOID4tld9+Aq7Gke'
    'FayfJB3bsgNAI1cfu5F4jM2pn9sIY+hprj4eBlqy2VHGiZ/S3D8KIT9IXuFC67RTkj5Ygk+sAao1UtcE'
    'MIxsRPrhmT3m2VSkYJVJ+hP4CP2HLgznasDILmV8nbrdYYVVlOP/EGxk/5m9djTv/9cVP1ggemBlFgF1'
    '0Gt9ZntSQZ/YtVMgBtZWQ3XoSu0FGhwXoMnfgdi+AiXDU9idQu9gcS96IyBQTVp8MX1VEzRAXe/AaZ4p'
    'TYXsXRPaAIr+/Qrk1Bv90Vmkt4WKpQWjg8FiCm5i0PZboAai5DpgQ9pipGrJOogRYGsgtSJVYOvYJIOK'
    'Idj/YkQbH9Cjr4Un16hwquJ+67luFQekgtaGK0LWNqWr1ohXTKl6mWN6xeJBteVmu/fy1EcIAxALVhFA'
    'BdPAAn02D5pr5uky0pWF2sjDwYN69aQ2Lth5PLkDFpJ8zXfxTedzU7en/24EWjp4b4/G6Zwh8K2Mzrkz'
    'JR2NNfIkT3HU1IsXLKwuohaC0mXPySwkzL1RF+AWouGrjm0vXQ4Qmyxvxs5uaxTfkRyBWdQAVUTH0RM/'
    'KTK6ZLrs9Mh6O11D1bCJOEXDeHX/Q3q1qfCJbvNCgl7oOurlJqSk5+emnxGEudJG6SFI/PXXkfCwtggl'
    'mWVP+w0zyjqYHSsg7/HjfKNFhzOk1mxxKXfoJ2+lVRxQ9LXivOtJvZrYS/7gbrJhJiuWtEtrZckAoz8G'
    'OuI1vWQUTfmLFyZm/JAAbhZ2NGIkw8QzndHmMDpDj6zDWYvodsjmKf1pvvSqn+tfXiRTBCZJzd2JjyEk'
    'viRLMjKQbTC/bVQfSoMdKQbuJZKNuMOtjuryx/fLN09zXnyQf2WBwJlx+WOLcgwMbEYKznfMSHx5KN7/'
    'sFUYp5dPlZopZUnY4qOr/7DP14Ukf9w5MZZh4qwugSM3aEPg4jfuPxtnzQ1j3gL7u846MMuvY/9I6LK1'
    'd1Eao/KcG8gD7jKsoQkntlUW0BkTKMsMs/FJRDUvoY0a9vUfmyTtUtEgU3AMHixqupQm+QL9hC58+0/7'
    'wC18ReBp8L609lIFfk0dAAc5SSiq6YgyOxjKVAjQ1w9Ana6gI9x/q2bncwIhnUBV9Kvo+tD84NlsE8SE'
    '2QsGmbxd6O8jS/7EzrX3gAdLJQVbx8tFPZTaj4ewG1KDLhDrApJ+UV+rUqJGsNx/oX5vqwV8VAHXrcVf'
    'crkVLhLstLMOYy1+Ull4biOSjAE4IwWcNdP1vpN0oW7Kg59GBsG6n62NRwmybP0O3/5VEH7cNoM79Mwx'
    'kmWMG4V8QjT6myECzRmss9Jf91hOOKLA6WTWVA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
