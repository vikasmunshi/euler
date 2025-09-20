#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 389: Platonic Dice.

Problem Statement:
    An unbiased single 4-sided die is thrown and its value, T, is noted.
    T unbiased 6-sided dice are thrown and their scores are added together.
    The sum, C, is noted.
    C unbiased 8-sided dice are thrown and their scores are added together.
    The sum, O, is noted.
    O unbiased 12-sided dice are thrown and their scores are added together.
    The sum, D, is noted.
    D unbiased 20-sided dice are thrown and their scores are added together.
    The sum, I, is noted.
    Find the variance of I, and give your answer rounded to 4 decimal places.

URL: https://projecteuler.net/problem=389
"""
from typing import Any

euler_problem: int = 389
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '3SwhxjAeX5PGxu0W35aPlxiI9LtZmYIejyO1ztSrzl2jydAAryG1/fr8GDbMmSMAg4M1e72ruJMdDg80'
    '5QLjhSwA+PJrnjX21w2EMqdFT418Vbrs/SHIcmwtjovQ62WTuYlkh6up5Ae5DeULj86F8BtZJypjEZNM'
    'JtkZj15V8ITZUHF6yeTntOxCHA/oZb1S9uYUwTyBRgQ8gyLXVjDj1aS15aZld6eS4BFbjLq5b/GB/5I1'
    'Bu6MXaWSkB6/Wkzq5jOEY47CayYgKp4bxv7hu25gays7/1S37G10SBXX38hfpR3yDQRUAY0G9R2iWYWA'
    'APN7jRPtzmjpJA2AUSLkaMrSuajzdMtfvrkrzb748iN3w/4TSmKMP+ZEvAlXc0YIg3FFvFcn8fLlZbQP'
    'lABOuXZgAzCr4vXYhTBRSX5s+TCQCKCiW0xDuNbjsS75j5f58R671M8bLkuVwr+2vLtSoacHEVt18rEb'
    'leVXRG4fD1g3BHmg4+EHlRWAgQZPS42exGBDLBq+2nTCLr9GeFBEK3gLznHyHakjVTVecUrUR5a1ouhy'
    'B2+OFSVMpLgVkmiC+1mpE9KO6v70bB683y+KM2sMJw3n+S/a6qpA6vVTAdtkN+9YpYNkkvOynmZ8eOf5'
    'D3cN3kRqlxS+GAWV19MXrYgzO8pB0Nn8LGc/9Rqm2yoxnpNlmAIflcKkXLjL2kPso4OIgqCMfBWaSRvW'
    'cBTZgZbl6DWKIeExBQY3blkt/wAQ8XKUetLo/q9XiUdYdKDQ0IJqNSPSVzfY+iOiOfoDXHfiekn6VCCd'
    'H5BA46q10d3ozbDP3rrfGS5m56eRPDFlocnnEvvKJUtt4ybvh9Bn8PQdYVudIdl9qUJpWmDR/AEFe5p3'
    'cT4ECDVe22imBIS7SyJ6iQtz3zWtDl781lvtLpriC1mgxMKj1vOzmJveTQwITa38BBIbaLe3LYWBNP4x'
    'RoxD+/Fl7nIWyqys8wgPdCLyUOnWf8Km2nXUCrM3dTrllSp2A036L4q5caBQ7LlcNkvWN6VLrkuZGtIP'
    'Uoq1YUJtEQJ6jkc9vOQSV+WlGZENKPTPDE+j4aOXarN7AV1v3ix/B7Qomdal10d2qMuyDYcuZ4/ZobPJ'
    'JyzfxHoMkbOaOGzc+33X6f8QmYX73jk7Py5naY8V4yRpPBsIcEI4J/+qOWeEg0BdRK7xcoEw/u1BFnbs'
    'sD47huoDaTzbrsHrUN6BbvzXGf6Pm6QlToIVOAztZ/GO0NYni7lYskzUjNmQMEr55LnxIpy24BRzt4+y'
    'qzBbTqPLS36DsXotj6wqy0I/Z2UdUW4HQFGNzBtQiEB8P7hvtPCaJfjKGID5dwrI1bESV89z7y484HAS'
    'I70MT5BG6KKEkWnEFkMh6fu8AkJyaq9UWsUU786FUjKkerTJZNS2WlSrcUSAz3e7OESTrtnbeKY/82OM'
    'UdfRJaja5JaPKt1orImJg4lcaPnVoHqwhA5hk1KiQlW3kOiJICo3z2ui7U4a5iFKfUwzHXe6fT0DGl9G'
    'bpMq3JUEgCH/bdbdjmDHlxbpK8+jCfMR8w/MgP/Sd9DaH3lfSVTTyWIPXbr/OCj0neTXf8Q5oqXj3g3+'
    'hsXNvSOViqL5rrOsVTEEbTUEjnCjaAT24psUFj8JntjtDTlQC0tV9W0sCejxYDcwPDWAB1kGfOsdk4xR'
    'JKNf6IhLlvS5Ab7Q5HPcILBwQaZIbPY+KJx+xfoDU5iyVtwDvWrXAtCeR6yM6mTLhzwRqPk8mzMAV4u4'
    'BRVg9P0pnkrBCczGduwBxlRW/KDhLrvM8kVMHxafHDrmiw1rYhSWOMCelbZkoKBn9yaesS7Hh28/qaK4'
    'iImCSDFKsesYKC03wcWZxW9/9UkbtJ2eSfYDyramdsYaN40rLFKQ7LAKqA4Zlj38DkbnrhvW7P+XQOsc'
    '4K8eSi/7RIdXUOLrgxpdZ9q/vxuBbIJg4VM8oLCysfum41iNk3Q6K/Sx0kDuh2q0jx7LR7T0tCnE/GV0'
    'jp2OsS7fl6EBtJLxh9T8I8iyW5BXHi5hmQQxmYSno5gMzGMdWNgmO748F0K/f5WRPT46yJasgTC1swyA'
    'dwdU7B8u7MUEZwkCe+ZbOW1X+I0C7BvrCTdImdtRMsZeGtoixH25fwSQ4YT7BUx0R/87vCrr/iyBI/mW'
    '+Cv4v/oKPHwhQ5iqP/K/IR31W9lghrQ/3k5iax2JCS5D8jLMMKeOzV9VeM+kQSs5QavE6kFqLsNc+ICh'
    'o5Ble2y1I3VXZIeH/UBb3VXnJGGbuDfHdGvpFcwcJAeltcLusKCUasOvIlDVrWQTw3OWkawZIPQZbLcn'
    'tHHUD3NU+mmQLp2qCnSts7TsWvNV1qppL/+A4v4aveh+FVvWHcyw+7I3JpBP27Aw0cEyRbjVGJOSmY19'
    'U4dQVM5TXVqxNPPD2WcWCXCpuEC6MmY8reAF450mKheekOV3UaR8uNBPtRmYpbHrybEnrYmPqWCEDMul'
    'p9Uqoxq8DTmKw6Xh'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
