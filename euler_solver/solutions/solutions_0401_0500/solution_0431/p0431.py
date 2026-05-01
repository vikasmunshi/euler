#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 431: Square Space Silo.

Problem Statement:
    Fred the farmer arranges to have a new storage silo installed on his farm and having
    an obsession for all things square he is absolutely devastated when he discovers
    that it is circular. Quentin, the representative from the company that installed the
    silo, explains that they only manufacture cylindrical silos, but he points out that
    it is resting on a square base. Fred is not amused and insists that it is removed
    from his property.

    Quick thinking Quentin explains that when granular materials are delivered from above
    a conical slope is formed and the natural angle made with the horizontal is called the
    angle of repose. For example if the angle of repose, α = 30 degrees, and grain is
    delivered at the centre of the silo then a perfect cone will form towards the top
    of the cylinder. In the case of this silo, which has a diameter of 6 m, the amount
    of space wasted would be approximately 32.648388556 m^3. However, if grain is delivered
    at a point on the top which has a horizontal distance of x metres from the centre then
    a cone with a strangely curved and sloping base is formed. He shows Fred a picture.

    We shall let the amount of space wasted in cubic metres be given by V(x). If x = 1.114785284,
    which happens to have three squared decimal places, then the amount of space wasted,
    V(1.114785284) ≈ 36. Given the range of possible solutions to this problem there is
    exactly one other option: V(2.511167869) ≈ 49. It would be like knowing that the square
    is king of the silo, sitting in splendid glory on top of your grain.

    Fred's eyes light up with delight at this elegant resolution, but on closer inspection
    of Quentin's drawings and calculations his happiness turns to despondency once more.
    Fred points out to Quentin that it's the radius of the silo that is 6 metres, not the
    diameter, and the angle of repose for his grain is 40 degrees. However, if Quentin
    can find a set of solutions for this particular silo then he will be more than happy
    to keep it.

    If Quick thinking Quentin is to satisfy frustratingly fussy Fred the farmer's appetite
    for all things square then determine the values of x for all possible square space
    wastage options and calculate ∑ x correct to 9 decimal places.

