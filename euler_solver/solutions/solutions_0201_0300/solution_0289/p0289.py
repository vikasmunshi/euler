#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 289: Eulerian Cycles.

Problem Statement:
    Let C(x, y) be a circle passing through the points (x, y), (x, y+1),
    (x+1, y) and (x+1, y+1).

    For positive integers m and n, let E(m, n) be a configuration which
    consists of the m * n circles:
    { C(x, y): 0 ≤ x < m, 0 ≤ y < n, x and y are integers }.

    An Eulerian cycle on E(m, n) is a closed path that passes through each
    arc exactly once. We consider only non-crossing Eulerian cycles: paths
    that may touch at lattice points but never cross.

    Let L(m, n) be the number of Eulerian non-crossing paths on E(m, n).
    For example, L(1,2) = 2, L(2,2) = 37 and L(3,3) = 104290.

    Find L(6,10) mod 10^10.

URL: https://projecteuler.net/problem=289
"""
from typing import Any

euler_problem: int = 289
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 1, 'n': 2, 'mod': 100}, 'answer': None},
    {'category': 'main', 'input': {'m': 6, 'n': 10, 'mod': 10000000000}, 'answer': None},
    {'category': 'extra', 'input': {'m': 3, 'n': 3, 'mod': 10000000000}, 'answer': None},
]
encrypted: str = (
    'nDIlQhjzsfkV/5jwG2UqJqmdvE0bp2ufswoE60sBGNuoZJ2AOezHJpsX+he5sNzGxPHVY113m2qkl7Lc'
    '3sNBdsL6fK4pI0BjFbOFtj+EWSHmyDlnTyoHt6Q9st0RDQxK9q67Abm/pALGRd2ZGhf9oko4JS8zjKHo'
    '2012Ge3YPrFU8ekITXbSBh/uSsZuNEm4uTyjM1jo5qUbc/fXfVmiCxVtSH2L3b8em6PSziR7CDFKvSjz'
    'BIknMzt8CNZu25VrqoCnlcGhlPusfRBfqzATV+5PWu5nCd2fp9k4QVYSlJVrFvk4qkERSMUPbT/6skjY'
    'IowyXKiZPQWmJPt3/ppWww/dCOJyXmpVdSa4NSfyZhAk0Ay49yST5sy0GeJFblvBysznPlSpKVo/WG0h'
    'cbCZMxOx4eH5H/aj5YN4SxcD9M95zz91cgdAsrvEMnTvaF3kvvg8aq2pAkE0+ihBMrtoicHKUQf7j9mN'
    'wh/Jm/0mxEvv7Df0O7+Hu/2J+Oe6XQuqMplW/w6V54Y53BT5o7PNwUA7zXvCbt7TSX2FRnyfFfpwQkBa'
    'SaekgJ+iKxuPBF0dYRUJgjcZXQXV6b7iK4nOMmw4aKgsMqDv9szcNuuHaMA6aoAOXVXDFP/wL0JucEHa'
    'UmJFHZ4FH2ro2RDE/XMeO5R6Fufp/6YpjwjQcDHXxkRDlGAO6rA1VY4QXRMjEr55+Nb1YVLLaJ57Stav'
    'vJVJbWi3QzzpFqaZgJLl9mzfF0ehIr9Oe2fTNRoCau2wXn1Eg6HYIuljVJBao4dy2MixTy4MxyiH+zpr'
    'Lt710cZ+PibH67Ghcj4PsdqYdYWXv3OQe0aBwJbRaNAWkczPxcd9jOiqH6uSpcwSIqeovhXD2aDeWyJi'
    'XW9thz3lBpWCv5+fIP3Jmduc7KpYCGXL3B9QFdPta208OKuY8XBK2RrODjxKIZMofcRQdfzqYQJiKyHU'
    'YPiBLRC1SXfq0lqXknl+Xystz/XeA9olkaAhidt+hmJhPMz4dRxz7y1kScId4Q+UzOIn4NqbWhsVw+rz'
    'OIP//BM5OUkyw4fxcaKbgptj8kNcXRf8y93YlHhyCOzqo32PUS2kA4N3YP33Yr3O9BYnAuI5nMkdR5vm'
    'TlJeKftbyshzEXmhbLONPhSLre7pzVNtUzYTgRO3rmhd6+D3AtxOWyWcRCeB7QF3TKkz+i849XCK7Nji'
    'yA4EweMPFEt/MTwNjMwvdJ3GzOytos2RBgDGsE0mXtRBP567Ff7/u2JxzwMotvXrrJk6FPcEciUmlLSi'
    'o1ub58HDHsuDPsCrooOy/X3FuFKmFViEcJnYg7rqgMyR016u/1vdbL1aVD4CuFaDSdHpLEaKs81pJzIF'
    'pYIPmzTI4oGJ6dhwLf+5/ctTQ7ozGQrFIFVd+4ENBbd+umEK/Yyx7qWCl4F+SowdZ48ExwsFU3GCcAfx'
    'tKDZjwgbem+W0Yj3jAT5QbZs3o1MURbFoI6NlOvaC+ns39yZpP8BcDemnOIGmDWX0FxJFc4EUxgxqHd/'
    'mzcWX6ZhfK/e6sfkNYd2xq+rZn9QUNf1WZ6yVl+E0UNopF1RlhGeR7DnyzoGRZI6mQor4ELDgTKuHd5t'
    '4KYLRYq4iH5g5/JbPbu7WjqTbLQXhEMV6jJNmCWzb79X4gzvZ6T6HPVeSnYd+8rG7RJbodIuAsnU/iOY'
    '5vPds9FuVegtKtK+YxDOBaRj0cBrYE6V4E+DJu6KQdvqQKsBcr8I0hXoiftJ3T9Gvdfp7XSA9izQ4AVa'
    'myPs/XGAJbWu8Eqmu2/4KSiyLf6yY7b0GX/c/Wy+gfi3+0S/tSUKbUbJD2Up1yO48PIJsItRNGRxDs4i'
    '29Db+JoiAIXpnGvwlspmvannEcIkYaS5WNSVHMoRudfY7luOteYreQxBwCQAaPz6nN3zEkkxRUpvw5oh'
    '7QC57h2pLdlRRSBhB8WObsIfHrOE+bHkTKsXSRZoFdpP3yylK0bnfElnuO7PM3eIeAye5G+JxFh+lCfl'
    'yWcg3n9+fVz4+yZltsqVFCfskGsCfYECVeVyPkKSsDayoTg1za3f4SltW0Q3LZfQ5N0G0E8sL8ppJzHy'
    'W65q5eK1uFo9+6DY92maOu0sRB+UseQ5580g5j0su04xQEquWPjY+FYipp4+7hTwDFhvXOMSv1Q15tKt'
    'jERyNNeSImV5BlqbgknlIaUxZLlvOTiyMWMAdASmACQcOhJqog9na7cYYuPVxmwPpfLOv/4ey0NzkLlJ'
    'lb/8DjZKIpJ7y4Fm7JLGHJ68o78SGd8QUF8gNh/zf0TXoTP58SYHTPiZC4ZQlUTf6VPqbLAw5eIoT+0x'
    '2O96bocQIXygXckYpbp++OY7vkGoBKXd6NHm+7PDKA0ctX+wotfNQTaw0Jh7IbO8rKMLCV0zG1M/E9o3'
    'W6O1m0xv+u9i6+M4rb0xuMxdj1f7sB4t2ceSC+4oSk3ocArJblDBaNtFuBOTCic/CxhTnJV63dANtfV0'
    'DpJolPSybbaUA9hHFoUQgLWJqoFhUBMLqudyoZDIsZR853jcIFnmUDd6fHqv9F5mIeu/zlterm6zE5g/'
    'D5KCQlVnbwMAB84oW3Rt23fBZYeqtMRYH4zCio35zxGwf7noIN+qDFeE5THjFa7UeBocfPXRTJU9RJ+k'
    'BYjhadLAWATAiLESgpyxnrWY8YBISvZrO3dwvrs9wbTfySRmPB9D82xmgMAyYR3by3pnlGLmmbso3G5J'
    'izArrQ8UO2OD7SRictvfnU2/THqH9pQqPncd4T6DS7QV5QKabPx88cMhzV5yX1FPanR0DdFDle8sH0Za'
    'Eg7B0yiCr1jG5k7V2iKfnm6p4I6/SIic+k1sqInFS4MbP+G0lOCstvOd3KHE6sCZ3eML7DvuNzI4fK4n'
    'gSVUu+KV6jZ4OM/L3DXWHEIOxggtf856DKIkJv+txiAWNf5/bvbGXSqttnxcsdQf9upzmTeteCaBg0qH'
    'oFpD6Od60aCzbSJZLGajBb8rTk8='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
