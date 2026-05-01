#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 549: Divisibility of Factorials.

Problem Statement:
    The smallest number m such that 10 divides m! is m=5.
    The smallest number m such that 25 divides m! is m=10.

    Let s(n) be the smallest number m such that n divides m!.
    So s(10)=5 and s(25)=10.
    Let S(n) be the sum of s(i) for 2 <= i <= n.
    S(100)=2012.

    Find S(10^8).

URL: https://projecteuler.net/problem=549
"""
from typing import Any

euler_problem: int = 549
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    'oRpdQzxpO+EyAsR+gJ6NknrA2OiWNiPJq11VVJmyxQt1J2aaQKH3RROnjavTMCnzmOKyZa/+dsy89YAH'
    'Sfb6hgb/cqBnwC1dtaOSDJQIhs92Np7s05ihTT6lbjN/PGRF3j8UouCESVG2V32LL8GmWrHFw1jAvMrH'
    'qvyEGnA0F/BofrK0GKnLsDvE1DO836B5ZgGDboqYuhxHBPACv4k6y5TN2Pn15DfuoSGZ0yZ1GNZ59Rb1'
    'TCpEcqy45ZwTvfbpMjEpOZA2rp7K5fyxHIJYj9a5tGpNKl41cJGamK+U+Hr1s6DctjgjRExZJ0AV7U/y'
    'vKZb9OFGZMdh7eV2bULuuxEk3RZ6tbs1F4tGse2dXU6hMwVY9m000GI6/hYZV84UhvXc1mENenqCj8yr'
    'vrHVCMNrcfXiokAFWv1uQW4U7tVWKUtsFJPRTcNnZc0pENVPzsc/FXkZCgU+B1HqgS8GPUkHoWfD9VHN'
    'SndESxyfquHw7Ns3THBl/xsCNc5sGk1WGXiqynn+nyBT1TxvwOjKBHeuIhr0lxPrHLss6vQ396XhV+Dt'
    'yw5pIPBnhdkpBQiRPHONGD4dGNL3GE2E9XxP0dmx+jSLh94XRm0IBP3WjlhhFLdMc9U1nffVsJLvy9Me'
    'nAmH3E4PEPjwg5dQMK9h3tYyPBr9auD9R73LzVceSr1W/sWAwA3Wd+ZZ1JLjh0Zl1nIhs9VSPDrgVd1d'
    'z3TJCc2yK61AB5ZYPKUlNiOWUic5IpjT4+e6jg5+eLJVBuxFJ+o7cEhEJrlulEHcs9UBHakVN+FC3zvi'
    'vTicJM17q5WjSczfjR0UwsyLp5hv2DcCdzT0ZNVPMBQywy0pLJmkSC4GQmZjqTuT/ott06fyGUADptGe'
    'sgpb9zdh/D9+a404Nw6MyTG7hUjnACOa159yXLKVlavDpClRhMhejHLFRLUVqp1F8SVKrI6uUZa500aj'
    'NbIQl3ZcsCrLWb8RhZ9B4oxqFrHtOL5g+JULJskXrAYWOH4aRFKFBaKICeZ8g4MUI/x8/UbtuM9I+2wZ'
    'kOa3ZgW2f8oKqIEHJ8Y1EcRGdxSoQxgpU/SroOOhesn4HwDZ2t1cV+aAvXak/2/rBPTL6VKGWgsS5W6y'
    'wVBasxeD9Ywg/8H1DtONdqtlChVQCf5sfS5x0TsW9YPJbyeSoNp60ReT3SsuelmdDveQTM2G/BwKVCff'
    'S+vXyqaoju7UrKbxC4WuZXTOQW8eOZZIPPzZ9Ir6K6AhYFWVXMdUxJ3kfCpfjfY1zQZTyrL+N6fn16W5'
    'rVG+4WE6Bv9sF7juy0vZP8SXgD2AE7VKjdMbdgtiyswSngRwwOU3MOLj1xAM83hxjzE/0G7FlI4m7LF5'
    'VYynnjFeGmvgDfNHDuwhHPxF+eM5WCSWfrgwMAK7FftnuYyFcPFiFUuX9sq36mLXvYmXAf9KpI2OAgnW'
    'v4HVR8sDcKoF1tPGbUiUvPPVYpW6ebSv3KfzVo38SwCe/zyrTSz3vD4KsB6kQnnSnj7g9n4ljs7xRmtp'
    'bPKaxinyEO5YmhSAbF+g1uy3k3jEIazjRO8mWZ4TK8gVZ+59OPzhVuvc41eykcuW/VUkjG0ul5OOMehK'
    'oedQew4FadaNhFzTgJwQbouH2RyA51ed3hAZ8RR6TLhtoBVNyl/0cfq15kspTsV5pdVAMDVHOqfbAfLm'
    'zobPyFRYz0LnTf3bhsW6BLPbJkxuGnDL+nDWLxsCrhyIGg/tPW8xVsHzhovPocLSwfOzz5XAE6zeVFaE'
    'lBtqlIlGP3mkL3sYbQSZfUd2h4C0QEqKs618I2mlPCtQf3gHfgvM+Ql3L9rEyzXFmHNBIN36mhf7qvJc'
    'dKZmn+Wyl0e+tGAh23ddHClAUZ1NFfFzJZ2t3YvHEtVkNx+XF8gVwl2TLEDM26ZFVRirOSU1AqZLSriL'
    '8+kLD0kcQI6J1LvTprbE2iGknuI6I1hQqqR73tDd8ivteZYfbSaELaSFEQkcmHG+iQQP8FEsoSdgISnE'
    'Y5pxUTiPCcpS4Mvk19Oh67nIebYUyHzmMdiSzOC+K5QFg6IqOLAtw4UMs7P2liVLHqZEICFxEZSStySV'
    'bXdgGlLhBhxROToV1VU5dqD2P3AvqIhyWdzgRJYLV/cCTTZ0VO8DMP++MRz5K9WFB0kyx+90ZYIYU73z'
    'DcNTHDYMbosssaSDo7uIQ0zye9pQR3IRofto96cOexjaQZrWpQNdyIzdvqy6cUVul3RmfyyIpLoB1WCB'
    '+o/lDuq5CPI/Y+myc4u02/03KpGwTfP0NLpedDEqq9iUZeFUSTDzdfd3wvSAFDzSmurQ24UE8wI46rf1'
    'Hoj1nyw88P5bMrHTSsnVcNFw+sg0LcaGPu3dZvHTMVJQv076sLD4vGJq1Q6BroBeCxO5Aw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
