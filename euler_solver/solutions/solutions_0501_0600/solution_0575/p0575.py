#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 575: Wandering Robots.

Problem Statement:
    It was quite an ordinary day when a mysterious alien vessel appeared as if
    from nowhere. After waiting several hours and receiving no response it is
    decided to send a team to investigate, of which you are included. Upon
    entering the vessel you are met by a friendly holographic figure,
    Katharina, who explains the purpose of the vessel, Eulertopia.

    She claims that Eulertopia is almost older than time itself. Its mission
    was to take advantage of a combination of incredible computational power
    and vast periods of time to discover the answer to life, the universe, and
    everything. Hence the resident cleaning robot, Leonhard, along with his
    housekeeping responsibilities, was built with a powerful computational
    matrix to ponder the meaning of life as he wanders through a massive 1000
    by 1000 square grid of rooms. She goes on to explain that the rooms are
    numbered sequentially from left to right, row by row. So, for example, if
    Leonhard was wandering around a 5 by 5 grid then the rooms would be
    numbered in the following way.

    Many millenia ago Leonhard reported to Katharina to have found the answer
    and he is willing to share it with any life form who proves to be worthy
    of such knowledge.

    Katharina further explains that the designers of Leonhard were given
    instructions to program him with equal probability of remaining in the same
    room or travelling to an adjacent room. However, it was not clear to them
    if this meant (i) an equal probability being split equally between remaining
    in the room and the number of available routes, or, (ii) an equal
    probability (50%) of remaining in the same room and then the other 50% was
    to be split equally between the number of available routes.

    The records indicate that they decided to flip a coin. Heads would mean
    that the probability of remaining was dynamically related to the number of
    exits whereas tails would mean that they program Leonhard with a fixed 50%
    probability of remaining in a particular room. Unfortunately there is no
    record of the outcome of the coin, so without further information we would
    need to assume that there is equal probability of either of the choices
    being implemented.

    Katharina suggests it should not be too challenging to determine that the
    probability of finding him in a square numbered room in a 5 by 5 grid after
    unfathomable periods of time would be approximately 0.177976190476 [12 d.p.].

    In order to prove yourself worthy of visiting the great oracle you must
    calculate the probability of finding him in a square numbered room in the
    1000 by 1000 lair in which he has been wandering.
    (Give your answer rounded to 12 decimal places)

