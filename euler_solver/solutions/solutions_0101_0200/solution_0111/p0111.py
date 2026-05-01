#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 111: Primes with Runs.

Problem Statement:
    Considering 4-digit primes containing repeated digits it is clear that they
    cannot all be the same: 1111 is divisible by 11, 2222 is divisible by 22,
    and so on. But there are nine 4-digit primes containing three ones:
    1117, 1151, 1171, 1181, 1511, 1811, 2111, 4111, 8111.

    We shall say that M(n, d) represents the maximum number of repeated digits
    for an n-digit prime where d is the repeated digit, N(n, d) represents the
    number of such primes, and S(n, d) represents the sum of these primes.

    So M(4, 1) = 3 is the maximum number of repeated digits for a 4-digit
    prime where one is the repeated digit, there are N(4, 1) = 9 such primes,
    and the sum of these primes is S(4, 1) = 22275. For d = 0 it is only
    possible to have M(4, 0) = 2, with N(4, 0) = 13 and S(4, 0) = 67061.

    The statement lists M(4,d), N(4,d) and S(4,d) for d = 0..9 and the sum of
    all S(4,d) is 273700.

    Find the sum of all S(10, d) for d = 0,1,...,9.

URL: https://projecteuler.net/problem=111
"""
from typing import Any

euler_problem: int = 111
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 10}, 'answer': None},
    {'category': 'extra', 'input': {'n': 11}, 'answer': None},
]
encrypted: str = (
    'XoI+0CdooMA9efJTv+FI1n5o7rQaPE2wFH0e0Z65zny8tcoNddbZr6DSb6CCoEVh4FwkGh1el7b/sgNu'
    'bp1ZZ6gDXCFVjixya3n5DMEo4l8or6ZLnMforKPijikNUG9nALACUrsg7Lnfl/jtswarR3bRvIGQrhmB'
    'IEf1KPVwQBHVY00p1fWJou1apFUYTM63459hM8OEYtJ1g4HlSJhVDPW/n/n6QIqGqxyuBgCIg81ovcx3'
    'VwF0u/BCl98oCdZdSF6BY8GgbRWrnGk3ZEUcD/CFwGYUa2djSSPciDqABVgrPNtCsXCsTFjcgVQoLL95'
    'gvq5juEuMn+0VHJgymqFe6J51/5RXPADreAJ7uM/CDIKFV/yIMAGDSRlmAPldwpXzKmyjc1keOuKWvO+'
    'e1RTJ9aF9GI6Equeg3IDgfj4o/bHrOygNbX5vOgZI//6ms1TyR/7gvTzYQ5VSuKHI/Vtz9BsWhZlY2yh'
    'C44akGarnG2Px7Nv9rXo+LoX9zUuNKDr/47SJKnIFXM1NcNqMxIQDedmf45wSQ4xHzhf/X+bf+2KL9ox'
    'hNMGpy8W2HLIJxUQ3TKZu68Gq+RodECeLPP4xDkmSH96UUCIBxbVXsse6FNfxv9Rn3zg0gGhQTLGImzk'
    'Z4dJv4oYxNUGc5LJtIDxnAn7k6dxqSDc8LwV+FF6/eIM00ovHtoawFM69rCPWpdLbouQItwsJ/c8ma11'
    'DyFZmmjThYMMj+Vt1q8YT9uVWd++3RM5Xk/MKFQW4MaLv9+QgUVCFSU+2HjKUoFrlAJDwAOCIt/bqWbW'
    'IkaaOKJzow0NDnlFQ3zbc7kOJLmc4eD0C+cYRoPqPWfQ3KklGRH0S1AgKNSh5r+QbzPWHtzVcFJGiEPj'
    'jIADHfJmKHvLlvrTMuUP3bk6OzyqIoKNsuzFiUl7OPvaOoCH597Co31zqrOqnB9hk1Ze8dHPR5tbwNZl'
    'XYA+qOXjwf5Fl17/873OEqAbnUa4RKdLif0640imHFxz88grZ7dEwsrO79+juLNh2ZCAn8s3/i8H9CUm'
    'B0diEEF0xhWS4WXyuQqHY3w8PZBTEFCCD1wxA7T8rf0hwGoG34OqBCVMi2U2CWaFxbBHz5OdwY9I4noc'
    '71cBfoVmd4BrZxQmQ9c8rsqfzySTib6JSD0mJAMXAxH5OHzwD1PHnTd0VLhSgDukXZzGhmBZ9h3TB7KB'
    '8kT+bNVr3iffYYd9OkdDy1lwYT8rbsACZTE8ay7CpWxubxBNYTnchqa9v0YuONEpqqRQiiuZmn8HC1Lo'
    'tb6qGJXIS8Q9hD3UqrhsKbuLs/JUmq7BDItjv4WPNvt3KHwa8Yzk9CHGKsvpcAiKxyXPwmPxR4zQQ00F'
    'qbHhn13ijUAdb24l/bbYXvA9jx+LlzBOKEEmDtWDi5GJIneFtKOUA3qvbHFBYp+GFI1hyaw/5A3zFyec'
    'cOCxbcUYbExtg9nHj9pfbS+Ptm6ftAfZxibbFeN8qXjMJ/ibqsb+f5bufHcXU9z5RL754zaW18jF9DHI'
    'Ydv6cNL/lI7lU+TzlVLWAhV6A5mtxS4oX9vVw9K5P7WC7420nHcThWlgu6KKy7Wzvy5NRAQBG9DRyoAK'
    '78Gc3w+KvvOsGYCDexY1648BWYyfSk0buRn2zIaxKIjMol3qAPPcwA73pSM45072n1+/3RtBL4BGekGB'
    'yIppgb0MFafsmncKfGQPju+GLTgY10GsFDa18b6PN7Xn0v2M8rBgxFBVG0F525GHO/cnvEydkLKYlE7m'
    'fVienHy1zNmsa+S0KekBZoqoRfP8zeTiAIkub7ey8UVO2nv/v3KyrEArL2UKKFInIGwi9oUS/nn1gk1d'
    '+A9Hwed9C0vjmg4NOCmyo+bF6r2Ip9I7R4o7a/qo/I7Quhzo3qpyVtpR9JLaQwtNUycYDMLcquHZWaBt'
    'yJGR1UG2dP6tmYmZk3QKkHh6PHaJdP4s2vGCe0U8D4LPhwm02jNxzvuLGVKF9xqIIu17nUHJL9b/M9xa'
    'XEVGUU+6ak1Gn8xj5KQ/7uv/IZ3WUPne3Ix5NhaqvHyKWI2mxViUKbIyHT3HlircstRxakRkm1yM+ou2'
    'mNVaLCWWMm64HrTvWz4A1Jw4fNkR+zeRMc4xKzsfwuZIZzO2jx+OsRSyET0xzBUqt1A+0Ht2Cy0n64qk'
    'UCZ1Uf2AQniJgoUAXujXzxi9yx07vKqvV2ckw7j2feBe2SYYC9madjdKhuQTKJb5/+xz2em3tCN7gfqA'
    'Rc04B+Jh8yqVPn7VL0KGra8YGeus/SMseMQBcF02MXZdlYEeSHqmj/EDTEUBMFQJHq2XeaTQnbHRASqy'
    'CFQa7W4oGkZmIvlWSEnqRnVyCztahgvU+uN79QjBBnOUYs6VBNPxuG0igR8Zea0EYb4ELGvA3zz8SvIs'
    'At70F/CUMhgsZNmFcBACjlla/EMTgRgEzCj1LzzjDcLqutXB7K6EOThHatRL8mrKqYjROMzhOfTVEZVS'
    'CcslSwLMy6G8AWsAhcI4o77fN1JNtDKwJJ3YquDzrK2Qpx76p8X+lWrkWYkuOfktVOqNsOcBoui2YlNB'
    '8knJ5KWtaxwz9nSWG9fNhpYS1w3YyO9LcGrlEJz5iKNj3M1mftpac8xjcIE0qVl4B4xEzlD55AiLXqNC'
    'YHBtHMRn4xbCEbEclJKTv6PqlrVAwN59nE2VHLpP2r5kf/LfS+wuxpQyERdHW6/2scMXSiBlOGfHwlzS'
    'ezuT+B7G/psQgg1AGtaZ2DrXZOu1ptWwA0lMKDJQrxD8wIfQDZl+sUAV+3tAwYIx8toaPpJTX1fb/3h9'
    'zPgomt81FmZk1Lq6rQgbG8UCKu9UM2xDm0f3jvoUdtc3LTqHuld0T2JTEFZLBI7teoWIRNTmwZSp7EYd'
    'vumGHOUL/OTBWzuhI2DTijN9zJ4YwlxNuHGrleGFHTQqhJLV7izF8KXI++l9EtI/w0oJA0Ahvn+rdMb4'
    'W/lXKHEMb+2pyrTjdqeUu/EGiVYF3Jz3kFiKm6tr3v9waTfbyHS0qwtvLmAuShYj1u1u/WX4HCI6Ei6W'
    'vcnowOo/UzTGTttiZ1ah8JlYaCP+mkxnL0tRLRjgV7/bb+OdZitVQ7kDDUjh/USXSeY+KNbdJI6sn63D'
    'TbUDW1hXx66I7iJwEtjxJQYTjy4s/viHvl7JRGL2/+mWT3Y5wXe1o26Vvhtfmo+tRvGoOF4aFOwIT5un'
    '4hknPK4juypCiPwfMOUs64Za/zuE6ihmVxAnmYQjH3jS0aoVRINxg/CHQh0JlFdaZTCjMxhy3K+zg3yU'
    'cBb4/wkvxPaZn7FIHHzdLYNYLvj0QB/G4S1fMTHIZitWct1zNYmdgNRN1Lqe1nteOwAGW6rVUQt2hoZD'
    'rz/Q7+IOHPQprWjB2wC2O8o+XbM+oLVwIHhAQPFr4Fx1q4qLf51gkGS9POcuDYvYkSNSDr23DlwcJCur'
    'QdlO5v1GdrgKlFlaRg0IoTvSyq+8zoyxiaznrOAMd6uY0FoBU8xP7y2w4tERM4xSmBFOZXkPmcQ8aUpv'
    'AKf9K2N92+q+er46V1O6mwKqMrwqmIEeww9vYdtdKTcxnlqdBzHNEzelFpoWLYt4Y3opGLlq2ddM0aQN'
    'xMqhdmeWz2ppDPVDqaSs3arHm9lhr17EuIKRVmrpq+wCyB+QWd5RjFKu73SLcuwH+g/78UDnM9iSKfhy'
    'k1T+JCn32xAC9G3xDIWvf1wMjsCDi7iQGwWe2QQZugsgbvrvYVLBuExV5zg4fefCrIkjWRLk3/IV0CEe'
    'q9bzrwUeLpSxlDcaIPpNQ6ktv6O79IkOhdruV8edVJptg70YycWFEaLuOAOOgq0BNdsM0qpXBtxa+muc'
    'BM1o2xIuLsAjlBlIsLnx6Ha96HC4hobSR3TpDwFH1iZqYCP74+7a3eA0PNmQy4mIYVZI0Y+7/OC8H72b'
    '26Rw4krmT2K/gGQ/wCO0izaieJIQ8FpPPOnl4scct0qPkuTJWzPFdmphmuMdpwJGRLvY9KO0gzap5bRE'
    '/kc3RCbs1sHLq7+/ECLNVUcIt+a877lWTjTcoULjZxaOmsrKhuUJVvmriJTuAydF2jkkaNUK5344wWzh'
    'cHhd6JJ9UEgYkpBBF7I9fk+p8M+0cyxtcj3M95TUS4VA/Er5/i9Lh3dCOtA/LscFQXuOsQeURbSC7unB'
    'n2rdEXpj9T/U7KqLVZSciSnzJr6u7ucOc2Twnk4bgI3OSUbfujwDPNpmcqE0EPiMNtSMr3Nt/Cn3kDZU'
    '5kMUbhIFB6hL1WrisqXnGnqgcRV1XUHT/j41igujtWe9pg574O45kMCoK0fxTMsuFV/DpT+Ts6HNRTe7'
    'f56zl/CZwZX7NHhoKnG8RVNAuiWgNVfclfKsFpspd8VImJ+vRDV7yAxA3xGfDn7oTCcalO/FwfVoYNVl'
    'Mwcmv3AU2dIPHf80cOyj2o3gfoL06iOgXshWuj+poHovCFFSBGJwR5dhf5FZ3GC8MAtzPbQviNGm6mvL'
    'AQUAzCzRCi8eMJnrHzLILDjdYM9BZD9UZK6ofou+4EwD7T5f623pnY0QAz7ePpCDgDYoyLGdgVh+4jX4'
    'FdPj/CZUVhTr+Sf9DjCDruRL/DfYvTtqbn3PDLhieuCQ/eO+1HAAiskIIGkQJP2fxBnpIU4BghZPCbjV'
    'OKun7UrofXtoPQHNyO/2A23BIZZvzpLzlNpEOtLkf6s+vT1G7uafs25pCIDQTNI3JJffMVClqGyn8pCV'
    'oMHSEv12mrAq8G3ykj+9dv6uj5l6p9dUQ+DIXxyUC6ViYBEon+WHYgaVgU6N61cNplj9tu3Tona7OmDX'
    'mMEGdxLJvfjsJf+Z+YSNP1F3HmYyVEFxOpHwP/xaOF9IE2ZlJ0ZXYO3SxEU8gLAzG9qlWl8YqQTa1jiu'
    'fH46J/KgLKkbY0Go6uLXR5uCH0uwuPoO3vtAv68Ao1gO4SlSG+AA6s6Npl3yoXymL+4wV2IGcQcvIvQm'
    'i7Zphv+bfzwy1Tbhn3jpW9HV1hYnxLtR7jW/1yiIUdhTL1Zw+iBNZJiN5FLAb1oRin42a6fRjDDQCcTW'
    'VzW+Kp/rgA/NNHLW2qBg4HoMXkYGPBR+aNd//uDGsJPMFKTWPHpJMacX9w7k0TfQDHt4QMxRvZPJZk5k'
    '9g4ZdWpLYLYP6Juw2pC2ZkXlpzFjM2uZ3pX28BY6RkY1hiSFioi9uAPDlzNkuIrWnGR2B722HFXu5OuD'
    '3Ljfj/sUsmDEfyGweGEEwrcXbDHS4fUyKmb9gVUE4ziblmCOEk5PN0Ya5ZqpwUlYIWb5e2/4AOQiWtsW'
    'NUfFrXNeM1BM97uO6ioztDWdmxyPLQ8p7FWgC930E1T1M7afrhv9Doa276MkbpsbDL4KTih10x4YP6qu'
    'kKSmxcMKRMF5b7fkpmi+CfViVFuVHdkoMO21InNLvZq6XrtQVD+TO9VHLLA5KyMDY3NfsSvFF9tE4ZnE'
    '+73rWvBNXRBGlIvJ763jdk65PJ/zUkx8DvghfiEWC9gtofcS70UfxlH2WYaShZnrb4mvvHfR/SvjjtDt'
    '3+kFzvPI5VuDWi/qnrpEMgaPlLXtYq8A/kfh1TRDNemsR6Yt08e/Aq4p8susP6n6E2JCgt2sKcfKaTci'
    'G060Wlx1wWk17jEQttqA8ea5isajDy0guSZK1yoSupK9EKvOBrKRiJ+JQE6qjPCqnkTCMe2rzmi1OSXL'
    '6AVqzh1L0jGGWHgdS9s4CtJu0Vsb+cXp7JyjavRFR2X4NtIzxtGIo0l6ga6sYFontoyPCFSjfreV19SJ'
    'eeTTu36t/plElIsz+J4hwp/5Smp8TXsIH5kw/gbPJel2EH19AwwX/h98sjQ/e0Bsn7trtQ+VZhLe175x'
    'C/OV+Hu0Hdow1MSjuJOVzYl2bnF0FPxOiPDrbjQM0wW9INLn7AAvWm7B7XE5NdvRMDqMRsVuZ2GlzfLY'
    '5MdqC09R/yyGqnIFD6Ar0rQEyG7KT9onrKtwOPgDQk38wLTvzV5S4TH4ufN7YSxlWDAEL8BBtOAxf6yr'
    '2git0uzmnc6ojEcn2EzjyAJRF7P+11mri2u/Dau1RUVkqRt01rOJZz2ISt1NDgrIA5rlW3r1s6y8VNoR'
    '/CdF0KfBMHdATp1dKi4PLQvDULkjm/xtjF8CviumnJZsPSsvZso/ImRvpnGCQ9YHY2iDD+o85WCbVVX+'
    '3rqrubcMTvrAupp/Tj3KI+QlkrnlYna+jbiIszNGmodN1mLHxUj9E6bUxw45QrWAhKSe4yD3vQB6tN71'
    '26pKD0RzA3MnKkSuetDt+IFPb6Ri+zEZnTqi9gmfs5EH0MDEl5eDueLZQgxYROoROiMLtIUbBJR1CLrV'
    '4fc9rkj3HjpVbRGEoqL455er4dCcFlHdM/nYVPnynuIRu4qFx0lZE4mlpaXORFgeU32tV3XTR9AgB6n9'
    'eR3Nym7Ptj2etBqJpd4e/WI87UvSvtHEQqjuFI/exhyt0xNRLUfwAiG3MZA631O/lrcb3p+RJTeAj2RY'
    'zaBDTVsYjgPcWbuAgyMVLo+iqBkmS6jJ8nvR4je1Pbm9blv17MT98WHzzU6QzKSHH29TkNuPRfyiJA4h'
    'AyKEFVNgByN6Zahs1n1oZJah/YP2UZpz5XAeXAvxC6vT5LcrHd69wZ46fu6dzAyV0ax4HXjtn+h+oFWT'
    '2JfdIIpM/2w26P5jl09oUOLSpsNYQANVyz1PMEghDzpRBNdI6DR1q7mSQmym2k6vcZ6j/CpKktOcrvoo'
    'wYSteAvvhBgb9Auwsp7tH5yH+Ed1UOCsXO1ZzSkiDyWGOj0MRXZU1IokUG5HC5lJ09VXFXAEMbLGO/QQ'
    'Afb4z717lOTLPmH5gfbeEbx8KnOY8RDHvOHOtztOKp0fno1e2/y2qJ3k97Ur0yg5EOqzic+AfH6VQR7q'
    '2W284moqFpnzciZ5uZyVh255tQXHQb5fx/KYgTD0XZXXCnWOSNwGKiyymbd1bLZ4U88WqEAEAZA='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
