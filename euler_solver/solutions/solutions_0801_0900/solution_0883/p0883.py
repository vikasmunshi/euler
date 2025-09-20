#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 883: Remarkable Triangles.

Problem Statement:
    In this problem we consider triangles drawn on a hexagonal lattice, where each
    lattice point in the plane has six neighbouring points equally spaced around it,
    all distance 1 away.

    We call a triangle remarkable if
        - All three vertices and its incentre lie on lattice points
        - At least one of its angles is 60 degrees

    Above are four examples of remarkable triangles, with 60 degree angles illustrated
    in red. Triangles A and B have inradius 1; C has inradius sqrt(3); D has inradius 2.

    Define T(r) to be the number of remarkable triangles with inradius <= r. Rotations
    and reflections, such as triangles A and B above, are counted separately; however
    direct translations are not. That is, the same triangle drawn in different positions
    of the lattice is only counted once.

    You are given T(0.5)=2, T(2)=44, and T(10)=1302.

    Find T(10^6).

URL: https://projecteuler.net/problem=883
"""
from typing import Any

euler_problem: int = 883
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_inradius': 2}, 'answer': None},
    {'category': 'main', 'input': {'max_inradius': 1000000}, 'answer': None},
]
encrypted: str = (
    '6F5LyZmLa0TmF2RnF2KVXDuvdXiyeprotPFnRM9a1n1MkphspTHqUlfSCD3gJLVyCbxm7yrfFNY8Nibx'
    'IvQTfVV4yGhjkyR59wLFnejqQoL0n6hxK1PTJqmQKthq87ffohEqhU5SA5ZdCceKIC2hqieuHzMhquxA'
    'MNiTlDqk8P0Iti7Cgke6wXApkzFG1Fpcav8ZwbQ56W2iw2Y8b0e5kazZPSgOxV2Sg7QVr/LP9guELBjF'
    '0KkBenysyj+KO5eX1BhP4fqeS29Md+JYfDsgWR8QdDTss45eqysOKx4M83b7ADKqyIBNfJ6fk6598498'
    'zJVnlCTS3iIRXna8jswT6Jz7mIOjDEH51hKNsAs5rFHPhDYfA5OZWKc/X+oiIInoMW6tR7s7Q6DICJ0F'
    'K7+pnPieextec+Fli4QCkpJQcGKUNC8HH1jl5i/aGNCTGDmtASMHFdyJiTAhENGw/bXnQaCo/gnwxJDi'
    '259LTlr9RJGW2oCIODPg0MWl/0tMkS2QRhzNHetMZ9OWTtd2jSRHyqBvx4PmDW+ZoFv036XeFO7nWYB/'
    'QyKLCoj67VAXliN8O5gh/KBAjmKfT7BrQhzCQHH9iPvxmoW7spa7DtjQX3gyHMfbN1sDM9g3x6p83s6S'
    'j8FKQD8BLrYrMFkJBAnsvmEd5WH2FXsifaufDe5Po/lv6PottCpAXayH5WV9zR73pbIoKDCV/UbaFQlJ'
    'kiYBQ8hXg29St/5PgXKyPWiIzT1iq/t+u1ghljV5BRSMVRRIxEBqow/4XdmfxY7xhdUt0b1mt1aantve'
    'kbitaO0qCVgATZKmx3Yb5STM5Ywl39QzR+csgN3oGHOzCHswGDwT11RJh+xH67d84lyrU+JhhQ6EIA8V'
    'yP9/BbspugmBOdyA/QGsvU5cmVFWfcc3AAo+n7oDCwPQEWdpxtidhv6Oh64TkmH6Mxu8iItiIzXg1w6h'
    'K0aBdVYFXPcTtFHDtKGaKF2zDMIYAi57R9TsLhVC77Zzt6dQEq9Pyeyd08YDlGlYlPUjKcqRPg/0GIW0'
    'StdKo1q87fVKcuZnUhCNwdSdGpBgF8fwDJexM1kDYPvAjawvlKGJOymqmALIfbRLbTubyWieiVhis8cU'
    '9dCGle1u2/SvheDdwV4npF8MC09DYRS7ZPqPTrt80LfjunaV3qc9liYCLi5MCEQWKJo7Qr2NgHrk5/gW'
    'kp+S05HcttD8bSafVxexNC81LfyIOiRgSqTE2UbJuB7+lfeUmwQ1tTyZZtcpIrxuTod5dObVm110Qrvx'
    'i+BB4sF/LLc663DZUk06IZgqyN07XzYfD1+vWlJDgL/jjT1ki0lyo7Leb0jp791wRE1fpqfb4whlfmev'
    'szmkD9qGurs9QBOIbA0kyT3AcpHOmESI59If5ftekOuDQTbUckw+209kemN9A+lVnwjy4WtpYDwLgUHN'
    'atufDCwAVfpE2ZUQAl+EvZDeUkW9FzzxgG/jO0gGX1Y+6UXmDv5lxg1ZU6SHxTU1g16wdAshwmPiYyDX'
    'xWIj0HX7dkotW9wiM3tePZiu/o7G3FRn7Bhk9YJEdADMLdid/iCGrmjJ7JWYKRG90Ir8apUTtb7l7z2Q'
    'VoIL8jHj9CWgSukDmgX/Fl/tI5KTUBllRCYLyTZ8UfN2dG7GzDGuJ8vYMv1dopDySw8zLKIw5hV/oVIC'
    'NXSYR24z9lneLerEbLl5ybJb1oOTOWqFXWghKguFV1XNiuVw9pb532P4pYUCKX/NzY0CdPZyoTBAWuY1'
    'jQWX1Win7g4zsFb6vJWrTQ8Ej9xc6QaEqr+r9cWEkCdTsua1uBrsVH4pCYQbcSPxSkPpJYMarhh+ZFhp'
    'fTAQN9XtSRZjFt0zJKkHRnrSuLDED3AOvRM7IRaMYW73RxrYHSHoYvt4FL9JvEX0VgilC9ktJegP4ydY'
    '7JdtkpAQHXQefWnweyKJ5HRe7kvEmIq02uQiO4i183eQ1Fjn0lPe0Hc0GFt9Y5qKliQ1bH2RiDwcGLJI'
    'gcZ7EtiU/0q8ZQYKaXhPH8OpVZYCEhQIUWmrc4DW05KBf6uBpKEOTCcsCTcGpDTK8N2V3oniXs747ZMn'
    'YKPoX8a+c+Wxkp77NURRt086li+gCTUAi8NKk3wQD4Xb0guq4K74+49SBgu5SNGEl6GKOd7A7GzvGeHL'
    'vWCyxGE46yNHxkmW98IommV1toYhIM6DtclJ7Kdm6T/HwMxUN72ag96tp7rLA497lCZv3zFybZjH9mb1'
    'XvkewSxoHDhVD8bjGNnTiObEwoCIIFUpJqbCZhjj4kKYNPjb2SEBrU1h60p4a/B1okaTLmUuoq+62oIm'
    'ssJCDLEQoZWn9Uc0aLGHAlMjTg3UBEkJHrYVMg3fZTFvUVlas3SNawp9CTLRkveJ+Eo3u4irOeVcjlQu'
    'DuL2dR9Vny8YJZhtffmdeYU0muy90+JFdS4ZPtSdf5kZGXCMomlIuBwMaJblhP9IDgdxEDA6+Zs1Cm51'
    'osI9iq+Tjh8BEMIFI7C/CyF5qsNRH5c1frBt7BOJPi9gEtXSBVsQLc175Uo1Ym3V/VG67Cpi7qj9WDYz'
    '3gfukBnddRVau+GAQjKpOQ6tfyayZ54MHb4LJ2Y/WTbEgqFToTG5IUTvEKBv03oTMNJti1nEB9J/tyFf'
    'S0qofDka+La/Z40S8kpWd1xAKui9ufVQAJn2WhXj5Sm7F2w78dTVelD409mqXZRgwu2ie3wEWymHBsjm'
    'V6pojjiElOdsDBtySzoWSzq/jmTLIfuRCXpaYeiKB8UdFPiTiWsygw/WsYfd91eG7f5cL3/h+b26r8L3'
    'LZSe+CgzZyBZIRmecWVTJPyRnIW9zs66yjf9DSmicER3fFe1XTSW0remBV8z5+qZeF7NUMWnZNRsecRQ'
    'HpcM2Cpdki44dnGtK9Cy9dDumZg3FnBnbS/nTJflFMovLimUfuHf30kg94yIoU+9LCHxsLH0G8/te7Ro'
    'GhvI8Xn0WxBD8etbiXDJxeEY7zyvv4kJTu4h/8BHwGS6bIL+3MnLUVU4g0s+YANa+jVbmB+Tjyiz13h0'
    'jw/2FE5TDsqxNv4DHPXqKiV1pkQp0uSYYGyOde4XMJPjSpsNzVcmFPly5ZCVFB8w4PIpfZHdUAoxy7jF'
    'tVvonK2PgVszGcT3tt1a4qAhBiyPX07uFT0W/6jTAcdLg+TT1hsPzDrUCdNOZ7orxOdxKvQmdqyLzzoV'
    '2VtzxxYUZDMNOt4Nfz+WnTWc1o0ff58ZfKj5+i0Z5CdAsgQVJU5SZGwRx9szLAn1'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
