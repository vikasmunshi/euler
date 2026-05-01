#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 453: Lattice Quadrilaterals.

Problem Statement:
    A simple quadrilateral is a polygon that has four distinct vertices, has no
    straight angles and does not self-intersect.

    Let Q(m, n) be the number of simple quadrilaterals whose vertices are lattice
    points with coordinates (x, y) satisfying 0 <= x <= m and 0 <= y <= n.

    For example, Q(2, 2) = 94 as can be seen below:
    (image omitted)

    It can also be verified that Q(3, 7) = 39590, Q(12, 3) = 309000 and
    Q(123, 45) = 70542215894646.

    Find Q(12345, 6789) mod 135707531.

URL: https://projecteuler.net/problem=453
"""
from typing import Any

euler_problem: int = 453
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 2, 'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'m': 12345, 'n': 6789}, 'answer': None},
]
encrypted: str = (
    'AcophDTiCo0tu1PGepAOzStuPptl6HueCknJwml1wzc1Nc96cy1oVhQZqRaKcoYnt3F8SE+LX58Y7Abu'
    '6mx8wO6VF12OzvYtVCAKdeHAv6pM0NFVnYHWNvP0pcuGRH/DCV8niMHlgKQgM9DPhV0MZXb1kzZuaIZI'
    'xsrV3TJCPWx0QlrFut26ogVC8ft1un2tD5ImHyos8uCwVn5qzksr9LfBBbPUrz857Gaw5W17KmZ2JoRM'
    'ja24+EcQewxDUUfZ8uSxywShbusXLMlYQzUgoF7TykFjXcQjYY73r29jFSBR9C7VEpLE7HicnWmaa5qp'
    '6H7kexBd7xrJJUZ3+gOMFcGVP16q5BL3Zk1LkwVqzt2Vg5/bmb+zL8L6dXEeJ+Pd2iqTtsogJaPg+7QN'
    'yDL4/Mu02CRa9JhcvXwBWNtQD8aDkAc44wyzjGTVbhSU2FTIYaJ4C/WRF+jSwxYaojtLpnH75ACMbKYN'
    'CyHNxvjJFakuA5vGFxCFDzIoUcmWxA/idqbnoH1JGArmh6lvq/MaKWHX50D+ec+5IhnGg4fW4NezakNY'
    '1tuLtAM5TLJ4hb45sw8CbkMhZ7ixqT8D0kSfGYln2KCezBNNr0SwwDGpzP0mp4akP0ryS9VgxLnspGtv'
    '+ZEFlwjAMqZwMYSlDcXB32YRHzh3ZPAZOyZzKiHCt7t5yYbFppPaInyPYoqbQdn45Kg1x3dVUJt1UrO5'
    'YKQV1JxSAjySB0BkIZ1r1QDZfh1SKIf4FozqoqdmZC/baZc7avmyFhI2PBaNQXRtYBm7malDy9Cmf1sX'
    'MS/jhGklCHPkMMNZcemZE2JQehtFMB9uK5I5SLvq4mvWbq1MXIuZ5HZ+YoAttY0UCYvL381ig+WHkefq'
    'TUHxXGAMlSoprMMbjsZoXZ/iwyCDvhMOQNqP75+519w8fz21k0gRfByv5jRuE0NBiVxb6b8kfB+5yZvc'
    'fn6OZ53lllTvP/dLddDpcvq1psMOmsAejx1ZPEh5sf73IBpX9ZVfjukH+DY6V9M5dfq/hG7rt5VDXZZI'
    'Av9RFTjiZ7FX6phOFkvKvWfbkJvlV4Kvl+74IOS7cTln+oCuU1QYLaZndS5XodNlOW6oVqpGS6UAApIM'
    'rJvevdN2LJEAyDh++VcWqjQQqThY4Cius+m2F4xhMIds7JKfYdJ1aT5kmUheVUt/wM2Gssa3YaqLc0fb'
    'xi+VIUtKpUHMyBCGN6zFAijl8kTo0DuHlYlfMTSAy/Z6cjwha/oAit3+KxR+UekRsSGfTAY1gOUAHNR7'
    '6tmJjPgIEoJYtQw13caMjcOeA1LL5fWUWhzDRLlxxMHB0w/5bibNzp2SzPh5RA72zkDBLXOgIG57NJnU'
    'fJ7Qvze+4LqRTmnFjV7WAQQK/Jqa+xzA9y3Q39/8Kl9KLAU5ruvhbc1TO+MAfDKsr54DI9ryyzxvRthL'
    'JNnsRKpggT9vjCa/9sgwUF2aBxLilnaWIEcEIrcioRAF6K9KcXMmfok/SQqkh14WtsymvqttfyJBTKP+'
    'uVgWFe9uuRwHrlaC1E8hCIPrN36Eh066a2kpn8d5+VMcFd9LJfXYJi9ey5fEpZB1n3l2cc4Cja2K2l0p'
    'uaA3Q35RH02zEKqPRDDjGM8wjB0LZ6scIMVgOH3NqRRAwaTdWt9SgRKhIeQE5U2NvnrHoR8DRkgHaMWi'
    'QEnV/hQHKjWwNuUFzYfwEGzjj3GZOR+oYw0JCxSXL7w007tpBkBV/7eIMzTpHppm/HXyptjsy7oDuHYa'
    'YRtB93xqpa7evE6VvtbU7vqtDPubwCO6jXhWxWeugf61Yh9dis3hXiVfeIWCfTyD1nbANrjlo+whQsHz'
    '7MkqBhhMuMskrQyVNr6SFSrvTfjw0ZpS3PSWTe2a3AE1p9wb95wRzcy4tU0UumoyjfzFC+a5g8rzX6J1'
    'a0gZCuBSPwLpoo5w8ZoOKv0K1Rz/Xs/4Qnc4vfIHry/pM4nKJj8FUMUBqg4PEXX8LAw3jaRrNjEbQ+m8'
    'fmqp9dUDUERAZuvw4KdYzktkZiRY+ICJH46ttiWP2+wwRy7J7n0UbF46Dso6YiXvQJaKLBOFsrtnoqH4'
    '5W50C4dMOcBYTVXykJ3bkTxrM4toQnRFkIvvrs5z4dUCTSAfpT+LjpDCzxKezAe0V4gqGusHUErTzQao'
    'HQrDAsGT7pZDF7R4JwxVGYuq6+e3uOeX4Jp4h4iasGm6Oy/zLCnz+dlYL4V+/2SwYL9EnYZPXiqDImtt'
    'APJb5gIvh1D4O/VeR2LbAVrXYPd9Gp7/684NWDjZiGNm5D2SGbpM/fe6XKxdf6lfdzphf1qR75RWLhRZ'
    'IhCIhOFU+ZI2khNKMwDbBTsFZsIFQcaP2w8u00odBir+jbevMs3feGZ3rxoLBDNagii9hHlqteRCd+rD'
    'jnamFQJEaVY1FpHn/QGyDNKR+VkMkg80vmzOarwS43h3U7SMqgx8LgfieTGGRchyMO2FxgtOpBNIZ5G2'
    'mmYgUbLA3DNo5YD6M6CBS4usoy96Rms74bEoZCfQfg6XVkkKsZfTPkc4uC/b4ebo90Cy9b+efc2bpf4J'
    '4klJzKrCdM8tq4LM+p1tqplx6ZJ+Kqxhg5+HfSi7pcX5A0sjHPtzmu/Vgq/Dhq7UvCtE8SfoyUlMdCxX'
    'qrHeEKsGQx/W6FaA69CduDyQ7LLp+adFh8mByB2xD8AeOcm/880xi3QkNJk9zf5sHyS5ocFWX5SBKjSN'
    'IIv6yu+vG1p+5cNJkUSvErKdrZPKAg29BAq5scyKa3idwOBKHqr+NdkTlH2G3hm6KCqO4SXDmH4c1nTf'
    'd2aiOF4DLcnTHj3gb/JCrNGAKJzLw9DFUGCsVg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
