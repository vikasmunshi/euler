#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 150: Sub-triangle Sums.

Problem Statement:
    In a triangular array of positive and negative integers, we wish to find a
    sub-triangle such that the sum of the numbers it contains is the smallest
    possible. In the example given, the marked triangle has sum -42.

    We wish to make such a triangular array with one thousand rows, so we
    generate 500500 pseudo-random numbers s_k in the range ±2^19 using a
    linear congruential generator as follows:
        t := 0
        for k = 1 up to k = 500500:
            t := (615949*t + 797807) modulo 2^20
            s_k := t - 2^19
    Thus: s1 = 273519, s2 = -153582, s3 = 450905, etc.

    The triangular array is formed by filling rows:
        s1
        s2 s3
        s4 s5 s6
        s7 s8 s9 s10
        ...

    Sub-triangles can start at any element and extend down as far as desired,
    taking the two elements below in the next row, three in the row after,
    and so on. The sum of a sub-triangle is the sum of all its elements.

    Find the smallest possible sub-triangle sum.

URL: https://projecteuler.net/problem=150
"""
from typing import Any

euler_problem: int = 150
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'rows': 5}, 'answer': None},
    {'category': 'main', 'input': {'rows': 1000}, 'answer': None},
    {'category': 'extra', 'input': {'rows': 1500}, 'answer': None},
]
encrypted: str = (
    '2iCra6FFTVwphi9rPvsBqVweLW/NL2dKpvKJnFx0/PW00piUcO0NEBLL5bjxNBWAFFtoqHTHTTywdQY8'
    'Ys8djZDghmdmUBdlOePkeqYC4xcdrcBUon5AXfyikHu5FDFNNzlCXqq/cgmd+kFSKhTl3km/IbCyEYu/'
    '7sPjFrX5Hy/HFhkNYOUqVFmFCkW60gE46qsK0S4NG00F7RgGRKZPSWxTKnGNZbi/oaSc6QUnx/NVsFcv'
    'YfSTyEhOY2SPBJuS5NiO1GYqqh4eUTOpBWMNgqkTsH1HzSOBrjobDYwU0lENGgsoXZeVkcRDwqKspHC8'
    '5isT2ErN5SCf3LBAhNIOvWyPs+v9GEI/bu8pLwaTx+v/anTBdHKKH+FAvdb/uTQc+1DBsFMTP6wBr/D/'
    'PMa1XsjTasPpOyn78hp14Ac/WTkHUeZeDcJtOok3K+kn08RdPJATe2TzGd4F+Pu9bhydfXbTyfUzc2OE'
    'y8M01780V0a8D3r4s10KBWloVLc7tVnk5iRwpt48cm2BW3JUkxD6ua3BLc3d3x/ACqJQwHomoQyQe4ne'
    'fHW8YeG4xh7pYkPZvtiuyp+FpzvG2qdwJTK/AvhG2ONRpoXuzltfqo42G0/DzwmGu8HWtNI5PilPJaZL'
    'KwugO7NBZUlwLjL2ACX3RESRlGCb+fzsFUbLlQd2nEVA0MRSFWxsF4xAAT7UlTeqv8JRMsjC81oc+dR5'
    '6VX5cnfMGkkbYIDRjX1rXFyDaT1NclCZU2rqwMqt0iuXMA5+U8VJTrh96H0qojDZgB9Y1vyd9H49Zjj/'
    'wk5RzEHOd+Hc/kfZKYKu/6Cy/mG0YQGMMKAXh7DVpwP7TF08rz8pLNGfSqr/idLIMgT/7goupm8cpL/E'
    '+56kFct1NWl27eEFPXQbYBxzZbopUR5Sy3nZE02yVomR/JZecVQgm2JrIlbi83JepsuPsyemVv1XhLX0'
    'eEPIBQDw1PsP6npSZvRQ+7T49Gp5ZNIA0GlRypMYplGQD2hQA1w4nVl5RtaBrBm3ZufMDtM2/AdlGjdW'
    'bc6U0QL30ckg0m3LGuAnb5cfb015f/DDEtJYPf/68dh1RVOexyrVFuMbSwO8aFS+0sbL/Lf2T2QRTCZj'
    'uV3VC1kvYEj9ogTp87Zr/bIBNINo5oNUVd94JpHeyy8w0xzvMKcSDkOSv5hpm0w3BkmA7X/AsOmj7vbj'
    'kP+Nz6UbI/EcYpTjRmDx8QOvJj4PSx3J5r8HcGVqJzSxDcBdCwCqJ3eBZKSto4OMzQmbB47HEjCkWcnL'
    'W4lXrSyfWht7yC3lMEv7paDCDh2M9vbT+Nip/P3+m4gKIxvUznhNfLwyzJ61wfHfZTVf07Tb8Wuf/X78'
    'bbF6LUIKWHD8ZXHvuPY5MkpIvBBmHQU6N6K1CdWDrYJXHzWyxrhXjq7AhikQOaOnrXhvosCxJ0CIa105'
    'dtvhywpu7yutah6UBEkvcX2+Avskax9nMXvDV23iwnVeRKF2H82cBef97WJL8fs/OPld+iash7LQRmAd'
    '4ifmDNzFws2yeX4mkc8U3g7QZoB/HSUTkhiKRQ3FsZWTWpsg79paj1unlR2EtpZ6Tiu0IAxPB0CCQGfO'
    'i3ktEnlzqd8djXXH0sanH0tgeEDzmIKj0r7ZtDbuN+GfbhxvFbjp2SXk0qo1+52SHyvOpapbTPSGT/HT'
    'aJS02I4jnffDdl3D7XsYrGu8MH3zhaSvgQdcjYugz0khW/GVCoXdMqs/+BUNhgoRZTj/S1PkMsL49Bnj'
    'to+uHjlLYAOyi4HUSg/86bzn2rmTqSItZTRv3r7P/gIvdb37Cnkht8+gYEsxl2CwskpJFLVX2DW+7qX4'
    'v62IRXjOpkfoIqEqPbRr6mHMKUaavmmXENij7KoNWIZjFf2hGJv6pnHaKAq7122AxjxJ6LWap3x2xcCS'
    'QsAgmfQ1s4v+gsW9rVvZnARJGX5wfMB75tcVqzbmx/7OrOXXXMnxRwCb5sTj+/9ZLoqWV/XuQIhxw0E1'
    'Pr2Y7/fq1ZH4dGx/ZZZPqu+eXkcCtUamWD0ibQOV2qoQuw6GuScXkQrci8+cJqWs2AbM8krABcCh1YZ9'
    'FyxZdO7YBc1LMgLYKDFF+W5hHXs1IroRwV4ouOPvbmUCVATR6kNWC0f16ugA9RJVk0bAanGCLRwuidVJ'
    'TXYNAlNVyj/DxsAHH3mH4xCUHvLnRorIGOOc7mfZkuaIbrGb2jRe882z4I/wLEyaAU0TxrsIvQYk9VkL'
    'aF1NC1BrjGcO3Jlf/9C/4d+/P1skUcf75jAqL/24mTE0Kn7CGv2xlFm/DgWKGU2PHwXJc7a8lNIvMZj7'
    '7Vq71KWGkOufja7fxvI0u2eav1PjlOgEcB4RK9hJPn/j5JTseGfaaCSPeILUkgbNBn86Wvl00HO96r41'
    'tbWqRl7SCZdr2y2rqX5JoMEqilJFDJKQ10uZI0gWDE+uOp7ZQHRc3sn4xc97yi2xESyQAxcW+pbV66VB'
    'vC27hvjyqbNCriIwr/3Yf9X/t8e2Wdp/rqpmXi6Lor0TERHzzq7Om6AR4Ot1HKxYEZbkbZUJ+Z/IlS6H'
    '8laOkzn/bxtMPI7aorNH0hCTX5UlaqkZeIF9xlD6zLRlGidIQnOXjeOiS0I/06NuzdhdVjG2yDBrvEuy'
    '86JWT++lcHxJmUM00ewHan7CwCcX5Y62oVnWKqScle5o4u3LzLceq9puMWovNTY53GJWfN2cqjjwLaTH'
    'sADxI+PNTqQdGWiqfX22iS1ZcO02dupyZADSBwAsAKY0VUV/68OiJND1jjQ8Fa3qutaVdSM9YfAF8L1s'
    'PijAplgB6INuHs62oF1/TBK5O6Oh81dhIjFVbGWm/7bAaR1Vq8zf/rpIZFrz2MLRrUIby0ifC/ysFHrp'
    'u5uZoJT+lbyHpws1W5XTghoPxNFQLiJ9D48hS62XdNUYIn1nanD9t8F3mnM0QppfKGJI7Wz9RZOVUUTD'
    'hWNuVSrCyTU83+etOayfBSmcxYbowJjwGuyHvKdcRRPmNcgQj4I3PzmPPniVIhGmQu6X3vCk5rBwHGkS'
    '7AIs8Jx+TkhKaSwth26f1hmfi1OvqZa4nQM5lWslX7gEE56PpcOS1glDIL7XABiQGOv8GRBlAiEXvu1/'
    'Ra1oxD5MgA9DeiCgf+JP0Hgp1GNKRVE7Ppsnd4rS6d4mSMtQC2kdnEltTocAkuLFrBKI2cAPsIcYuMO6'
    'RVHNqYB99AraDDoAohCVt6amDS0eYMd5LGHXondRKh7lzJBezbjhdIZnWI35mlQacFjWOdH+EFc6xIbO'
    'sVnz0QNi1uHpP9pWkr7WJ71FvpXT5kPqeYqOmPUnMROV6jjYPFgLQ7tEK1WET5b5Ee0RwOU6h54oUdf6'
    'By1TTg0tk5Zb55/3UQWu2Ur8OXx/HNSfvK8a0YbsBoVD/IlOCnQR8pUhYQspEmUR/PfZo0bnT1+b6/gn'
    '2hT/1eOfN+lB0ycpd/2VWOYCCMhmOchfnhvxz36C80ti3zTuzcQ5sF79Qd0='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
