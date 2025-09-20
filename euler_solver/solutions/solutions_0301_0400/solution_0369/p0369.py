#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 369: Badugi.

Problem Statement:
    In a standard 52 card deck of playing cards, a set of 4 cards is a Badugi
    if it contains 4 cards with no pairs and no two cards of the same suit.

    Let f(n) be the number of ways to choose n cards with a 4 card subset that
    is a Badugi. For example, there are 2598960 ways to choose five cards from
    a standard 52 card deck, of which 514800 contain a 4 card subset that is a
    Badugi, so f(5) = 514800.

    Find the sum f(n) for 4 <= n <= 13.

URL: https://projecteuler.net/problem=369
"""
from typing import Any

euler_problem: int = 369
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    'TPBIH9QSGDd+z8KxPeLeHOFGwcmsVWPIxuOITCA2tWdhlV9f9fSQyzjk7kZ9lXH1ReJ7qBY78kO9ORlK'
    '85w4JzYBdQWX+Nxqnu52zO58KNRe4q2/WcafgxT7t86rUYkR3aXpOOweX7CJooMuO0f21MDyX+NEl7WH'
    'ZASUGIJNNkYnQiDSYRU0+tgiggYiNU5V6Z+FYgM6NQuyIZdsQHFtIaQBwdiDlZTBBTuRTOHvShe4GB1x'
    'pIxTn8Ho2YLgxI8112sHp1hw3MgnKWqnut55H9owKPZFW1GjHjD7a3H1RK2DNCubX83CUtMMhag/GD3X'
    'DMH/ZJ2C/rqBQpVOob+aErcpXi1VrarDlGZgGWLnBrztD25sGFCVZ8jU7a/rFO9QLbCyBmvImBsdi+WG'
    'De7sZR/WXrSzEMbp4eG4Fl/ugJmVdYpmfeH4r6JWTHTND7QiatUynv5roFFrCpfIJC+dLCnkdVXGoVSM'
    'YbB/lZs0vn8RXjVl7huRbvEJhA8o7k09FnxtndeDiylD7LUljHYZ4xsLrbznyKLJzOKgiMZH8VrCJAuU'
    'HtE/dN7XkmkRa/c1jYHOI4Uf96FDEeFPrxOYfwdytz1soSTJRXkCEA1esLPnkaNjxrkthWe9zupy08lY'
    '7lGWHRWtX2amC4aaLXsxD2jfUXAHXbuleXN++LARcw3dMLee+fQf+HdkuisS1KOLsro3YXIPqe8f+mKw'
    'Ot5qvs0PdjJNQFtYxVvc+o9xlFEDas6J6zD+xfRBlRsKF7PtK1ZgLMktcqQJxtPTCFcR2LCae+emHGRg'
    '5n87ILARhGypyF2pse5T+BB3/3EZbBbTpXh1PiSgGa9RllIdLA/gDgHqmk0APVjXbuTaMb9wUy8AhbhX'
    'ynOEhhKuJh/YaqN88JT5htR1D1RsZae4Grj+CpM+cwC3Tjix6+owd90vhKKrdUx/jk1XPDQoAAKWoxyY'
    'vIODkenXWUFt9BRjt8fnkD7ee+Qr+6dcU4ubZFhTmEtsjcPErw/Ry7rZZ5OwMjfLMsToNyf3hObdAL6U'
    'z8JmAgg6hmME8OlEGec/yod5JySWiGWPNf+4A3J8ZcVW9r4PQCvUVfQvwYKyut9ASWoLAoKxb9t5DV4/'
    'LYPXfwNw9qBOhRYVw6r35v4Xj21XmC+sMI12Frw8G3kEGYGZ7fikXiOZeMVZ/7j8v6XZS49cIaQMZL9X'
    'zm75CQqk+x5C6nqmebtDWfc45n4PPLwE6WF7HKC5MHd1DM2eddXh/wsqMgougrSqpxm/ULxR59btGI7s'
    'Me+WRDPMXkx2XUGQjAhX7pFeGpH0PM7k6MRn30Vs0SOEHwKHkIQWUlNH6Ye5GjB8lewQnBCfB/upJhsk'
    '0wod7q9q9u045NBrRIAxyKcaECpg5yccEaahhGjlh3TmjhOxFdCEZaqLLjXI/ZNAis0EaeenPPXNf+NY'
    'qFYZRmrEfgR9/y1tejGOL6JjK7HvYAibobBf9NrtQSrVFJk7xoahLrKrWflKvOs1JQkFaA+lBlTi5DDJ'
    'sRKetXNItLrOiAH8NDRWV2Q2KE2gr0Oc76hES0WjWvvO+eDtymmqFCiN8FJPit6MIxvLIEP933CyCL9k'
    '64Lg7X5jA7FX4kWbaofncKZ66H2Gsf/+nLaB3UZdlgg9NxuXM0dQ6N+S2i+pNArGGShHdiPS8EksZ8+W'
    'XAi+xyrpIaymlWVfgRoyJa14hHiLKtsKhSFoKtauNOPZzM1ctTcOgH6USUY2zSLUXQ0dVH4wsLCQqIg9'
    'VTLtaa7UklHktvbvSI1X+YNL8Ojc8Q4iZgeYEksv46MrD1WxwGuOWBCD4C1KE+OYJVnq95y7Cv/SLNDB'
    'bI3XOcTK2ynycKnHVtDgu9Adi0327tFcDibpXn4IYlsusRZIwsBBxNUNz04SJSEnWpVKe/6AxM7GAZkv'
    'sgxG999ggl1NulOhWhoBf4mLl34JAShA9D4I4c14trKm+tpRGpnAjUBvLPIjcWEWRqcHg/08QEhzLSrc'
    'nu4uivfDkCl6RbBxO9VTolFN722R4nwV2OxdeWl8X8/6pfSjSmTpgV3EW2Fug6UVBKk6Cr6QOlMopPRv'
    'itXl0jeHjibH9L4cndpJ3Z2BQFZ9RF+StMu1aQDACSpX692mi2IQ+5kAbp2CVVwRG/QOyCi0nAE2NyZ5'
    'QjBQ3JHNggRDRlqvm94aJ4qytE+mMewXXlamnNmO45nT7TTbRhzzGO3UEQVMbcF2gI9nNpX/jYyg6TZg'
    'R4fUhwhDtDWxv/c6ZrTunQR47HKwFQ3XpDIPKoO2vD64jr2k+oTukW9tRY54UkxHZLwjGnlf0o/eC+Ji'
    '6zpCiBf496/aIERVJuEfkqG7UH2dzNdlivTRMIq+WPFhRYbaCC76sl06nT3uRiBGMQhDHI5tdABXXYRm'
    'xVnM6mEMa5WFvXAo5EZ+OH7YZ/dobta8tuYAlQZz2+WdvzqWEEd13f6fnSKJYdXc0nAI6/6zBXbtzCNS'
    'oxFiaWtKhnvKvHSrACBD56RBqrdEK8vcoRgHQv/cUfVabuSKHCY8t1Kf4FV4zyKZ4BoXoyBlnp1vVihO'
    '5A3GcaqGeI7x0XmJnjWgGP4u/0AqJrHm6Old15szgljr1vXY4ubyKSqKRn2OiveHHED7CzodHjATY4+X'
    'tgd34RpkDT/gOyGAGJiHYhedV/gwSrpalX+cH4d/tmnE/vd+'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
