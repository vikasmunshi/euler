#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 835: Supernatural Triangles.

Problem Statement:
    A Pythagorean triangle is called supernatural if two of its three sides are
    consecutive integers.

    Let S(N) be the sum of the perimeters of all distinct supernatural triangles
    with perimeters less than or equal to N.
    For example, S(100) = 258 and S(10000) = 172004.

    Find S(10^10^10). Give your answer modulo 1234567891.

URL: https://projecteuler.net/problem=835
"""
from typing import Any

euler_problem: int = 835
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': '100'}, 'answer': None},
    {'category': 'dev', 'input': {'n': '10000'}, 'answer': None},
    {'category': 'main', 'input': {'n': '10^10^10'}, 'answer': None},
]
encrypted: str = (
    'MTRNJ5mtGnOUI6nMPnqyfw+aac65dEj7carDOnfve4wjgZv5rPlJ1GFmr1+PmWgeHnDdaXIIKs7I/2im'
    'RMckKWO0ZN76efMmc75Ahn1Sw/i2las/3qjzXFWkF7yuyEzzXU+d3p9L42BAWg87ffaF1YcxIRUO88We'
    'H3UX0CTe5oYWrBE06YbizFYsPJyppU2iAAAv6IPJPBXeS1iPkiUgStD8A8GRGT4ZHgYTBfJZUDczKG+4'
    'PWzePMEEZSjqkOHiDIN8cvTYWPAt0vrnUfeeS6865rAHWu0yXdcM+75cx2fp4VZGoCqv1JwGHtGcC3SN'
    'nE3k4SIoRoH2vpud+qC1HhjoZO3gOXvpkpVBbZH8+LG5pC2/nSGVeKz8QjtMutclR9yvRN9D+JdYg9bD'
    'X4DC95CKCfQMBh3UhoKvfgnVRrtRi35L5V0A8ZisLuMXpOzYT0qUISy7ommnHBQDg4+ej7W66ndFZmj2'
    'KvuiJ2JxPaQRBNLzEZXHiwxLYz2KRTv1IatwCarDGJvYOqscGUrqVyFXe1M7JuPaPe1IoUi/b3lVE+oI'
    'rEPE4ynlmC4LOsyS8e7vF8/pkU/VpZ3hU4k+IxedywlhBfbLgS3a9U7CsOk0Tf50+AbCcovk2Je6H+L0'
    '7HoSJaz+56OeaLjs2SnvVrGGn84KOXLTJ98ZR5Vfj0UffKAjuNDqRbS4+e5TrwvFGRPQvdzcSklUi9Tk'
    'ezp/dNL9CMVsoNdNTW7W/UxnPEkFOX7IiDhWWQqQAZljbN4aAbVoFraM7oNp89y1HQTmS2jcwpWRh0ah'
    'tXxbNQaMSO06WePIYALJT7Srre2zy9z58Rs4HVmdsc3KLfcMNwmcVgfojKZt0P3pPTuWdtjtYeaNy53B'
    'S9fOTqi9eTaGXRvIVoPOzOzwCbTxzLjig3BcgcBsJui+Lup72duUA7lgLvIJT2cCSpcplvqIWhTrwDXL'
    'ooaSNms7BMQaixs/91G5fKB/iUnSgHxY+2T7zn7cdkffFH28xP3pUA+XZAmZ4jpfZIMqQLacS2SXPmv+'
    'oVJkGBQZkJTeTL3St33WXqz3sIv860VQQ4OnHbnyOQIz9g/zUAxfaUpYEOpFRNu1xTTPNIpARbemHEvG'
    'ttQh8hO++cZ68dKoFTE25rLtNAXlgVlbRFiWFC2jlCuI0iUfmgsIlPmdFOBxZ+3kj1RBkCUaluaqfCeT'
    'GGvlgy/+Muzf7T2ftNL7oDOlvHYdH54DKJ3/oFI6X9oCmBH6rGm9jhD6p1K958UZHG2W0KU4wIZwoAoh'
    'mpMGKYZJ3T62KHZnfHUp4iBwLlqVa7lXALUW1OlIzFM+m3bZTYN7gVkPsINQAvlBVq74UCIMFHJjSg0S'
    'CfECzX27sRHK7+wrrXPd2O2un/jRpwgaw06exmT+pez03NYHLrhOOh8fO2kP8kYJU59o4ExpZRy12+tx'
    '150eMxj4CqANa1u0P4cEXdMlC2gYPGmxCeUWhd5+PLYHfQ23/+kcPlZm6eB3+Nf72IkuZ9Prw9RMhBLW'
    'mn44Qd1M4ZOlx0YR0TAMNxN8WfjfyzgFfV0Y1WLkWxx8gTHq/evOD+p51bjebWMCxkpVIjm+lCUowtBE'
    'cAFR5UPKordXGUyOWNJGMLPQkisInfxGesgvLFyfBVnQ9W2MiwvseL3h/2ZUbTzGLLXTSHvDdiiS2v83'
    'POGRx/TP4bxt5UEXMLRSQkXpo49oM7YVIUHaiidKP+2Qx78KJEkc6Ny83hothQIcu7jknKIkCtzLST0f'
    'EZYbW02xG0vQgp5efhRjOfikmUXPIYPKopEotOLcTdkJdoWOPpE66dFjeJEXYRRKboNN96UohCj9Q05L'
    'Jrv9lTl602IrtjbsyEGmot4zmmiPscA1gnVdOfXLA+CxEn3a9Y3cSndAXjpWXKkHP24V1rzCdcm+F1xv'
    'wDdRa0IdFWRur0KelP3wElmmRZsfKAyD/pjJE+ZrN8TQABo/9U3yBjLabr7M4OZVK8Lk1onATtRBI6Iy'
    'RjfuGHLCCuk2t9xXLmW82HITPbeVs5i3PRh8dorzBuv3+MHEjZlo0OGqyQ9XRel5iuCHQ3oiZYPbMdGi'
    'dSPQrIfJoqLe66L6zjys5VZXWwlVHK7O0yuoweniTwvNnCZ0Mu+3pT2qQhVJYhl204jl7HxuNbKt46Dn'
    'QC/cc3UwgyEl5wi7rKxZcSTR0tyZ/NymmK9GdLHAiArLIxiR2bdib6KgpY0gSgs1pNREI3o2guCTLL3P'
    'JI/eJR4nNCnSlTmRBvIEzZR0d6UeVHzuNMPOKoni64HmEpOdLhHKDDSwOfTFhfnRSmqiwYREjok4+dsu'
    'DQCHGtdIvYDzw8FRswfVgx+K+CU='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
