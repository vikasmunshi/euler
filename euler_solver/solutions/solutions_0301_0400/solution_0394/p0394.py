#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 394: Eating Pie.

Problem Statement:
    Jeff eats a pie in an unusual way.
    The pie is circular. He starts with slicing an initial cut in the pie along
    a radius.
    While there is at least a given fraction F of pie left, he performs the
    following procedure:
    - He makes two slices from the pie centre to any point of what is remaining
      of the pie border, any point on the remaining pie border equally likely.
      This will divide the remaining pie into three pieces.
    - Going counterclockwise from the initial cut, he takes the first two pie
      pieces and eats them.
    When less than a fraction F of pie remains, he does not repeat this
    procedure. Instead, he eats all of the remaining pie.

    For x >= 1, let E(x) be the expected number of times Jeff repeats the
    procedure above with F = 1/x. It can be verified that E(1) = 1,
    E(2) ≈ 1.2676536759, and E(7.5) ≈ 2.1215732071.

    Find E(40) rounded to 10 decimal places behind the decimal point.

URL: https://projecteuler.net/problem=394
"""
from typing import Any

euler_problem: int = 394
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'x': 1}, 'answer': None},
    {'category': 'main', 'input': {'x': 40}, 'answer': None},
    {'category': 'extra', 'input': {'x': 7.5}, 'answer': None},
]
encrypted: str = (
    'RL0cBRew5djeMFw7rxMqjgUviPPq/XeqJYyC56rdMFK0NgtHWQUf0wj7ILVnJOM1umGu0+6gJthamqtd'
    'Nkb+T4frKsucr0mc1ENfA6w1A/P6gZgUK4w+BAInyKxcX3+vGR5K7jM5lvh7CjANI2da476DcM2F/cky'
    'Kd4CBJE8+8QFm73psBxgQFFyO2X4uUw51rSmty1fQugMeszzZDxQ38TcazLq4Ieg7MJ/q+dFu4vssgNC'
    'F0ltWmRi5/AzySYEpCyrucz7PmJ3nmGhKu5sVDFQ30cUigdnZe9LpKPc6cdyqwutiP4n167RBN4/5GD5'
    's/0Eza1mqmHyDJkn+6tVqDFzSafBp/IZR3xvkbdX+xRD9nqOcOQ+OMXHjXSIRNdyqC/qDCM+bZ5D2dGg'
    '+147FmnoccGyFiXJg1Vw2gc27Ycqc5Bv14laZnOJLdLsdELEp1oqnRxI44KejNlbPuSnDxi4iL6b9EbO'
    'uoofSUB+thHIe+n5e0QpSZCvXDE25OxvJQa5k810n+mv3r0ckzYp681Tb0p7CRcnPOel0+J+/Jmf2WBS'
    'zJujYmAQoMCPxFMgEluDmhtHjVVG9njm+f6vTN2XUrbX9RAZ0kTN4zVWH+u9DPu8+tbFhgEnyaVkohpg'
    'uNbGiyGyG2Ty3eAm7Yebf6fOuBzFduXHsyVIHvqKJG1ubOEqIURAODNdauaPh1eM43rjWuFtbZ2D7pZ7'
    '3mClOoynDr2okiT7sE03SDaNl5iTXk0Ya6YdJBpfSlg/eAfEeFXtJfUIN8JAhNvelEXeBHV2dEQmmVoj'
    'Yp7R0Xb885zhoy3HdVY2CflX/FF9l6oLR2wAb+ISJXseaFlvEd2rbGdbKTsNE18iHkuKLp4dVwNNdFI6'
    'aJIePGd96aFrPMTsJ51gDtWcS+FuXFJbqEgU1QFidtH6shmd8UaX8BTXwOZ3YFS0MW0pOB9SgKM2DuOG'
    'lC50A2Kf63cvZWZwZYB/fFKyxf+fs63euM7Oj+aMtoqgbb7h9sHN1PLZd/lBiPoz/aoM6cLrX7ere+PF'
    'Dhn+/J0gq7L6P7AeN95m20bwbdJ39I/V8ItMCSmR16w/hdphkPZyZ5vEC3fJa+UOvtuXPgB85VzjtaDn'
    'qGkyIGVqQ2JngQavxA9zrt2/sEQK0TJ1OQac8WledrUmbUWcEI2WtdMuxI2adU1Bqhe2FShYOm9ZGdIl'
    'EKTYMvoOXUwpwlQCGQXpFjYih/AvGzurkxiyQm4Cnso+CFmVb14+FiAq52aIUxrtD9DcXFBU7HQMNC6l'
    'k9u4la/ZkkeW1+HDXaJWJlcS58KEM6iEGHE5ebWH3hV/HkLRgwrdT8OcAm1K9sxlcBGIcrvlcma3X6xs'
    'CQbzc6e95DMZlSkVnHp16gbS48gE8cKc7nZu0MAWE1alBcUy/0x/XkjV3+2ANzqQ2zOuc8cNm6cHMIXG'
    'l/4zBEoWoLCP7Zx68RH0Uv4vWl73H0fxQBxeWVuHzwBC1v63xLAVPHfTKeITTATdkvi0EzOVRsos2V0H'
    'uj2CTPPql4rkF1DcTAsLbq9ITXHcDi4c3EYg0H3K921LbimiNuma3QPhiha6PrllG4jCVaVvTSUw8gJj'
    'rOVeRsxota9K2sdk/E+5xcHdHY/07I1uUVJ+JwIsPxiMiUPOFjKCA7I2B8XBSqjd1XncxM6UKC6G+fFi'
    'gQtgFNG5l50d8dm98pHPMJfuW2miKDpnLHKPqilAEGGqrpBHY6xxLxZoBB/aoPRc4iibL001N+a+FMJv'
    'SPDqG7KAHWi2UA4vH4lYuZhFs/bOQQPHkfricX+RNJLUI1PC9JHiS4Aj0njJ11VoiK0oZ9Uk7nEpmGLH'
    'Ef3xnu4SpU+jPcDpCmAU71bO31MYOYTBcbAkL1xe/6/yYH7BrRDXMlBPmOms+3mt2Qe+P9NCPkkNUv8w'
    'K/xaJfinlg97/nBbUqnAKFbnbzlcYd3PLZmhlM3pYR4sHt431t06Dq3L16WjK6drBRiKC/p5uCGgnkAU'
    'UUbenfpTFg3N6vs5enipFUKGhdOhyGHl3u+MfYdp4wFWuKGWwTJ4jbwCQWO4TYH2sjNe7XC5aS9vdwUU'
    'XJudtfcmdXODzeAvHZtDe2wS6b7ILZxKJJJXTsrADdXavMFIzQmPAy6pXUyq0gdgW4kcjYpTpb12pRFz'
    'L876Q6mQMitqNtbm+CyDD1zY95M30YDD/yV4FonsW4dWRt6K8kwQEirQNExXh7QAyO0qK50h4jOTavJ0'
    'BoFfT9GW6XOeaGxITe8NNMsd87VfCtAU32Q4Kfnuc8HWhO4o9rkD0G2Tys8kkNSONKzvPmRhfnvajhA4'
    '0zn8F+LJy9Fyf+rMkOrRAkY4y12U0g3Onk+8zhQkrNKcuvCX0SHNDtLRow4f3+VesiqbSwlZzThHUBob'
    'rHS71+uAq4KDMUm4dCwfisDTFJWvAmcCzdClwjsE1UdvZcmFjujwE5qCW6/cxpsB7aDru3PiKTApJlQ6'
    'ibyXizDZlAs12amorQdXW0yU5j9UIn+jUHdyzijoLw8uDvGUWl0gZ/u+9A5NjdIOeve+tzydl8SOi00P'
    'J+WQV8Dos8eAZ1o9Oachw3H+holKiSrd5npLmdj4NN15mZByoalxuxYCO6eXZcCfl+DbnSMKsN3vWpv1'
    '3+9LpWGVgYlyveGeb+PtTnWmVzikkhCujS/pVqwagi1Bx1lSDCDXdpDV0bQjZJeSgOJc7RlcYiGpBBfT'
    'OaxIfTvrYCspNyrbf7xVHxhBxsGIxk003ZaHFoz5QU/PF43oVyYONssZREOvS8vGVrWIjOh8aG4OhE0U'
    '+2nDXEoHbSfkS0aGjHNX7neb6xzBCGJVfqgsH5RCCI0BwqbiFoAd/pQqJbDbP9gUH/CEKP2RUUVaoAeN'
    'KYtlvwvJSZzgPtK+dMvCXsNZdHGiVNnc9TMu87WYk6HIeSSvhbNo3CBTRMErIqRJ79IlJzRiENQ4zyDb'
    'uvjRHH3i1bMLCEtCrV7m3MwqX5fdM+x/FazmTZJ5H3G5LVlcWTR3FA8TDYBNhGNtziQ2QHSyOdaghGCt'
    'tIIF6FclLJKVAgg0jwb//3IxZHc469BBzVErtDNQBSh5j41N1VXB7cBAz3OgVuWRlh0umSW30n5HACOn'
    'Zp99WHrBaAvxPLm8bAIRMFzAZ7KYMz0l/5e2jYmDU9HlVNNW2UbUdVDa16UL8SmWtndz+4LolBwEOVkI'
    'y036WpaEjRW79AIV7jZfaqu0udjTVOvAp98nj6zI+U5uC6BvsgkzbIqsd4sMVlnadZuVJgeyJjnBW1aK'
    'M+CFAN4kthvoVYfLUZmw8RsbJs2fpsWwlN/RL/aGAq5QsX3ia6gqh5nIn67oWFezJJh4hWt9eQUcXxpc'
    'Ho/EQ+sV/jwi0kDk6AgVbyM9YXtoudHYXo4DFuSBUMQYbey5w2MntuqEh+7agVXzylH7TrLjaWuotsPk'
    'q/Zkq80wHfQ024AjGCrqayOmP46klbu5r0cWvg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
