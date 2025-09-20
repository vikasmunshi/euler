#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 385: Ellipses Inside Triangles.

Problem Statement:
    For any triangle T in the plane there is a unique ellipse of largest area
    that is completely inside T.

    For a given n, consider triangles T such that:
    - the vertices of T have integer coordinates with absolute value <= n, and
    - the foci of the largest-area ellipse inside T are (sqrt(13),0) and
      (-sqrt(13),0).
    Let A(n) be the sum of the areas of all such triangles.

    For example, if n = 8 there are two such triangles. Their vertices are
    (-4,-3), (-4,3), (8,0) and (4,3), (4,-3), (-8,0), and the area of each is 36.
    Thus A(8) = 36 + 36 = 72.

    It can be verified that A(10) = 252, A(100) = 34632 and A(1000) = 3529008.

    Find A(1,000,000,000).

    The foci of an ellipse are two points A and B such that for every point P on
    the ellipse boundary, AP + PB is constant.

URL: https://projecteuler.net/problem=385
"""
from typing import Any

euler_problem: int = 385
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 8}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000}, 'answer': None},
]
encrypted: str = (
    'ttttC66XU6XYAP6iMDeEJnMbZJIYUP8lzV1A2BEUpNE89LYIluuVr4tCTdarJEG/j6bG3I23g1F0Z9AK'
    'SsPqnpSx+0EGzchfnvwhvfHZjDp0qBT2uWvfwehdnaYeiQYGFTC2WdJAi7vP9/ZuGUB1839NoBASp9Gh'
    'yPwX7pOgeaTk/hHQ7+Z8Z16x16ywwFg/OHq82JSkWBtXlkbhJQHh89eXS4je7a5t24hk/ZmT5nQSVyg+'
    'wlXvFOflIfvVo35r9aZdeAZwpWFtcZy7cqx2UU4xslGakovJkwZe+NYp7CLaEGZ9yO/nksteA940MHFK'
    '2BP/qqIXRBdXBzkP6s3sTKz+PadXXAUwyGkG/9lY8oV5+Rx7mPbj5r9HiQb6VT09mGQETUq2fSSEmQmC'
    'FEdq19iUXKkOcr/LBgTavIGI/lCUWV5OCeCvfDkbw+EE3p2ztH/+ns/LH3lCgz0uIeDKa8WLhA+747zH'
    'yTjp2O4v7N5PQFrVIbUBKFQUAecCywYY2s5K3p1Uce4nOrqNon3EgxGpWtuJPl+GcGn8ykuw7ayJe+PD'
    'OXkhZQhndv9nKcr5C82LmZm2r4n7kWCvF8rdPpN4rIO3qoadLPhs+BWv2mj49HWgCeYMh6Nwt0JNoHt9'
    'DDZbOvM+vQnh+GpSr06ZlP41plku2z8gxq0oLShKMnt65YXgcOXESTFpa5WxUwukLAcSebtTRwLXGTzg'
    'yht3PB0YSTYfoo1PSMpPkNeRheK/7Tp1PxwtKS+2doHNqDlvq+LgKTUz9+ND993dL8EB0b8BmgmbZaxP'
    'bb7vk5ALsGwDFvWxgQHxscZh9MnsCyuMa7me3UAbfwaZ+T5EQG9GldmC/X5Ue8hTFALWBU2sL2S9IROL'
    'jQA0cW3eSukjuwEvaN2KqfctqByM4XL/AgwcXXGXfb6Y46qS+KOoR31nL+F2aQROz1q/RIFFUhyPfzcz'
    '8L0c9Qe18BD5bTc9+LEnWKAK8mXLN2sCRCfKrOYnve0gWar35ORaLFE6Nv2iBBDKVqK/hLLVfeJZu7hh'
    'POtmD5LaKzJgU6IiJ7ssj5f6DNcAI8ozF97a4NavHyEzT0LbRqvqIBuMjW2wFTG+41RRitOR9N+bvHnd'
    'Q8VT6exBZ1x1PO0aiEwZpPZoUh4oxX857J7nJPAr35krteZJXllFMdFYmXhq2B9BpiKequH0KFM4UuDI'
    'AoSjcsY9R6vEH75Dfe4f9WQTEX3tOVpUEcTXPYlL99P751kDTeO/IrvsR2hVspztx3UBUZI6xqqJ07fi'
    '63Fx9Nbj/u1xKWncewXEzxYCRMujXaczMlG9pGPekH9rna7RohLZRWuKsh08mXrueApXdZT6qKWnJB0l'
    '5EIz2IFv92YANta9wVOCs2BCyMboiR3wl3epQuXhaMFzz1yU9mP0roUKXqOANuueMHuYRjVGKKcAjBDi'
    'OnfTWOq4uthxQESjZhxUJ/5AoUaMKj87xnvvuKL07lwkiadxq11oFqHxRsIO9+Fg83DZvGfP90w6bm9w'
    'Zj9XMoPIMxqviBbNCSWa+7UvkQCbS4oYbVem89be7qOVI5ql8TBn+GfH9/h7Zgnkyu7raTdXOjOYCSdE'
    'JnUu2VXw4lTHBopZLuypC6DQWCUE0o0nWLYs8dR+pxQLpUY8D5PYN7JlR16BwjdoxxJNkRDWZickmbZ9'
    'gWAzEzzbf0LGR/cy3oQLRWoxSAk0ruUcTGAtGaiP6dRBWZO6f7+VxDwWAeQChe3EgmWiUrByPAAYWi9I'
    'ofyAO+Wk4O5xJtau/Pz0P5OYK7sKBV2YTk8NUtkobHCI3U7JCbUQrUONqvAl4zwLrMjQq4tS2yG6FclF'
    'nryxoGUOcELKb7bbcuS1Srl0Pcj7xWWXxC4awENApHD8HKtAJNLZCECpv3lx7Tkgt8fDGUARH09bo61o'
    'Q9nMRniojAKzrY2tsX1UtJ3KHyktyo4pbTUdcTMoXosWBceYgDAIm0bUvPVoxxYqQwjCwuiIPCiiWCPG'
    'OA9FBo0uka0nmewSOf7l/Mzg+sLUPMqbHPZ+kIfMJsA/xJRjD9eAWKDUMvo/HtXUyOSnF+LvF4RS2VBO'
    'XAVUjze7bW42uuxB3ggRlzIfhVHGBVj9T+g9VuR3pR89XBy9liEcmgtcle9TgBbsXfiUoWgtAXlY7jn5'
    'oKGD/idWwqmFd7FxFOQhB3aZjgrjqeobejAjnjGVlAUnH/4BEinooiLENDVlCkp5L+rI44efPe0Rs/Hw'
    'DovU3qE5mbqCDj86yBEVcnjqI+g+6VgmFc8FPDlboqBsEMrG5HGcfWotX73qAa682qjwr0NsINH9mKQY'
    'xfGHw2pyadyP9qnHeqiLK8VAplglS6RYfrU//8olbObiOAyZfrvT8Vr5QfArVCZVR/VnX3cteCUYavTH'
    'eIOGstWHnqGdoxMjKsWftyP5Rkgk3BN6YmzZ8Y4oWuC2QwVHBz3Xxg0kjTM+btKsu3AhOWbPjIvtrE8l'
    'a4m1Oe4vu9W/ttPVEWICGB5V1/gZHoYyfuiANymq6dzDkIUnKPsRkJM6sFMtiWQuDm2olq5+0AS5SiQJ'
    'bhpMpY+W/tfUinq1VkrEcan+DmXuE/7aV97QDiyRPAu1GvvMIGHTp6xrOytZN2ACC3caCJsCe58Al630'
    'VAvjR1F7YyurbvcpZ6I3tYrCc/Mo6YDDn35SbIvTvkmyqhh1TFoNvtBP++cqaAmU4Q33nhjzLfl+fIoz'
    'A78NS4yVAu53AHaeUid6wIG73ZZUJqcQ7a2fk0qyBYKFbYcnPoXT/7PGYX6YGduE6xSMKnsK/mB5GuOT'
    'eutaXaxwtIRgTPqBjEX4Q2p/2Mk8ss5sJRwa2YwzUTzRRepohp9wix1DZMcRs1ZWPMZL18+FqKEXLrB5'
    '785+ST8IX6VEhVBU6ILy1t3etVRTKBxoMeVlACF2WJms9T+LBwQLzAjCzjmWNa+jty/Xuk++aQO3YSGP'
    'v5/Yx1ooaH86WGH9TXH8jzUtu4i/f0Zzm3aUcRQl17U1B2qpsr77v7wAYQPT7c85kFqy6cHq34iddtCz'
    'RYbKjgSsE56fMa+oel/GrbLuyr5TvIjzkmjcVbIwNtoVBi3/XIbS7LQPaFs9UVVKJc8ipFGgQAvS0Q9n'
    'fWS9tJ5BhaRh7aFpabghFp6VlMkCpMtbF8eQSB3qRdeHi0r/hXN6Jagw8Ibct/3C3En4O/IyjVwOPmg5'
    '3iVyUWeHxeDFmoIsgJX7NwWSGWUH782qWlI5JlQuls7pzoivrz8buBz6Be41xOkeiF/8EdNRKNK6cpgr'
    'nLsvCg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
