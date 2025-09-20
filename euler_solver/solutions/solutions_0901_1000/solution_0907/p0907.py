#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 907: Stacking Cups.

Problem Statement:
    An infant's toy consists of n cups, labelled C_1,...,C_n in increasing order of size.

    The cups may be stacked in various combinations and orientations to form towers.
    The cups are shaped such that the following means of stacking are possible:

    Nesting: C_k may sit snugly inside C_{k+1}.

    Base-to-base: C_{k+2} or C_{k-2} may sit, right-way-up, on top of an up-side-down C_k,
    with their bottoms fitting together snugly.

    Rim-to-rim: C_{k+2} or C_{k-2} may sit, up-side-down, on top of a right-way-up C_k,
    with their tops fitting together snugly.

    It is not permitted to stack both C_{k+2} and C_{k-2} rim-to-rim on top of C_k, despite
    schematic diagrams appearing to allow it.

    Define S(n) to be the number of ways to build a single tower using all n cups according
    to the above rules.

    You are given S(4) = 12, S(8) = 58, and S(20) = 5560.

    Find S(10^7), giving your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=907
"""
from typing import Any

euler_problem: int = 907
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20000000}, 'answer': None},
]
encrypted: str = (
    'ZVIoBBwkkBzEskYBWSbI5Id4IiuNag1CplTog0M4CRWc+kiktHcKenWa8QhXwrk0dLNsi1gCfc8GaREv'
    'OFogL7JUgMU3MUgHah/RZ1aMizCsD0pbXGVuaNralNVJpvP80S1a73aP7pLzvx3T/bQkCP19HSrJf2yN'
    '0ja8Xggd/adVmJm6BnzbZVMcTkG9FrMdV+1vOL10eE30L204Hy3EuYKX8yZ5MRkSkPKdmLlMf43XGfq4'
    'JApcLGXksR69BG7DjzQLPlVti3iqnNXqEdW/nlVmT/uXr6VCxi87SSyV6E8w9QEHf6XFZ7zScw68VYZn'
    'LvNMp3eu2HVwkrHD6+DmFvwZmJE098SEbmOHG67w7osbB1If0HkZTu5NVh4XpzrhxQg4SB515323qHUP'
    'S7xaIY9m06GHSBn1fC4LwNmc3jeNu77kxN2kbxMuxKa8XGzp+QkSYINAONFPei+S42N4rnZim9GY8jwS'
    'DMaCBSNrspZGEipNSzXXWfYYt/2nElqupRcgTVmyGLL9qRzfmXBsCQ8QJLv0Qktv4ydXVqLha7BCspUr'
    'FFnDNpaA6ntFCqSHvyX+tGEppnewNEJuNbLujzlYcGzkAx7/SisfoCUPUImsSslUYWXxoaiH3uc+cLw/'
    'vVMdO7y4dbiL7EpKtKtUa0YsM/GDj5fe2HplkUjhTRzJk23PhAnmH5WOBCLAU6oFZnnXdMcRSUDUsTMg'
    'Hll+rVRpLoDk1HignqHefGJayWjFcUeZsgbRAcY67s/7EG1KnSmrttv3KPWvqfPZrVOX0VbBD7mOMFgC'
    'ek3sJ8L/rcPhwEhchI5N642c6163POW1ruTGx/X/gAmrVtGu2SgR367TdBIDWJBadaXV0S6W2ph54FNS'
    'P+zHOSeSvGN3dh7MDx/xkLUWd+FExmOPKXPuokgUwHoiN69xxCqRw4cSr6kfk31rsMGkaZLjltyzh4LT'
    'red7jXN1wbPo0rmx/0Vd+w07gcIsz5ZGizJZk9LX3+dte+w10sCeUwlgTs9uAX2DxUw20kH9eBJuwmxq'
    'D9q2NwMiOhiFjzkASzzq7fVPJyapELTEg51mZnR/rdadXPa7E3wOPDfmwHhBtuddpCMRzpyktzKVQjuE'
    '36Yx1cc/Ve4g8WfQt/gb9CZFsbzi5FMY/f5YyI6T81eeUSgkt7utgLCSMf1J9kHB8Wk3vf6sUCQqDk8L'
    'NSxZBA+cgVeQg9Vo0dWTxjdVjLHICoBPKF91XmJqBPdApDdF2cP8MrLaTyqeAbjZEOFhbiW5Zyd0oRmJ'
    'GwIVucnX6Bd79jD6RxrmdmP4VReKTM+io7QQ1o1fyb8EvAAYXQxflEWTDWiBQvt7niD0EXNU+NREVIEu'
    'n/mX0KO3yghZiHuqAw1SGg99cIhVQYqvITJeompTxKBj9d8VirnbXjIQCX+wU6HQOxrbBho6KnXR1Pnv'
    '7YWsn3Vcb9oZjsX8+02rnIdOaruPT8z2d8fWT3K5d2xI+4/5Be6Af+rAiXpLPdLmpHVITLR2P7IoBbuh'
    '03wh07bNqYfywZ/e+pWj8tZ2hHAklMEZ8d7kik9jJKsXoPQob/7idcR1iUNJ2eV/SKiLHp+p8Mg3B+p7'
    'hy+4XBU0v4QR2O5XJ+qKdZjxILsL2XiJL//U9e8M0jr14lQnXjO8wTanQCVkKX+Veu4y+ePto6qQ5OYD'
    '+QJlLuePZnEQgmQ4YbU4AOPxTAos6LlZE9Bs2Rdjzw7x7BLm5FO7aq2U/LxHi+8ZM/ZeYLe5XG/vTT5+'
    'Dvgb/MsS5WLFFSRwqJHufOUkLlUOUHY8QnkpIcRvT1BGqsmol6hweaiDfSoIycBy4jCfQtEJTTM0SMGU'
    'b7ZMZGt71RHMKJHjWDPLY7fNSydtSLYRZR1NRQ72MolS2qkWPRXZcvQkF9j2zfHtHg+6zwidVqKgJW8J'
    'QFeFTDDwH11YkmY1X/wACgb0cJjhzC0qTKRJm5ttB9EKtCiFSbI2iJPP7LuXmdsABkYHqGaLLewWs9Hh'
    'CAO1f8oeXe9ymaz0obVkVwxyXxKsNtnVpyNWwBcO89gFuf/nQf4D7hA68IxBqsC1hpbSEpApa8EditX3'
    'z2HryR1MWkJYeqID0HNPK8o8BQmHv3uMmW81L7ASpMUmenWJeEh3bIn1H2aTsTDdvUy+rhhfhY1gl3b2'
    'F1aGh7Gtsxaoq3WNrp7vLyvNz5RGs447T8V70/FfXt/5q8zjF0QsFrM+7Q9xYiGb7cURY7w86FWu8rcw'
    'PMiIPcHdpQtoi26meoWrgGznLaEKiP9VR5KRwhncaF1wilNdXYsIIaB8tEblan52bYm+htWUZ67SdWl2'
    'vrWd/ufBF9PZ/al157BFcMCudXmfnto1x7CptqTnHI35MdgJHn6bcQctjPMzZv+5tlb6u2y7q9JHTgjN'
    'jgSJ5V4pSLjIs/pRd+bNndMtQ0sFt1mVqBiT7QAewyGfcVPEvNDBOonZ8s473dmHs6x+jd77ko+VYtG8'
    '2vIiPmGx1RsCJiwMDSFbFUSMkbMYjrPJa2NnJysoEf37lsWkwmFuhn3XobkzpNi/UlUcZOBBp5EOd9Ya'
    'ZfxvYQDlbeIioz7pj0Lu+gWdFkfjquxGo1AKV05hAl/bmJUraHq3MQT/+tZYz+T4N3IMPTg4cXr9oSEZ'
    'ZpWx8ONr6qECfLZ4AmCJvx5wN4O1otfxjbx5VUCm229BFlzvUQlvxTdxQnlJ8f4GIJSVwMxfO0vmq/xu'
    'TEz/jvLMCsz/nImLqhg4NEZEjMgnAyAtNO7iWI6jVDjLHEW7ZzEaDTfdPPV2I+fvY4wuc7vhgZXbGWsl'
    'QrBZbL5ly3KllWCZqJleHNpc9cHYqTj/x9ClL72VSA0ZDRyttoTQeoozYiJGzV4J2BIuBfFwj+CAKFF5'
    'D2wrzW583V9jgFW+qf+N94tA8UBD+u+NsvSLDjqxLfjNMc0gWN2A6xu7yzkdB+LBVW0FfL1NQaCMX5f6'
    'NAgAR7FmMERUW76eGR9pJ80mLikPJ7X1ksmUnWDxKOpD9LPG2kBuJul4Fqq24Ia7/YXG9yHnV3Lyn3zx'
    'kgzVqipObc1Gmtuf8RJQ+7Es5ZDezPSe2AUlWHDNwc9obou0aEdHmotOTvsmlOXQwUvN8HUW3eXArF40'
    '++uSPR4YPPHW9wZ1+gF/EO+jFH3fi8ov6MplQeyDiwyzXa4D33QATfAEqKo='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
