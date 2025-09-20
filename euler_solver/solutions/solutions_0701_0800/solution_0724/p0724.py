#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 724: Drone Delivery.

Problem Statement:
    A depot uses n drones to disperse packages containing essential supplies along a long
    straight road. Initially all drones are stationary, loaded with a supply package.
    Every second, the depot selects a drone at random and sends it this instruction:

        If you are stationary, start moving at one centimetre per second along the road.
        If you are moving, increase your speed by one centimetre per second along the road
        without changing direction.

    The road is wide enough that drones can overtake one another without risk of collision.

    Eventually, there will only be one drone left at the depot waiting to receive its first
    instruction. As soon as that drone has flown one centimetre along the road, all drones
    drop their packages and return to the depot.

    Let E(n) be the expected distance in centimetres from the depot that the supply packages
    land. For example, E(2) = 7/2, E(5) = 12019/720, and E(100) ≈ 1427.193470.

    Find E(10^8). Give your answer rounded to the nearest integer.

URL: https://projecteuler.net/problem=724
"""
from typing import Any

euler_problem: int = 724
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000000}, 'answer': None},
]
encrypted: str = (
    'DPhW3LpPlbeSXShV/Lpsd25t2OJhqU1wk6PyddbzOwDCDGnasa895nDehvYj3isKIayMItOBATKUj7cE'
    'qCoDZkP4CxK7U2Mxc2/Uuo6rx8BVQwuhsgZxvwRYqydPAv6Jmi2YhNSX2URlTd5Y+9s5FnmJ1gd1AeXe'
    '1EYhbaqIgl3+ncUwgUKQtKmVMhxNTplSO0yfrIdvMp0KTPu5Z/OS023ws8fERTKxws7sLDj1SsxKeuoA'
    'bPpM/zOO1ze49M4xeeHkksbnIUFkF1eUG6f23DuOG6Z8gadWZIKvuRmuT+xplG48iC6TTVBtlJ3H/Ju3'
    'KlS09SuWywvY3k6KaVd8cQXh8ePvfQ6QBVnVGJFQOktBo3WJgas7vBGdVtLcg7PPWvWhINHp/WBK28lN'
    '4T+SS76efxXaXrWGjYhxCE0bK1GX/U710Bp7fQq6+aisxLWaR7mZ/7jFK/OpUiOXUIb2G+wcdjLyUB1A'
    'FNOtXCzjxJQWyXMUe6UBvepMWloHY/6ugX+UygVSBbFkZwUq8otASHRl9j4IJbRqxDIHTR59xvniOSdZ'
    'gX6BzayoUaY4l+CaYroosTX3RaFH85HJm9nkVGphNaJNkZgtemC/G8VVDFpTxybRbmqHk0U52LlZObBp'
    'uHNtASLGL3/FH2+pq+lb/1YIBxpfCxUe/c++imD+P6yMOo8B3IWJGM1oZk1eibvQlS3oyFuw2cNzGwvS'
    'EV87UL2SOgmO+jScSjz+L3HioO4LxeLgGgK/V7jRuondKoxlSQfUEmAOOUxQ9S5oZcLwx4NsayXg9EU5'
    'R2UWn2qafbPCt7mzHnfr7xYX5I8XjJXVfu6j0vD/fs6Fw4Ia0kjkvmQ/E5nLNa7RZ7xJwFVGH11U3/Ys'
    'Rt8lRP5hnhznFBQeGVfPQ8haP9LMY7uZcjomlj2NmT/qFxVkia5rt5z+MKufgCKPU0sdnlw24K1XJzPr'
    'wWDb/92Qsba5h5VpIowBHnKW60TFLdPiJB0W+4sdnQK0/Ia5puBYsITrhbo/mC5ibgI1FBqQROCfYHmM'
    'afyChRb5NY1/aI6XxJwYXenRsxp2pCmNet++5V3E3vRu82Ar+uxssySZrHGBtFJ72KsdYetuf0WkYttj'
    'aILpKtk5OZQiygpeGTGRNdClGlsnQ5+J8hage2CUuk5inoimkSSgqP/rIRG16l1QHp3FxLH+ZFS9Hlfv'
    'YOw9bQ1iWRbIwwAsS1BbVawP8SvY3vHkIpDRXSeUi5rFZ4yiq6rUhZTIUqjn5n+3gOR4QYaepoovYirR'
    'OpXX/b4NMiV4tGV7koVVrAUl6yr3wvSrc0yWHhttFLCMeaPuwoaT4vkOlq6Nj4J42aE9NrdyJo6IIDBC'
    '4SHcf9wgD54AdYY6uWuzn5u/gPR19HPZZv2FSvaCLopxl4nyGsKV+J4L6WzHv/hPgrdFm2DE3WxKWMra'
    'DgGlXJ7qrqR1/PF3JDZUTA0gtgxoEhqvBlmeK9mBEWGmBgDxwcFQDHhPG0NVYkOqSvKt7SH/Hum/r6v1'
    'cIQeCM/QEnW9B4NdfH0F41WWFQorTP5K2rIAklNIu7gfqoxKl2vjfrtCP+dXia/Dv7fmjSQ/9h+BJphv'
    'fbYVE4eqOtmVz18ZHzDDyxULpufuoADF8is8ALEuF+C66zK0adqZ7Cxkhzrdam+LyUudMgL0npAcVjBY'
    'EH1XFVMEDyP0jQwLAzRYD9nE+rf5ausrKjOb2Wqk/zfjj2/Rcw2FFaFFJrklsOKvGLek9qFKYRkzoqWh'
    'tJnwZTI6LtKjMkkWsQahRPBbeI5iahfh14QRahCaP+PkP3inwDLFuLF/MFmpc4IfbEtGIBi+s8I9Ex6I'
    'HebUF0hBL/ZfISLCEGSISYPk+e0hqmvgvZdv2KpempIWet9PSdOL7yUTHqXTsfibTLfQbShKQbsC6jxS'
    'Npchafw+mT1oCYvuy7y0fyxfYgLcDUaEl4tgfgwYZ5u9Q4JiieCzEUfUj02/WxuhWNJiKxj1vi4tfKIb'
    'jX9R6tGT5x+20Y2EYEV3tGUEppNCwGDyazkar3vonvkMHzQ61dSOikkYTLN+3AQK/Kb23SsfyK2LJ09/'
    'ZMmFIeyFIbxEK4+55hvPcH/vueSsp4mINqF93zO51znVd23AY7xc7++YxvKWck+QZgFzhNrbpmrETWs9'
    'iTOQjYe73BYZNNbv4G+jHKTjorqbibMG6gj1i/ie/JNsO1UGWKixAx8SgL5kvqq68MrMqEOMhG8PBk9s'
    '+ZaMtS1jWpEEFHerZLBf1zjZ+xnVtQP6e8cTrSkNjTK8p/xjrqaT+HWPjCJXJ/rlGBrzh8Gg1JMvUTL1'
    'a3VEXGTNUXJeQ8emZVAhSogT+wE5QelaSRYwU/MuYWLPFUY4rjqvVKgYNWX4kLj/iEjQuX8pkzJrPF4A'
    'pHQCwPbTkaCoOjp+TxzYc/1BjKY0SMC7yfu9gcDWOvB1Up7D58dB5XRQN9TZK75umJ1Be2R7m5oZkAZ0'
    'TS88UmhfEIUvDrryJLAE+dr1R3/QnMVdyTrlhfhnwPGyVV1P//vfAHgBX7hePO+Nv+n6WCdb9HBuQcwh'
    'a0C278WYS1EhHXJNbO05laaiEXk5AZlX3pvlEmaCv62SxVOHoDyvTBhE+XES5jxw39CA9rrsPbr94bsj'
    'XvDDwJfJ2RicmEwHLrAwj5+Ej9PyEdNmvhw7QRC0VAZa+UzQbaagDB4CMhuXkaSCmTb8m8me6ZTAgmF4'
    'x/E816O0CTDAiH+nwYcehn970pMsChte5qE3e5QBkEzkEehcZ41hQEo8SjNZutar/mVxjOUJl1ida3Kr'
    'xeknQsy26qeko90epvfb9xLGboZfXZuipbpLDyJT4DnN30T05ddXwHiA8WpHulg1rChpr3R5jeUVpOMR'
    'zSwvCgpgueB4Aydvc2UAsU0dUClfZkFgxqTNcGXs+C0SBe6wMejC3bSjA2rtWHzhcShjOnIjMxma21bV'
    'p9C2mUchpIAD7TC9cYAiY7KbXUQ+wt6FaxfYm4UCaUG7dOPmkB3nD1QCvMxvbuBOnrH9RSxo5kyijccy'
    'EkKplsDRxfbG+Ba+sM4NBDuVFejGippjeHLxB2XwzZHCxT+dlWmAVwZnHE2fwBT8vF52k71RyIhvmsfM'
    'VOYI6QsXSPXRAtiTNUjVQvF6qpKE6Jjfj3L4dEuT9wCT5qeMTW854ggAOU5SKjyVLpFuzrPWxun9+QOA'
    'zIXLS2l4c879ue21lW9ehA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