URL: https://projecteuler.net/problem=431
"""
from typing import Any

euler_problem: int = 431
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    'vIncXQH1FXzOvP9WafbY7+IAk5xglUWcLa9XLmbkpduROxconZSB1LvLGVRUfq6KJjDpyBU49JYuiMni'
    'II3YZgpBWto0w5noum00XvNUwjUbZDvJBpGefbhY3KzbryzRbx0eLq5y6A1/le8gGO97v3+wel+L3MSy'
    '3FcPcDHDHueMsJdygI2zB7goiZ70QmDsxj8HxLOenjwkAN7tau4moYh0btt/8bPlcEUcZ+2+Jmfdo56r'
    'VTflE6eXyvRvS3QYw8CaogYC0xkwVJ9LHK0J3RDc+saT+lI/Dt8L1DJRQeiMKQWpqBZ3sI8FjoJf79aM'
    'Ppz2FQTU85Co9FiJqPL5442MxyIPw16KQZ4S8G23LJq79+wbWP/LOUAbypWRO3faZoUli9JXz8Vvloqh'
    'UbikYixNNuZZfDOc22CpgOmUkowvPHqdxMM9uTVghYnOJkiyzqsX8ulrWplpp+oJ+UE2cTkCxw6Y7rlR'
    'XC5s58WMTZc+EYwLlGwWNbpVqYe5R8Q6W5EsF9H/VuAg6LmL1VgTUAjjsks6PhUBS/7B8WgNQewW7Cp2'
    'qj4abFndSZWFY4Va92neOoLxLvH/7Nbb5Lc+gpKI9rTUdTnxe9SZyegf8aEGGaaRAymIvs8Vj+baDFQr'
    'tiA74zDyJUhpdDGRB7qSBL6UfRKEeKcVleh8Fo+zz1+V+tJCp9DXYRgU/ZjkCW6VFjtS5AQiUNeICoya'
    'LJ+s/QTsxUEuqcw/QqGpQWV0t1rFKsPgrDZIugX+xNpksIa5FXsERNNpb0p/dKfAypMp2ZKiDwOb+vMo'
    '3mlD0BmQpLC2wNXCJT2VoD6aLy9iexUSx5ZQDJXMreutmP/sTSQEK2tSttAZS9qQX4+Y7nn0h9fYatPM'
    '5L6BgY6RQMNAwxFHHboArZvBXkrVtk+/wu4nxv1Su+tL6X8nfpMP/KOGEzL3VzFjxakz06lrD64uvYKz'
    'PlQu4QNKxMGHBqHDHHRyB6G4gvOOzFQVnjBGvTr0bzZ/LCwT9mUpDTbnpHgkMfQgemPbCYxRvUTYW4T8'
    '/63M5TyrTuk3FMg5CyRgiGBl9kAkLgOz5H0mWtmlDYKYXjG7N/s4UviHxI/wZboMQvDEljDezEB/teWw'
    'PkmTCsbK7Ntul4Yx9WpjvWmGD3wr6PdyHnF+vdcOgAbJJ+PrZdLXIID/L/MLtkSMm+8jHfr3qAGSKNb2'
    'Bj53LTlMGSM+iJtZNH+i2tXsMpcfowKDItn15NZEa0GBPY4aAbf3Vy1aH0ck8Cxxemqx2Zijyrt1B8TR'
    '4OHFVJs8dYvnmGfIgmmoSeOiOf10VcZnnjGw8N+Zt6yj/nPMpS7ZEPYHP2uoUY2gZHOwMLgl0EXQ2pCI'
    '8mf0BIYRxe3BQjt509u29VuhVltR6MQzgNVzhIRB++XKCErvNJ8xtvcFnD6DV3A2NOhSCdAK/UTb/Pcf'
    'EZwaWB2tweIqMhi0+MynpP+vC6nPlyF2diJj4ZQx4Xc0oukfsEHVjnBFbd3Ta0a+GSdM8Uk4OvG8HUCk'
    'oRHEsek7YZfgTyBjOe8v4PGdNLzKWp9yB0ZMxPEmTgmpI/163kz1gc+Pe/1uV3a+v3PPZFyXjudXWmB4'
    'uXJt0VVxzCGsN/9WNHg8x991RpE2zElRzld3oXfesg1+QHMSMshQsA3k1RZMScJNXtZbBIL3twQd0ILM'
    'taxhSW92sb5RCndbvO+CMY+yJq5RqUJkX8wBNgUCz0qAx3fsrjpMEcJE2Nist8s/DiuL8LLM+6bCM8Hv'
    'qAO+XXFaF9Tmed8eYEn/NujRXKo7j8sniEuZatTvln1HVCE1jj300fe1esxJh4qQn6gIV30B5Oepq+3/'
    'l6PetYX/UCNB5NDVgRUAtSaCt/pRRYy0r7o+ztfEFFIWbMdptciq0B2LkHmjmScNdr4LRB/Vr2htRZlN'
    '9KeW+gZfUwWWIOduD3Nqlqj7sCAWp8ncttV8SbZYxmkWbWZ63vn6oSKu822EGU3WuEYpxI39kq5yyuQk'
    'blyl/tLwd41QVvtNfrtxGmx+d8WiNZINMgIod4fxkUNpBX68CQS7uw8bIpWZVeJOoZG9ihVU1hmfqXj7'
    'KfWKb4LPVlMaoqwX6PyPWfRrwjWvExGAuW999GCE/s0GEN6UXDJZ1fjbCPMR6kJH2+AbAtTEQN3XHRRc'
    'dr4YAEQX7rggHPaVwiswbxKO9lCp7dZo0itDkdDRvkWTbSwaj8PLjr5Lh5tb/0vwA/w/JcrigT7nNl+9'
    '/SXVXk1UOCxnRGtxVjpAwUO3e7FFqGvvTV4fQd5yZyT6zuVfFQvcbRlrVRWKVJATRJrGpHXz1+WlQhZ0'
    'cloHRQ/r2qZhW99XpITdTxY4GMmEMlg6cd3QbD/4tLivAVnDHbAVyVgrv5C+BHRTd0mplemI02sKnrCD'
    'RVvzlWBxbqXdDXhiZCLBalkLanLqbFzZSIUrRJN3wVe1HGfpCfB9hpXcKiA0lMPXu+unDh4pTqGD208m'
    '2mFmd7Tt4a6oi3SjXJPgPdiI8zXy7t5pSLNmjvh2KzwtHg+bz955Er5FudfznjM0Nxfw/+aTRfrRv/qh'
    't8Frb+mIHPzeT54DxK7imN1deygIlIQRWv5L78B50GhDq6vzoGtbzjesV+2P4DgqytkUUcJ+z+YV8F2O'
    'vZnxpeS7BLWScHQKeHe7mRn0FBFo3S47enRGMwPEL/PkGYcBUo/3uAOhUGw8ER/WzbX3mb88An9U/31c'
    'uKAYAcse24hH+/LAzvJ+bArD36AagkEMTANccREI3OeoyDskDsfFcDIpAdh+A9TqOeYsCTJS2WdqBnSi'
    'npEXmCjzOWrxZ1Y51yOF4/6kgB894koPxWJNffLoam+5h9Pryvk6/sHA1MAWe+9IN8s9/sUXBe0T8DTi'
    'Cbw9ir3Xw28KDHMrMQZBhL/WnVR+eBQ1WWew3EbYrgHOJTC4J+EqFhnMvOhgW0nQMyMpspC7GW2pBh72'
    'PySTqVEXm/FvPB6yYwBOBzrz1nm/51wt3MpbIl2OHrgQXkrX8+G49vhJGhxwp+TGr5t3VYa/+UdYVwtP'
    'LNL3jex2N4myTclBWR9v2/YJ+SlBZXXuErEIKIgd7UmsNn6Ds3mPeTEMFYidsEUaYGsE9pa4LMN0fWd9'
    'blsRKX3A52gqkmGnAxUDjDdEeDpxwlzOLumCZw0xMraYXZ/kHTqaB2CABg8twOhfYUs+RvobYmj1Vtdx'
    '0rrW9NCZtaiVOHSRXucBmwWKUiibmCWEk7XqyF/YXdyhETEUlY9Io91vI82bHSJCUnxZa0Bno1UjoJow'
    'D/dNBtFvA4Z0QUVOaXf8HyyI0rFwD4FEboZo/nflfKgVeJyY782vDFC1HyCXiOTi25btyhpCyirj/gMB'
    'gX0IxjAmqbYEyqIBTGKOGulleN2Qm8Mplj1EGc9xfSv1BgTn4nIMzaUT0np0+6rY3TAlzQCJ2v1ll2mD'
    '9qSLyaQzvTszSi/Lw714PNo4haoaGaonf4xLNiyY+4HzNm3mMoaFt4C1YAZeaHZVYLbdBMsinxgEg2n3'
    '9fv8e5X3hDXc24vX+KjH6jEdi5QxJsFJgLLh7onh+FqWPDodvzXuyfa5LF6qeHGjysAG0oQMEfhUDLUH'
    'FYybAC3dkYaAL5NWzQjNIedD24FoHNZzYaF3AcZ7P/eYSdzMKMpyVvGW6QIn14LqzujRh/d0TaPJm32q'
    'ohe9f8XaTcFnrwcjIgJMmJX/Ni0K/PMvOtj1I0qTFJ7L9HPGqNVf9eyrwdAv5AkFUEmBC5yCSgK3Htlq'
    'gWooXThDvfVDx4KYb+uGU6KR3iYPTuxtkXt4iwpsAPS7LCUFZl5MjrpSAm5yAboFFKe7AN8LezTZneJs'
    'meMgDTXmMEFBa9tRuXvVAQDapDrCwWPd5fadGRu3+Y54/Td2VM0AoXdPD9BN56li2io2USPoEUkfyGkl'
    'jMRSAI6qQqiB77jfgvX5VF/RL+yn5odKIvd2nDJ5OG/8gFD3We+s5rc1mamHiTZ8jQU7K+ObSIowBYlJ'
    '+BrPn9acDqaJfGq0AqkDK1e6e82T4eQPSLVsAhA7SQk0meMWwVFx6skZzNB5scoMr9adJIu4QYde6ctx'
    'rHdXI3x+w11KxPsubb6koGwvGCxJvmnGhHoNe9Nl83XAcDt5pu/EuoM6XrEv1i5laLlAl1TnXZ/Z2oIf'
    '9HcISeopuDLBfn0bR25l8P08bhSIbfVTKXrPQo3umjBm+k2L+VbgIevftASogLRk2ZpGpVK3eZ5VzoOP'
    'V1M0EFbVc3A8bUuA/dPQLZJl1OKgsNot7JgKl7iM8xAC65tVASrH0Hh45g9NrWe9KgzNV9jtSOstBTgi'
    '2m0gAQ2hhg7HZulz103BWcdwpjd0cgUEPhI2z7Hioger/1NAsebh0JjQpX2g3E/ul1gAHOm4cbrEq+y1'
    'pEYnRqwcIG5J6NSe1xJnVAa4j8w3WGRlAVA4+ZI0findIhkS/bEAkE8hgckfPiEIqJuEawonlAIRN9CI'
    'jyk3QwjhMCbWQU3pXb3asuQhCFYWdz/Iuk831j7FFGFyuxR9ot2W1FXEPeSejKaS14oYw5uM6JJRKLoQ'
    'RyXJhR4/OUpamQr6O8GB9ApPNKT6e9INeXuEMX8yEJ6XfndtnwrJFbRZwaxpGkaULH/B5HEc2oocXnCO'
    'XIQVv6v9KhBER6hrwlvjmFO+wj9r4svaRZMZ+uZb7pN7xc9OZ9t1n2wVPYmUh8751InAJCJeSB7Pyxk2'
    'mpzxT1B8yuqH9Zq1P09Ad/OeA1FYcYcRJPXw8umN0zUS+dHh1ONMpMbPB54VUjsPx++qpSUvGaCiekbt'
    'OyWjyOT7MiPCSYtbSBCTLMpM0oj06EmThNOR8h4wQQJpEfV/MJq5AbBAYC+atmpNGpT9ohk83BsilQo6'
    'nepuGSqtETY7RPb/3UULzZ+EPasph6ewVmhiQWSOTiHpO4OjoZKRPu3J0o5YDx7trcbNG2YgzKn2a95i'
    'CI2VgIXe+28='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