URL: https://projecteuler.net/problem=575
"""
from typing import Any

euler_problem: int = 575
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'grid_size': 1000}, 'answer': None},
]
encrypted: str = (
    'f1hdpDSe+A6lHWgDaPrGofrjSM8Hyp2mDK8DHCiHMGDRk4mMcMCgpJZLJ5xZMjCdG2O04wVk3u5DH+Ld'
    'mr3Srm03sK5HjK+hQY1QN2MO8JjKmXioe39bjfy/8cLgPSAAzz+C0LlY4FW46nTVkPYmi2S7ZaKb2W3N'
    '0MslxwhwFY6Pv+9mUsZick4ZlhA5ixaUG3XFJ5IX2yILOWS32i76nw3zrVn5NlJSILRWhz8XqLyWvznq'
    'bYKObPQ+fIFFmnEWZffqb22oxlRfdz2zLL/RjW4TjANlREOCQtPwJ0FQUvhKMd5MWd7+WJE6rqNelJwO'
    'xSvgpWaliBIrVqTiNToOZZzLgeY/lEleTHGpurPTmIcFLcs3dqZN/cHhQVI9N81ZBmeEdXtHtyrk/O8I'
    '6o0YQwJKy4uo3Q7Pk6PQNokLqTUUxHzUBdOVTRYXOs5lNHIiv8gQoDFOqxbOAm0rp9TdTafRAuwea8KI'
    'm9prNLE+xFjT/pMI8uqf3oGeuwDhhfLXAVQ6zxYZ+7eiUleDL/fRUDhVZrIjxuMkGHylAhaDM8i9+ztj'
    'PpXck0f99OrVLwGdHIrm+M4dA7hAZQvJDoA+wD/ZFIa2omZgZfpGRljrD+z69O/KyRVHRgOkArG21LJp'
    'pmWiJr5ZkuIKHwY7cTOjOshiYt3+4vtpVp6hlNj7XzCC8NxRXDktXyuGraD8g74RE80bmQaqkIoij2Sn'
    'PHf+eZt7E/qoClwxpMmwEq1ARIvLIODCYOf4VDGpEeTvDGTOEyU8plwUyfjnwRlmdxqjRArT8ufpJ6qY'
    'IjQ7P5zKY5IAtSiKVDo0vxlCPG3LbP8MIU5d/5WdDMMOX4f/bzK4qMBiHoalLovunIIe86lJtt4jiWxh'
    '8iMLHWkLZPzi6MqVANfWmED4x73d2xLItg+UZ7u3gFg+sXRvw+lsDpxGgQF2DlyRwTHoPi3oZcM+wsSg'
    '7nVNZFMgmqOFeyD/WsUmHL4mDbP7C5M4dh36+1I2l508+3304FAKKU37+141dms52GyQH3rVii1VpsZp'
    'Q/bj+ku0UivhA/2C+UzUYSAez2HiBJNvj3efoO8E9jTffPWcNZTO+mvKN891+d4SmsQbK8NxbbAx79cP'
    'AoZtQmXdVJEOc4JsZQlItFnOrxlbNLZoXgP3mK6bkeYzQb4IWJp7+kSb1wkMGPxcru/hftLp+ouPAUwk'
    'D/aibDwik9bmhfd+sWvohpAuMb975QVkSiuQFFk5PPLZPTCbQHDcmVTX7ons6RR3hw/aM8MFKdX5TRfy'
    'PPzYVxZpomHlVYYKoXNUTKHU5C0nEzrLaIi5nAxkrcwKg/im1Kf+ptAiCFDGD5ZQtSuiXpbNTr8xEAD2'
    '3JfeQ3s2jXhPf4jEakYUBjiDSoDNwHatvDEaO3j3OieY6mQ3fXiL8OsTXWf5E8O64P1kZ3l1MME7mEEC'
    'QAhrrY3kZhBFEfJpvZs1wz4tWWNznO/AzGWID2E1gw3AECLXfS/H74eI0r8fCq65RnAcuK5ihQg2WwDV'
    '5ozRhlXvc98UuAPzf1do3AD6o8RPNYbhjk78oX+1dZqc/dwKHDQFCPU6kxNgGMW1u7kDmqs7J5c8zqZl'
    'EXVrQlIIL50Ip41/7rf9YKP/hCT95fC5c47fj/8BUcCSFSC+nj8dcdFM/gyApuWIScLRCc4bBJ5UsqOM'
    'UqfooELdP/cKCHznKRtrYLklYOoOXVNig200r1xxDQt/I5w1AZ3glohXeJn1OufyXsBg4tHrRlcRZ/kh'
    '8hOaWKTJGGyksdhO5wE/JWo+CzufALsNkCtm3ToQGpZVirKvafQ+3gEjfHGYAdRQ8mZo06+NwsuqHI7Y'
    'j7Wj7UpMRqwezQUuy4sBZ0qhq/NLZ9OiudtnlfYcxLRdAjOmMc+K7u+jOfueF6W9i28H4T4DyB83JeEN'
    'GBpLDRKNeglLCu5PbjX8OlVggsWrygI+A9Re0t1T8pFR91RdySjq084DmLFVdNY5LTQ6m8eg6fq/K7wt'
    'mVpvDq6IOH/8gJMlCo8TZK63Bp0EqbKH/yN0NPePatDWX81H8S1BFsqoFZe2NVJR1xcSLXzT6zQGhZ9Y'
    'RePaKESt/2yJdQ2+Vv9jQ5YD7xfFr+loqub6+vfvlhAzEg0XH7KTuhqE7y+jdPAnbCwiY2FNJwmV7WGV'
    'aohJu6rQRwLYw+hxN8TmSfSt42EQnZyzJOaOfU/I4ZlgakEsM0TIFZ5nqXGn/eWTcv7ANs98lRS/IfF2'
    'XFeLZ5gmDeGqxvBrtzCTFbi6Krkn2CAna+/FN+W6AbnvP9P8W2nAuZwmnRo25HiXb0oS+DVATFNBA9G8'
    'q1UK7ugvMKjXtIEr9Kld4BMIvouc8KjA8ltrdNyop5Z7iJ0KBYw8Ugk7kXnNStAWHsG+GCpVG29Gyf5m'
    '1PJDy3g2YoVFNUsIDxNMjf/6fBhMsSaKipLiG1KP6bdXbU4Gj3ONGQUdbks6IueBnR1pZUvFiCy1VIbR'
    'k6L8GUcSOhWjdMLp8QL2XvO/3gSd63/dsGQnm80/oStjXCubHHbYCYvdfTQExz6Jqm/AiErkbPtQiPte'
    '0UAfqqSwU9Rk0Rz3FihMD83wpxy8WbuWZtYxiFKBwpEfsU8tWzddCsRSmOT6HCIDWVvUWMDoULN6dEvt'
    'VUuoKzuqnm4KsXSU2Qosjq3gLomsJgw+kF30pDPvOnzdqLk0UZd07SunZ67kvXTcQp6uVJ/wL0AUZbuw'
    'bu7f3ltRYjYxCPsgNITw/YRTc8gJnKqcMcUQ7FBfpu3gBRLC2XNbV58Z5dnWH4V2KbRQoIOILLn8enHi'
    '+2JQt3s742eQhK+ul5xVTyIx+tU6gzDQ/AftSJbfZrMZ4LKemdD+cnFuSi3CEp0JdTEByFuw81LTu89y'
    'AbgvHgNDSFyLqtFkfajY2JRHiK497+PW9sc2d6KULMi2NU/yMcIM4N/Nuo6JE0jhI9OuSXymUKt+jTKl'
    'VSJy9svDCSMjk7a5e3sUTZPHPS0fIY4jiMWtGh773odzdZHL0P+Pc6TvOZfddUzeljWNxKDrIG9y64lh'
    'mfh8+qe56bxWP3GdD7NDsNz6ShfHBdMbzM1DUo9yqAIXXqkN772n64tyjGn3kMiKAFekMLx4Wa7QA/N6'
    'AElbipF4hD7GxVHcNUlEKyOw/ZxDY0MRiDVuKz5/HcrvYDtCte8Z7qcRWMPtkVQcgPXrVRX2Wf7CkcNf'
    'HC+GhQ7Byv8p3Qws6oWw8OW+npIrZ4lBau0spFZo9fl+ADBE2uugHjueS8z72p+pI0QeLRjZ6Lc9hDCI'
    'DA7Gx1L8GIBzpj3CbvutQHnoNphaqLsa7pP8RvySZer3Acc8b2heoPMjnMkboiB0XkquzeCK+Ju1K9/p'
    'iSzX2ciYqbdPoTSe9BihDH/4TQ4oB6RI903VAX+mz0V2HrtbVNx1LAqF0NhiFbbAfy5lZ9iajZ8KNuZ3'
    'y6pm203TOafnxHyBMrZ8nxRRA3TGZt7ehiAxcy2JXtV8gd4wKaos0qUgeohs7kg6Ieef8oCdvKAdPtIH'
    'cAaZlnKcmwf3YqvlQOfEovMkOCkPhcMEvII3EyEmP+d59D+6R/iTbDVyo14EjkRZP1zzCzhUDyjFH9g+'
    'nRuPIB+zVbcNreAD3QVeKfQqLg32v7KhToYZwi35Z02qPHSB++gM4B/HU28cVN7NWKh7Z+j3GVWsQDqw'
    'LNMQA0MUg0cqWHsfr6eIBGUOzxqonRrqzJZNwr2w7BBDBJDI5yGuQz7nRbvytJSz8lQ9c9KF5GjPr/yP'
    'm6WZQ/GPqwjiPFGg/XuzRO/M06teG9mhq+B3yFiHZraKqyvuTwIc29jvLSIpHN236NAcprpECAvvuxrn'
    '8//n6XomBlpwElsufT2rKo4or8IH8wK1SskwWQG5qtH7TG8Y/tTYGyArgyxC86SiSp+D3W2YRpx1wW63'
    'K08y/2ve+pb5q3q6o4cJz3jocZa4RXh/U++jefMWiQITw3SrU8zqtXFS+R2XNlZAz6hbeBZl94u6ha6C'
    '7E0/6FsSBUKfDktJM1BfkM7BldbPuhVHpg23LtJr8j2tOkUAlJ4zqf04CstyERKRNJV7InumAaJu4hnX'
    'wnytP3COcxTIQmM2MWfuQuYGHsMwENP6Xyigj0lRWxZoKKto3hwUWUXU52F+OgX1hdEf85pwo4QliC4l'
    'ouk9YxUkPJuekJ5EVmNhsRfKFMTVUMbNNEuqKTwnrZNI/A+KuDqPFhYCScH60lvPLR3S1HeFdpRICSkA'
    '6ggLPrtVnFwL8vYHy2wzRyZFZi0lr8cOf9CPs/h1bKO3QHL4fCPpQk0EnngEa9Zo9qCgF2O+ZeqcWfvx'
    'd5Fi+R9z/5VyKsIUb2zQ75SQF7/LoHY/fseyRR+ouWdF+vqoKCGfoscQLecHf1J9Tws8CISaWCDY3zzl'
    'kDD9s9dt1zHF6EOHryx4GnltNepuq1IYH99QtUO3vme9x6DDZlFGXCbp93OhZzQKNfmnRdC1bmP7h40d'
    'TkCGjam6Z/gZcmIQE4JqhpeouFU5jBus5NCzYkAzrZ55vmF8VHFQVPmN2gieUj7uS5LfYmvD3vlie0bL'
    'exEPH7Zkpy8aAJ69OhAZTqrCC2rj3xZvrdNBt4uv7MBAnLfEiRGRDWsHrUutzj8MCsmTu6dE6N4I/dr9'
    'NPWzQZDwu+ir9DqA7llWH7uHNtq0wVeG4W6LuliIT1x6HJ/O5+Xo+vi6xEfv/DAWt5ZAwJhRCQh+I//d'
    'juZIjReioTG/WqCfkV3EYYuFSTCvyYM9ZC41yNBzb0xPHmTIhsnTVefQso0W75gostnK7oNWbEuf1lhi'
    '4KbmV9/hS/ZPK7wfqIDOKqDUs5Vh1iuo8mLqSzgXlPzgzIV0UmBF8kQSHwblO9eHyopA9Vn7eMSqU0jr'
    'c6k2MPjsrgmo2IIDwZpgpduF3ccOJsCTg3rrQazUgB9IIMhf2Cj+Bi51D101MqCnOo0dPRO9GUQ6N6jb'
    'cwJS6a5zzlfgpqBHY4goQQhZWc1Fkrpw0RA1FNLyvM4/gIFq8Wc0Ao+qDBxXBrQqe6jh9Ufearr5BMnU'
    'vFmY/XHh4Djh8ZSWs83boBEYS9l0VjeCs+2gnTY3IpJhIVMNZnCkglislE4ssoJSmYwY85QnByaDyGsd'
    'lK6ZSnpuLt7MBYQg856r8IsfsnBQhYwbxFmLP2jaW3y45xS6olAqDvVtel11nL7yrWnuNfqglLuaA7Xn'
    '2GVENIPn6ck1HNXPUErsOvAJ8m5YxgaMyiS0Tbvi2BiYXz9Xpc42iYBCfyaXZWcmaQwn/PhrTlWwibX3'
    '6Nw+nyWZ2zDrZP6k9q7XsCMBTFeg2iCzJ5ogevmyUnmeFh6d/6G8ZrL1LKZl0zs4TlZi1LuEfqDrzoa7'
    'bQqMoNJ+mpvzqXtk4Lok46KY7KFYZ4wrSt/6lzuZrKRpjEwNx0QpQQtWvoioeQsglfw9A3+KQ6VydiCm'
    'zkWhFOF3izcHF4k8H9Qxk2Z5KfWZYlguCy1kOZZRb8dW0wHLpbU22zVGGHjSMaM9dxyMpT8cfiCVUPc3'
    '4L7PyalouG94+v2gHocxwsGM5ybQXHlixwvJzOUUwiRxJexqmvXmVoPK3RlspORAbmfPrg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
