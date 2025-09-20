#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 898: Claire Voyant.

Problem Statement:
    Claire Voyant is a teacher playing a game with a class of students.
    A fair coin is tossed on the table. All the students can see the outcome of
    the toss, but Claire cannot.
    Each student then tells Claire whether the outcome is head or tail. The students
    may lie, but Claire knows the probability that each individual student lies.
    Moreover, the students lie independently.

    After that, Claire attempts to guess the outcome using an optimal strategy.

    For example, for a class of four students with lying probabilities 20%, 40%,
    60%, 80%, Claire guesses correctly with probability 0.832.

    Find the probability that Claire guesses correctly for a class of 51 students
    each lying with a probability of 25%, 26%, ..., 75% respectively.

    Give your answer rounded to 10 digits after the decimal point.

URL: https://projecteuler.net/problem=898
"""
from typing import Any

euler_problem: int = 898
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'lying_probabilities': [0.2, 0.4, 0.6, 0.8]},
     'answer': None},
    {'category': 'main', 'input': {'lying_probabilities': [0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33,
                                                           0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42,
                                                           0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.51,
                                                           0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.6,
                                                           0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69,
                                                           0.7, 0.71, 0.72, 0.73, 0.74, 0.75]},
     'answer': None},
]
encrypted: str = (
    'pTSvIftmK63AEf40Ai71mW8qGftSdiCoyQY9pvDLxrMwWFN0QAo25LpWuGDGs9qhsKO5/h9jWtl6DGp5'
    'x+aGS74h64TDhzJ25+EsWAuv6jJ6ECIyyLEoSLZphiNYpizf8ngrsMO029F6hrPS7DxGFkB7gRlykv/g'
    'UFgroqf3lrItqEp4S7dm85EaY+2bRp7xlIscIvmpVjTeYcymXV5l5y2cSAzS8cE0b8qhlckqIdwNbF3j'
    'LkLNBt6C0uE5nxP6rU56s8Iiopiiq+XjANUxamWkR1eX6BcbK+zMi0l+rQOezqwtg3arQJcOZXJ4kzLH'
    'm0peZtH4PLo3LivIV+LnxO/zPAQS8N/dLMBe3gOFWS5blq2y9UeJwor1kNn8u57ef7xhxOpFHzjfg2OQ'
    '0ZrhBJhsIVe9JEr4HxnreCepJ0pC4iaNHuNxfWNoby3stmOneutwkt02ueg0lt59FkTwRAWhMnlypfzp'
    'NnkAGZBOPD7VdvmhOofQv6LrAElXlOyoy1BdZeIERGlUsLWe4lDER6TzxQ5r0Zu0rQREyFBWRE2O1cv+'
    'u4uHabvOWLt/s0S/DtTBPWdfWDupUbnOXS7P2F/YgzVtjea+jv8vAunCFQHPBfbGKXRwKpSg595+/Orx'
    'TRKYuGo955gzgB7k4WG+pgdtKNNhtsrVdwB9HBXaLVVwUh2bG9LgzyIlj8PiRQnPTxEIkwE8QROETxCU'
    '8MAT2IW6xIVott6fbxefraBLFM2bFvAv55H3ogNj/WJ1JriKE/tr2g0KxV3MUT3vdUO3n1CEr82lVL/s'
    '3pMYrSd1nvbthvwun22hyh5PUB4mbuJEMLWAouROlrqL08YVjGZv+Xl7kWMAxH6kugkW2VGhK//0Eb1x'
    'QreUrrt+uHXxRnNbYnGkkY4fVzESLf+Ed9EwlTdIWjLA1rgdYzgnFZcObrS/m9Cj6xLaU6x2u+8SMnZC'
    '+3zbbyLBiXTo0JBbD9Jje9LJU/iBIxYKgsAM4YYECSlfyaWGx8enIWPW8H7y6C+siuhQJ3IHZjdGjRGI'
    'MFnOPKEOrHBQUXoXmUmEhnkqaUoeehyBBtO8PAkHXmzHT9mv/xO/bvLgkmDPloc/XNMknPF//MlbUIUy'
    'aUg8GS6koiim/vC5iX7kVtNoE2nDvYAN/xWqPocBiYa/dCvVnMpVJ/oDoEGY/1kDrwg9VGLCTnFfw6Uk'
    'GOu4j9tYQrcaa+nSkXpZebmn8rSoqzrud1JKvFZpGjZuP5nrLjjurzWuxf/phTI80ZwvfQhgUSejz7/Z'
    'miM4LDKpfJghTuUFQ5zVAu0mouULuOzLhSeSVwY8uv8VtB80p0h0S9sjXI66FU+ECJ4Vu9lG5G1TGHOQ'
    'N89Ldj4dCxU/+CeXecfvyM9IJfue0TaeQKM3hRWHoT6nsUGGaX71pXy05Jk1x9j5PIpQNwjEM4m3LoKW'
    'nkoT0FGV4/6KfLPP5OD0HAhHrWDPYMl/1l/JgW3Hi81F1V73tIwH7odhBuVLh5FSkdA4RYgvbeHER9K2'
    'Z01/GB2LJSVc9LEWeWrDgzl3E8Da78eQ8KCvjldG4r5zvUkoN+df5Ea41IRNmDXQ7seVZqjzsxu/5KUg'
    'KCvs0UWjGyTMeefE5X3O3YmlZdDtR6hl2GvM0nImP5wte+vMHp0ljEc3grj2I1WuDedEwHrpz7Vo+kNL'
    'KoIYYEr91v6iMT/6lizGHZwfYQH21VTIwpk20C7JXMX4MdcTVdfr/t0Db+DnqDlwd+HiTzapTQoKsZGh'
    '03yuMiUdsw0b5BqWWNhL5xkVBBYGaWY2dOunFK+RuRCWOCdh76Z6U+G2xEuVqrKURcSzDKRNpkUR4oYA'
    '/Vt2UAe7f1ePevGYClbk7YIHrpCkptksuL+RQQBXVDPYECkZErZsp7wbb1rWtTw3U+25igFGgfFXHkoL'
    'Y7bkudmCq2TNblSsKpwuA1LM2cbu6F3qa+85ktdhLsMXouH0M2e7oRB/NFE1QwVwKr9sU/iaUBEgYCQe'
    '4HqWW9uutfHZVMb+3cErHnQPQRVquNfkwSySI5t/ixYjpYVKr8IEfG/xZJngDDELy9Z0b09L2wbMmfh5'
    'txPqRhLyiLXkYLdtNGvoJ5gQp6Goo4b4X4KzBpkmOWJGkys9iOJjURKkbiLLtQfjVQ4MAHeXPFar5I2H'
    'RxLZGYap8gYlibXVX/Cu44KFS/DJA6YoBcIfpgTLJjL97/NRAVyS6XTp5082tsFdwXHpMjXZYutNI1j9'
    'Mgx/EZWRFBmtB/74bJHPpXbG7pqi8sdt26Jai9bBIqt0c27mpxcsHXHuIgsDgzYMlpSn7kejerh+zMBL'
    'zOb72XiuCzVYw/vzBfJrPOZ6/1CokA2yYMi7cl1riPil3ivJoOnCN4YgdG7PY31MVIqNtDgMsxpQYbBX'
    'YqwaTwlVBKZ2UwbHGdQP0Mt6hy6OYjI6UXSHLg1t6dujmm9M01mnWCrsI0QAjj1UFX/5xwv1vvEFG0gP'
    'J79z05kw7ouBYye9rZRSwjH4WCUFfKuZagmpOX07QbIrXG1RrroPVq8L2Qz//GNJhhXamEl1/MPOx9ki'
    'NqBHzWHGdmvXJ6j3x1MCKvrZHGbzc3dUBxZYIHOjic7mEF6ALCbbjQGzsUOD9i+QJXSBgT0b37iCefsB'
    '7+GtsMAot7Fl5wItOVjYUJAOUkOAugDDLPY4dUPE8bnWisRQzv5ACS4agnZZjTVH6P8Y8KBewzaUNGxB'
    'XT0fzEfA562+tfUgzDbLAQxxoYVMRlQDvV6u++kHLEQAkCkvNJmJ8i/+AzZLh2YdZZdF19Ng9lD/d4hO'
    'GUd6acKsAz5fLVrr4VAD3pkkwe4Pi4BzHfJyWcQDnT4rJ4+JvSdrSBVolwAXL8ocFgNMWdPUvAWAckTM'
    'znspev0cjRhy/Hpn6mGaVpe4u0+3UWwkCG1gAcoJ7ZeR8V+GLq47kSu5GQA4B8gpo4Txz/kbwGhW7+D8'
    '3nHYssHcNrzMa1C6FjbD32HZtZYMYF0a1q9iWx1jyUis15Hb2f+gASwbNot/hvNK3s8vMFKNLICrBH+A'
    'clC6an7gLg2M92MDKwRINwOANFz4jLbe/nPBQH8wFWqhcO7eeC6qlC5aJuildoVupeWdorwD/QxABgWb'
    'NR7cIJVqPSza/nVDtVUWfWfOlIDfdhkxLF0n235TbZ5Z5kevsDkF/rAK1CEIONu7oEQvCSbeEZblkkqb'
    '7WPWHdjqw+ymlLlEe3ODDQ+S2ZpzD8Z5fQ5qn9mE+5R363BVSbaCOIVw429fz6gYvRvW3Fab8cTkQuuy'
    'lQ7r9Qqxeyk1gDLY9tfihuFSrCQStRpH/BJCJ+4AMmytxZpKH24WwJkoQ/q6CKAGS1FEfcneTfONJsYy'
    'CAsLCK2xh7r3an5PcEXZV3Lx6IL5ZZa20c5i/4YpJigX9r+74RBR3cxUIXU/skSQZoZ04QVJRmQF2Uzt'
    'XdYqbPoabiqzg5Nm7K97O/R/iSHdXWT6xh84UfNPagy2c+tcw2e408Ma4wkMB2zxdRB/k/5YvPgWv+8r'
    'vqR/jQ2yyummBhtXsm//9UBgXRmiMsc4MB32ECrPwzi/Vh8fiIjGW9RO6o0gqdSirpB9RrlWuot9CREB'
    'JErDpms5xRxCHM2fworY6vlt9J0jE/GaA7uXTGF+U3DvLi1SV05HRQCDlK8EdRcr2Q0gII3O9bVWkRhn'
    'M8vsiBQg6/QgZgKxYqF76o+oHZm/PveFLOq9nIQgCZ/iapNFUXTbFLoYsIbLWPQQ1bm/MpccTnBd7v36'
    'q5J0PMtLt9Vu/pQcKpIGYcFQNHO9SJxTHmStF0+TZ3PqR6PHEbwfd3yXmz9msC65cmEsjVHTdK8m1fee'
    '+iY386fu0dIr72TZZUSFdmMgWtPRkzA0k/BRg5X2TwQPdk4bwCA97ZZlGJOrjrJYZPwyUjb3TqPxryBR'
    'YzZzuaDfB3XqOZKtyi7uERj08OHyJWKlT9LZAYTxl6cPA9x8'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
